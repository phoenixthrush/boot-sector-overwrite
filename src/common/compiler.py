"""
MBR Compiler - Cross-platform compilation utilities for MBR variants

This module provides functionality to compile assembly code to MBR binaries
and build C++ executables that write MBR data to disks.
"""

import os
import sys
import platform
import subprocess
from typing import Optional, List, Dict, Union, Tuple
from pathlib import Path
import shutil


class MBRCompiler:
    """Cross-platform MBR compilation utilities."""
    
    def __init__(self):
        """Initialize compiler and detect available tools."""
        self.platform = platform.system().lower()
        self.nasm_cmd = self._find_nasm()
        self.cpp_compiler = self._find_cpp_compiler()
        
    def _find_command(self, commands: List[str]) -> Optional[str]:
        """Find first available command from list."""
        for cmd in commands:
            if shutil.which(cmd):
                return cmd
        return None
    
    def _find_nasm(self) -> Optional[str]:
        """Find NASM assembler."""
        commands = ['nasm', 'nasm.exe', '/usr/bin/nasm']
        return self._find_command(commands)
    
    def _find_cpp_compiler(self) -> Optional[str]:
        """Find C++ compiler."""
        if self.platform == "windows":
            commands = ['g++', 'clang++', 'cl.exe']
        else:
            commands = ['g++', 'clang++']
        return self._find_command(commands)
    
    def compile_asm_to_binary(self, asm_file: Union[str, Path], 
                             output_file: Union[str, Path]) -> Tuple[bool, str]:
        """
        Compile assembly file to binary MBR data.
        
        Args:
            asm_file: Path to assembly source file
            output_file: Path for output binary
            
        Returns:
            Tuple[bool, str]: (success, error_message)
        """
        if not self.nasm_cmd:
            return False, "NASM assembler not found. Please install NASM."
        
        asm_path = Path(asm_file)
        output_path = Path(output_file)
        
        if not asm_path.exists():
            return False, f"Assembly file not found: {asm_path}"
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            cmd = [
                self.nasm_cmd,
                str(asm_path),
                '-f', 'bin',        # Output format
                '-o', str(output_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Verify output is exactly 512 bytes
                if output_path.exists():
                    size = output_path.stat().st_size
                    if size == 512:
                        return True, f"Successfully compiled {asm_path.name} to binary"
                    else:
                        return False, f"Output size is {size} bytes, expected 512 bytes"
                else:
                    return False, "Compilation succeeded but output file not found"
            else:
                return False, f"NASM failed: {result.stderr}"
                
        except Exception as e:
            return False, f"Compilation error: {str(e)}"
    
    def create_cpp_executable(self, variant_name: str, mbr_data: bytes, 
                             output_dir: Union[str, Path]) -> Tuple[bool, str]:
        """
        Create C++ executable that writes the MBR to disk.
        
        Args:
            variant_name: Name of the MBR variant
            mbr_data: The 512-byte MBR binary data
            output_dir: Directory for output executable
            
        Returns:
            Tuple[bool, str]: (success, error_message)
        """
        if not self.cpp_compiler:
            return False, "C++ compiler not found. Please install g++, clang++, or MSVC."
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Generate C++ source with embedded MBR data
            cpp_source = self._generate_cpp_source(variant_name, mbr_data)
            cpp_file = output_dir / f"{variant_name}.cpp"
            
            with open(cpp_file, 'w') as f:
                f.write(cpp_source)
            
            # Generate Windows manifest
            manifest_file = output_dir / f"{variant_name}.exe.manifest"
            manifest_content = self._generate_windows_manifest(variant_name)
            with open(manifest_file, 'w') as f:
                f.write(manifest_content)
            
            # Generate resource file
            rc_file = output_dir / f"{variant_name}.rc"
            rc_content = f'1 24 "{variant_name}.exe.manifest"\n'
            with open(rc_file, 'w') as f:
                f.write(rc_content)
            
            # Compile resource file (Windows only)
            obj_file = None
            if self.platform == "windows" and shutil.which("windres"):
                cmd_res = [
                    "windres", 
                    str(rc_file), 
                    str(output_dir / f"{variant_name}.o")
                ]
                result = subprocess.run(cmd_res, capture_output=True, text=True)
                if result.returncode == 0:
                    obj_file = output_dir / f"{variant_name}.o"
            
            # Compile C++ source
            exe_name = f"{variant_name}.exe" if self.platform == "windows" else variant_name
            exe_path = output_dir / exe_name
            
            cmd_cpp = [self.cpp_compiler]
            
            # Add optimization flags
            cmd_cpp.extend(['-O3', '-Os', '-s'])
            
            # Add object file if available (Windows with resources)
            if obj_file:
                cmd_cpp.extend([str(cpp_file), str(obj_file)])
            else:
                cmd_cpp.append(str(cpp_file))
            
            # Output file
            cmd_cpp.extend(['-o', str(exe_path)])
            
            # Platform-specific flags
            if self.platform == "windows" and "g++" in self.cpp_compiler:
                cmd_cpp.extend(['-static', '-static-libgcc', '-static-libstdc++'])
            
            result = subprocess.run(cmd_cpp, capture_output=True, text=True)
            
            # Cleanup temporary files
            if rc_file.exists():
                rc_file.unlink()
            if obj_file and obj_file.exists():
                obj_file.unlink()
            
            if result.returncode == 0:
                return True, f"Successfully created executable: {exe_path}"
            else:
                return False, f"C++ compilation failed: {result.stderr}"
                
        except Exception as e:
            return False, f"Error creating executable: {str(e)}"
    
    def _generate_cpp_source(self, variant_name: str, mbr_data: bytes) -> str:
        """Generate C++ source code with embedded MBR data."""
        mbr_hex = ', '.join(f'0x{byte:02X}' for byte in mbr_data)
        
        return f'''#include <iostream>
#include <vector>
#include <fstream>
#include <string>

#ifdef _WIN32
#include <windows.h>
#else
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/hdreg.h>
#endif

const unsigned char MasterBootRecord[512] = {{
    {mbr_hex}
}};

bool writeMBR(const std::string& target) {{
#ifdef _WIN32
    DWORD bytesWritten;
    std::wstring wideTarget(target.begin(), target.end());
    HANDLE hDevice = CreateFileW(
        wideTarget.c_str(),
        GENERIC_ALL,
        FILE_SHARE_READ | FILE_SHARE_WRITE,
        nullptr,
        OPEN_EXISTING,
        0,
        nullptr
    );
    
    if (hDevice == INVALID_HANDLE_VALUE) {{
        std::cerr << "Error: Cannot open device " << target << std::endl;
        return false;
    }}
    
    bool result = WriteFile(hDevice, MasterBootRecord, 512, &bytesWritten, nullptr);
    CloseHandle(hDevice);
    return result && bytesWritten == 512;
#else
    int fd = open(target.c_str(), O_WRONLY);
    if (fd < 0) {{
        std::cerr << "Error: Cannot open device " << target << std::endl;
        return false;
    }}
    
    ssize_t written = write(fd, MasterBootRecord, 512);
    close(fd);
    return written == 512;
#endif
}}

int main(int argc, char* argv[]) {{
    if (argc != 2) {{
        std::cout << "Usage: " << argv[0] << " <target_device>" << std::endl;
        std::cout << "Example: " << argv[0] << " \\\\.\\\\PhysicalDrive0" << std::endl;
        std::cout << "         " << argv[0] << " /dev/sda" << std::endl;
        return 1;
    }}
    
    std::string target = argv[1];
    std::cout << "MBR Variant: {variant_name}" << std::endl;
    std::cout << "Target: " << target << std::endl;
    
    std::cout << "\\n  WARNING: This will overwrite the Master Boot Record!" << std::endl;
    std::cout << "Type 'YES' to continue: ";
    
    std::string confirmation;
    std::getline(std::cin, confirmation);
    
    if (confirmation != "YES") {{
        std::cout << "Operation cancelled." << std::endl;
        return 0;
    }}
    
    if (writeMBR(target)) {{
        std::cout << " MBR written successfully!" << std::endl;
    }} else {{
        std::cout << " Failed to write MBR!" << std::endl;
        return 1;
    }}
    
    return 0;
}}
'''
    
    def _generate_windows_manifest(self, variant_name: str) -> str:
        """Generate Windows manifest for administrator privileges."""
        return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
    <assemblyIdentity version="1.0.0.0" processorArchitecture="X86" name="{variant_name}" type="win32"/>
    <description>MBR Tools - {variant_name} variant</description>
    <trustInfo xmlns="urn:schemas-microsoft-com:asm.v2">
        <security>
            <requestedPrivileges>
                <requestedExecutionLevel level="requireAdministrator" uiAccess="false"/>
            </requestedPrivileges>
        </security>
    </trustInfo>
</assembly>
'''
    
    def check_dependencies(self) -> Dict[str, bool]:
        """Check which required tools are available."""
        return {
            'nasm': self.nasm_cmd is not None,
            'cpp_compiler': self.cpp_compiler is not None,
            'windres': shutil.which('windres') is not None if self.platform == "windows" else True
        }
    
    def get_dependency_info(self) -> str:
        """Get human-readable dependency information."""
        deps = self.check_dependencies()
        info = []
        
        for dep, available in deps.items():
            status = "" if available else ""
            tool_name = dep.replace('_', ' ').title()
            info.append(f"{status} {tool_name}")
            
        if not all(deps.values()):
            info.append("\nMissing dependencies:")
            if not deps['nasm']:
                info.append("- NASM: Install from https://www.nasm.us/")
            if not deps['cpp_compiler']:
                info.append("- C++ Compiler: Install GCC/g++ or Clang")
            if self.platform == "windows" and not deps['windres']:
                info.append("- Windres: Install MinGW-w64")
                
        return '\n'.join(info)