#!/usr/bin/env python3
"""Simple MBR builder."""

import sys
import os
import subprocess
from pathlib import Path


def find_cmd(cmd):
    return os.system(f"which {cmd} > /dev/null 2>&1") == 0


def compile_asm(asm_file, output_file):
    nasm = find_cmd('nasm')
    if not nasm:
        print("NASM not found")
        return False
    
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    cmd = ['nasm', asm_file, '-f', 'bin', '-o', output_file]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        size = output_file.stat().st_size
        print(f"Built {output_file.name} ({size} bytes)")
        return size == 512
    else:
        print(f"Build failed: {result.stderr}")
        return False


def build_variant(name):
    print(f"Building {name}...")
    
    asm_file = f"src/{name}/boot.asm"
    if not Path(asm_file).exists():
        print(f"Error: {asm_file} not found")
        return False
    
    bin_dir = Path("dist")
    bin_dir.mkdir(exist_ok=True)
    bin_file = bin_dir / f"{name}.bin"
    
    if compile_asm(asm_file, bin_file):
        print(f"Created {name}.bin")
        return True
    
    return False


def build_all():
    variants = ["custom_message", "empty", "memz"]
    success = True
    
    for variant in variants:
        if not build_variant(variant):
            success = False
    
    if success:
        print("All variants built successfully")
    else:
        print("Some variants failed")
    
    return success


def main():
    if len(sys.argv) < 2:
        print("Usage: python build.py <variant>|all")
        print("Examples:")
        print("  python build.py custom_message")
        print("  python build.py all")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "all":
        build_all()
    else:
        build_variant(cmd)


if __name__ == "__main__":
    main()