"""
QEMU Runner - Safe testing of MBR variants using QEMU

This module provides functionality to test MBR code safely in virtual machines
using QEMU for isolated testing without risking real hardware.
"""

import os
import sys
import platform
import subprocess
import tempfile
import time
from typing import Optional, List, Dict, Union, Tuple
from pathlib import Path
import shutil


class QEMURunner:
    """QEMU-based MBR testing utilities."""
    
    def __init__(self):
        """Initialize QEMU runner and detect QEMU installation."""
        self.platform = platform.system().lower()
        self.qemu_cmd = self._find_qemu()
        self.qemu_img_cmd = self._find_qemu_img()
        
    def _find_qemu(self) -> Optional[str]:
        """Find QEMU system emulator."""
        commands = []
        
        if self.platform == "windows":
            commands.extend([
                'qemu-system-i386.exe',
                'qemu-system-x86_64.exe',
                r'C:\Program Files\qemu\qemu-system-i386.exe',
                r'C:\Program Files\qemu\qemu-system-x86_64.exe'
            ])
        else:
            commands.extend([
                'qemu-system-i386',
                'qemu-system-x86_64',
                '/usr/bin/qemu-system-i386',
                '/usr/local/bin/qemu-system-i386'
            ])
            
        for cmd in commands:
            if shutil.which(cmd) or os.path.exists(cmd):
                return cmd
        return None
    
    def _find_qemu_img(self) -> Optional[str]:
        """Find QEMU image utility."""
        commands = []
        
        if self.platform == "windows":
            commands.extend([
                'qemu-img.exe',
                r'C:\Program Files\qemu\qemu-img.exe'
            ])
        else:
            commands.extend([
                'qemu-img',
                '/usr/bin/qemu-img',
                '/usr/local/bin/qemu-img'
            ])
            
        for cmd in commands:
            if shutil.which(cmd) or os.path.exists(cmd):
                return cmd
        return None
    
    def is_available(self) -> bool:
        """Check if QEMU is available."""
        return self.qemu_cmd is not None and self.qemu_img_cmd is not None
    
    def get_dependency_info(self) -> str:
        """Get QEMU dependency information."""
        info = []
        qemu_status = "✅" if self.qemu_cmd else "❌"
        qemu_img_status = "✅" if self.qemu_img_cmd else "❌"
        
        info.append(f"{qemu_status} QEMU System Emulator")
        info.append(f"{qemu_img_status} QEMU Image Utility")
        
        if not self.is_available():
            info.append("\nQEMU Installation:")
            if self.platform == "windows":
                info.append("- Download from: https://qemu.weilnetz.de/w64/")
                info.append("- Extract and add to PATH")
            elif self.platform == "darwin":  # macOS
                info.append("- Install: brew install qemu")
            else:  # Linux
                info.append("- Ubuntu/Debian: sudo apt install qemu-system-x86")
                info.append("- RHEL/CentOS: sudo yum install qemu-kvm")
                info.append("- Arch Linux: sudo pacman -S qemu")
                
        return '\n'.join(info)
    
    def create_disk_image(self, image_path: Union[str, Path], 
                         size_mb: int = 10) -> Tuple[bool, str]:
        """
        Create a QEMU disk image.
        
        Args:
            image_path: Path for the new disk image
            size_mb: Size in megabytes
            
        Returns:
            Tuple[bool, str]: (success, error_message)
        """
        if not self.qemu_img_cmd:
            return False, "qemu-img not found. Please install QEMU."
        
        image_path = Path(image_path)
        image_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            cmd = [
                self.qemu_img_cmd,
                'create',
                '-f', 'raw',
                str(image_path),
                f'{size_mb}M'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return True, f"Created {size_mb}MB disk image: {image_path}"
            else:
                return False, f"Failed to create disk image: {result.stderr}"
                
        except Exception as e:
            return False, f"Error creating disk image: {str(e)}"
    
    def test_mbr_in_qemu(self, mbr_data: bytes, variant_name: str,
                         snapshot: bool = True, isolated: bool = True,
                         memory_mb: int = 128, timeout_seconds: int = 30) -> Tuple[bool, str]:
        """
        Test MBR code in QEMU virtual machine.
        
        Args:
            mbr_data: 512-byte MBR data
            variant_name: Name of the variant (for temporary files)
            snapshot: Use snapshot mode (non-destructive)
            isolated: Disable network and other isolation features
            memory_mb: VM memory in megabytes
            timeout_seconds: Auto-shutdown after this time
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        if not self.is_available():
            return False, "QEMU not available"
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            image_path = temp_path / f"{variant_name}_test.img"
            
            # Create disk image
            success, msg = self.create_disk_image(image_path)
            if not success:
                return False, f"Failed to create disk image: {msg}"
            
            # Write MBR to image
            success, msg = self.write_mbr_to_image(mbr_data, image_path)
            if not success:
                return False, f"Failed to write MBR: {msg}"
            
            # Prepare QEMU command
            cmd = [self.qemu_cmd]
            cmd.extend(['-hda', str(image_path)])
            cmd.extend(['-m', f'{memory_mb}M'])
            
            if snapshot:
                cmd.append('-snapshot')
            
            if isolated:
                cmd.extend(['-net', 'none'])
            
            # Display settings
            cmd.extend(['-vga', 'std'])
            cmd.extend(['-name', f'MBR Test - {variant_name}'])
            
            try:
                print(f"🚀 Starting QEMU to test {variant_name} MBR...")
                print(f"📁 Disk image: {image_path}")
                print(f"🔒 Snapshot mode: {'Enabled' if snapshot else 'Disabled'}")
                print(f"🌐 Network: {'Disabled' if isolated else 'Enabled'}")
                print(f"💾 Memory: {memory_mb}MB")
                
                if timeout_seconds > 0:
                    print(f"⏱️ Auto-shutdown in {timeout_seconds} seconds")
                
                print("\n💡 Close the QEMU window to stop the test")
                print("⚠️ The MBR code will run in the isolated VM environment\n")
                
                if timeout_seconds > 0:
                    # Run with timeout
                    try:
                        subprocess.run(cmd, timeout=timeout_seconds)
                        return True, f"QEMU test completed successfully"
                    except subprocess.TimeoutExpired:
                        return True, f"QEMU test completed (timeout after {timeout_seconds}s"
                else:
                    # Run without timeout
                    subprocess.run(cmd)
                    return True, f"QEMU test completed"
                    
            except FileNotFoundError:
                return False, f"QEMU executable not found: {self.qemu_cmd}"
            except Exception as e:
                return False, f"Error running QEMU: {str(e)}"
    
    def write_mbr_to_image(self, mbr_data: bytes, image_path: Union[str, Path]) -> Tuple[bool, str]:
        """
        Write MBR data to disk image.
        
        Args:
            mbr_data: 512-byte MBR data
            image_path: Path to disk image
            
        Returns:
            Tuple[bool, str]: (success, error_message)
        """
        if len(mbr_data) != 512:
            return False, f"MBR data must be exactly 512 bytes (got {len(mbr_data)})"
        
        image_path = Path(image_path)
        if not image_path.exists():
            return False, f"Disk image not found: {image_path}"
        
        try:
            # Write MBR to first sector
            with open(image_path, 'r+b') as f:
                f.write(mbr_data)
            
            return True, f"MBR written to {image_path}"
            
        except Exception as e:
            return False, f"Error writing MBR to image: {str(e)}"
    
    def run_variant_test(self, variant_name: str, mbr_data: bytes, 
                         options: Optional[Dict] = None) -> bool:
        """
        Run comprehensive test for a specific variant.
        
        Args:
            variant_name: Name of the variant
            mbr_data: MBR binary data
            options: Testing options dictionary
            
        Returns:
            bool: True if test succeeded
        """
        if options is None:
            options = {
                'snapshot': True,
                'isolated': True,
                'memory_mb': 128,
                'timeout_seconds': 30
            }
        
        print(f"🧪 Testing MBR variant: {variant_name}")
        print("=" * 50)
        
        # Validate MBR data
        if len(mbr_data) != 512:
            print(f"❌ Invalid MBR size: {len(mbr_data)} bytes (expected 512)")
            return False
        
        # Check boot signature
        if mbr_data[510:512] != b'\x55\xAA':
            print("⚠️ Warning: Missing boot signature 0x55AA")
        else:
            print("✅ Boot signature present")
        
        # Run QEMU test
        success, msg = self.test_mbr_in_qemu(
            mbr_data, 
            variant_name, 
            **options
        )
        
        if success:
            print(f"✅ {variant_name} test completed successfully")
        else:
            print(f"❌ {variant_name} test failed: {msg}")
        
        return success