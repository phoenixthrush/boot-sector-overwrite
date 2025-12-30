#!/usr/bin/env python3
"""Simple MBR tester."""

import sys
import os
import subprocess
import tempfile
from pathlib import Path


def find_qemu():
    for cmd in ['qemu-system-i386', 'qemu-system-x86_64']:
        if os.system(f"which {cmd} > /dev/null 2>&1") == 0:
            return cmd
    return None


def create_disk_image(path, size_mb=10):
    qemu_img = find_qemu()
    if not qemu_img:
        qemu_img = 'qemu-img'
    
    path.parent.mkdir(parents=True, exist_ok=True)
    
    cmd = [qemu_img, 'create', '-f', 'raw', str(path), f'{size_mb}M']
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"Created {path.name} ({size_mb}MB)")
        return True
    else:
        print(f"Failed to create image: {result.stderr}")
        return False


def write_mbr_to_image(mbr_data, image_path):
    if len(mbr_data) != 512:
        print("Error: MBR data must be 512 bytes")
        return False
    
    with open(image_path, 'r+b') as f:
        f.write(mbr_data)
    
    print(f"MBR written to {image_path.name}")
    return True


def test_variant_in_qemu(mbr_data, name, timeout=30):
    qemu = find_qemu()
    if not qemu:
        print("QEMU not found")
        return False
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        image_path = temp_path / f"{name}_test.img"
        
        if not create_disk_image(image_path):
            return False
        
        if not write_mbr_to_image(mbr_data, image_path):
            return False
        
        print(f"Testing {name} (timeout: {timeout}s)...")
        print("Close QEMU window to stop test")
        
        cmd = [qemu, '-hda', str(image_path), '-snapshot', '-net', 'none']
        try:
            subprocess.run(cmd, timeout=timeout)
            print("Test completed")
            return True
        except subprocess.TimeoutExpired:
            print("Test completed (timeout)")
            return True
        except Exception as e:
            print(f"Test failed: {e}")
            return False


def load_mbr_binary(name):
    bin_file = Path(f"dist/{name}.bin")
    if not bin_file.exists():
        print(f"Error: {bin_file} not found. Build first.")
        return None
    
    with open(bin_file, 'rb') as f:
        return f.read()


def test_variant(name, timeout=30):
    mbr_data = load_mbr_binary(name)
    if mbr_data is None:
        return False
    
    return test_variant_in_qemu(mbr_data, name, timeout)


def test_all(timeout=30):
    variants = ["custom_message", "empty", "memz"]
    success = True
    
    for variant in variants:
        if not test_variant(variant, timeout):
            success = False
    
    if success:
        print("All tests completed successfully")
    else:
        print("Some tests failed")
    
    return success


def main():
    if len(sys.argv) < 2:
        print("Usage: python test.py <variant>|all [--timeout N]")
        print("Examples:")
        print("  python test.py custom_message")
        print("  python test.py all")
        print("  python test.py all --timeout 60")
        return
    
    cmd = sys.argv[1]
    timeout = 30
    
    if "--timeout" in sys.argv:
        idx = sys.argv.index("--timeout")
        if idx + 1 < len(sys.argv):
            try:
                timeout = int(sys.argv[idx + 1])
            except ValueError:
                print("Invalid timeout value")
                return
    
    if cmd == "all":
        test_all(timeout)
    else:
        test_variant(cmd, timeout)


if __name__ == "__main__":
    main()
