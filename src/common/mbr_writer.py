"""
MBR Writer - Common functionality for writing Master Boot Records

This module provides safe cross-platform functionality for writing MBR data
to disk images and physical drives with proper safety checks.
"""

import os
import sys
import platform
import subprocess
from typing import Optional, List, Union
from pathlib import Path


class MBRWriter:
    """Safe MBR writing functionality with cross-platform support."""
    
    DANGEROUS_OPERATIONS = {
        'PhysicalDrive0', 'PhysicalDrive1', 'PhysicalDrive2', 'PhysicalDrive3'
    }
    
    def __init__(self, safety_level: str = "high"):
        """
        Initialize MBR Writer with safety settings.
        
        Args:
            safety_level: 'high', 'medium', or 'low' - affects warnings and confirmations
        """
        self.safety_level = safety_level
        self.platform = platform.system().lower()
        
    def _display_safety_warning(self, target: str) -> bool:
        """
        Display safety warning and get user confirmation.
        
        Args:
            target: The target device/file being written to
            
        Returns:
            bool: True if user confirms, False otherwise
        """
        print("\n" + "="*60)
        print("  DANGER WARNING - MASTER BOOT RECORD OPERATION ")
        print("="*60)
        print(f"You are about to write to: {target}")
        
        if self._is_physical_drive(target):
            print(" THIS IS A PHYSICAL DRIVE OPERATION ")
            print("This will overwrite the MBR and may make the drive UNBOOTABLE!")
            print("All data on this drive could be PERMANENTLY LOST!")
        else:
            print("This will overwrite the Master Boot Record.")
            
        print("\nEnsure you have:")
        print(" Backed up all important data")
        print(" Understood the consequences")
        print(" Selected the correct target")
        
        if self.safety_level == "high":
            print("\nType 'I UNDERSTAND THE RISKS' to continue:")
            confirmation = input("> ").strip()
            return confirmation == "I UNDERSTAND THE RISKS"
        elif self.safety_level == "medium":
            print("\nType 'yes' to continue:")
            confirmation = input("> ").strip().lower()
            return confirmation == "yes"
        else:
            print("\nContinue? [y/N]")
            confirmation = input("> ").strip().lower()
            return confirmation.startswith('y')
    
    def _is_physical_drive(self, target: str) -> bool:
        """Check if target is a physical drive."""
        dangerous_patterns = [
            'PhysicalDrive',  # Windows
            '/dev/sd',         # Linux
            '/dev/hd',         # Linux
            '/dev/nvme',       # Linux
            'disk',            # macOS
            'rdisk',           # macOS
        ]
        
        return any(pattern in target for pattern in dangerous_patterns)
    
    def write_mbr_to_file(self, mbr_data: bytes, target_file: Union[str, Path], 
                         force: bool = False) -> bool:
        """
        Write MBR data to a file or disk image.
        
        Args:
            mbr_data: The 512-byte MBR data to write
            target_file: Target file path
            force: Skip safety warnings if True
            
        Returns:
            bool: True if successful, False otherwise
        """
        target = str(target_file)
        
        if len(mbr_data) != 512:
            print(f" Error: MBR data must be exactly 512 bytes (got {len(mbr_data)})")
            return False
            
        if not force and self.safety_level != "none":
            if not self._display_safety_warning(target):
                print(" Operation cancelled by user")
                return False
        
        try:
            # Ensure target directory exists
            Path(target).parent.mkdir(parents=True, exist_ok=True)
            
            with open(target, 'wb') as f:
                f.write(mbr_data)
            print(f" Successfully wrote MBR to {target}")
            return True
            
        except Exception as e:
            print(f" Error writing MBR to {target}: {e}")
            return False