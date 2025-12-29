#!/usr/bin/env python3
"""
MBR Tools Build System

This script builds MBR variants and creates distributable packages.
It provides a clean Python-based build system replacing batch files.
"""

import sys
import os
import argparse
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

try:
    from common.compiler import MBRCompiler
    from common.mbr_writer import MBRWriter
    from common.qemu_runner import QEMURunner
    from variants.custom_message.variant import CustomMessageVariant
    from variants.empty.variant import EmptyVariant
    from variants.memz.variant import MemzVariant
except ImportError as e:
    print(f" Import error: {e}")
    print("Please ensure you're running from the project root directory")
    sys.exit(1)


class MBRBuilder:
    """Main build system for MBR variants."""
    
    def __init__(self):
        self.compiler = MBRCompiler()
        self.writer = MBRWriter()
        self.qemu = QEMURunner()
        
        # Register all variants
        self.variants = {
            'custom_message': CustomMessageVariant(),
            'empty': EmptyVariant(),
            'memz': MemzVariant()
        }
    
    def check_dependencies(self):
        """Check if all required tools are available."""
        print(" Checking dependencies...")
        
        compiler_deps = self.compiler.check_dependencies()
        print("Build Tools:")
        for tool, available in compiler_deps.items():
            status = "" if available else ""
            print(f"  {status} {tool}")
        
        print("\nTesting Tools:")
        qemu_available = self.qemu.is_available()
        print(f"  {'' if qemu_available else ''} QEMU")
        
        if not all(compiler_deps.values()):
            print("\n Missing build dependencies!")
            print(self.compiler.get_dependency_info())
            return False
        
        if not qemu_available:
            print("\n  QEMU not available - testing disabled")
            print(self.qemu.get_dependency_info())
        
        return True
    
    def build_variant(self, variant_name: str) -> bool:
        """Build a specific MBR variant."""
        if variant_name not in self.variants:
            print(f" Unknown variant: {variant_name}")
            print(f"Available variants: {', '.join(self.variants.keys())}")
            return False
        
        variant = self.variants[variant_name]
        config = variant.get_config()
        
        print(f" Building {config['display_name']} variant...")
        
        # Display variant info
        print(f" Description: {config['description']}")
        print(f"  Safety Level: {config['safety_level']}")
        print(variant.get_safety_warning())
        
        # Get assembly file
        asm_file = config['assembly_file']
        if not asm_file.exists():
            print(f" Assembly file not found: {asm_file}")
            return False
        
        # Create output directories
        dist_bin = Path("dist/binaries")
        dist_exe = Path("dist/executables")
        dist_bin.mkdir(parents=True, exist_ok=True)
        dist_exe.mkdir(parents=True, exist_ok=True)
        
        # Compile assembly to binary
        binary_file = dist_bin / f"{variant_name}.bin"
        success, msg = self.compiler.compile_asm_to_binary(asm_file, binary_file)
        if not success:
            print(f" Assembly compilation failed: {msg}")
            return False
        
        print(f" Assembly compiled: {binary_file}")
        
        # Read binary data
        try:
            with open(binary_file, 'rb') as f:
                mbr_data = f.read()
        except Exception as e:
            print(f" Failed to read binary: {e}")
            return False
        
        # Create C++ executable
        success, msg = self.compiler.create_cpp_executable(
            variant_name, mbr_data, dist_exe
        )
        if not success:
            print(f" Executable creation failed: {msg}")
            return False
        
        print(f" Executable created: {dist_exe}/{variant_name}")
        
        return True
    
    def build_all(self) -> bool:
        """Build all variants."""
        print("  Building all MBR variants...")
        
        success_all = True
        for variant_name in self.variants:
            if not self.build_variant(variant_name):
                success_all = False
        
        if success_all:
            print("\n All variants built successfully!")
        else:
            print("\n Some variants failed to build")
        
        return success_all
    
    def list_variants(self):
        """List all available variants."""
        print(" Available MBR Variants:")
        print("=" * 60)
        
        for name, variant in self.variants.items():
            config = variant.get_config()
            safety_emoji = {
                'safe': '',
                'destructive': '',
                'experimental': ''
            }.get(config['safety_level'], '❓')
            
            print(f"{safety_emoji} {name}")
            print(f"    {config['display_name']}")
            print(f"    {config['description']}")
            print(f"    Safety: {config['safety_level']}")
            print(f"     Category: {config['category']}")
            print(f"     Features: {', '.join(config['features'])}")
            print()


def main():
    parser = argparse.ArgumentParser(
        description="MBR Tools Build System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --check                    Check dependencies
  %(prog)s --list                     List all variants
  %(prog)s --build custom_message      Build specific variant
  %(prog)s --build-all                Build all variants
  %(prog)s --build-all --test         Build and test all variants
        """
    )
    
    parser.add_argument('--check', action='store_true',
                    help='Check build dependencies')
    parser.add_argument('--list', action='store_true',
                    help='List available variants')
    parser.add_argument('--build', metavar='VARIANT',
                    help='Build specific variant')
    parser.add_argument('--build-all', action='store_true',
                    help='Build all variants')
    parser.add_argument('--test', action='store_true',
                    help='Test variants after building (requires QEMU)')
    
    args = parser.parse_args()
    
    if not any([args.check, args.list, args.build, args.build_all]):
        parser.print_help()
        return
    
    builder = MBRBuilder()
    
    if args.check:
        builder.check_dependencies()
        return
    
    if args.list:
        builder.list_variants()
        return
    
    if args.build:
        success = builder.build_variant(args.build)
        if success and args.test:
            print(f"\n Testing {args.build} variant...")
            # Import test functionality
            from src.tools.test import MBRTester
            tester = MBRTester()
            tester.test_variant(args.build)
        return
    
    if args.build_all:
        success = builder.build_all()
        if success and args.test:
            print("\n Testing all variants...")
            from src.tools.test import MBRTester
            tester = MBRTester()
            tester.test_all()
        return


if __name__ == "__main__":
    main()