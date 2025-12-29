#!/usr/bin/env python3
"""
MBR Tools Testing System

This script tests MBR variants safely using QEMU virtualization.
"""

import sys
import os
import argparse
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

try:
    from common.qemu_runner import QEMURunner
    from common.mbr_writer import MBRWriter
    from common.compiler import MBRCompiler
    from variants.custom_message.variant import CustomMessageVariant
    from variants.empty.variant import EmptyVariant
    from variants.memz.variant import MemzVariant
except ImportError as e:
    print(f" Import error: {e}")
    print("Please ensure you're running from the project root directory")
    sys.exit(1)


class MBRTester:
    """Testing system for MBR variants."""
    
    def __init__(self):
        self.qemu = QEMURunner()
        self.writer = MBRWriter()
        self.compiler = MBRCompiler()
        
        # Register all variants
        self.variants = {
            'custom_message': CustomMessageVariant(),
            'empty': EmptyVariant(),
            'memz': MemzVariant()
        }
    
    def check_qemu(self) -> bool:
        """Check if QEMU is available."""
        print(" Checking QEMU availability...")
        
        if not self.qemu.is_available():
            print(" QEMU not available!")
            print(self.qemu.get_dependency_info())
            return False
        
        print(" QEMU is available")
        return True
    
    def test_variant(self, variant_name: str, options: dict = None) -> bool:
        """Test a specific MBR variant in QEMU."""
        if variant_name not in self.variants:
            print(f" Unknown variant: {variant_name}")
            print(f"Available variants: {', '.join(self.variants.keys())}")
            return False
        
        if not self.check_qemu():
            return False
        
        variant = self.variants[variant_name]
        config = variant.get_config()
        
        # Load or build variant
        mbr_data = self._load_variant_binary(variant_name)
        if mbr_data is None:
            print(f" Failed to load {variant_name} binary")
            print(" Build variant first with: python build.py --build {variant_name}")
            return False
        
        # Use variant-specific test options
        test_options = options or config['test_options']
        
        print(f" Testing {config['display_name']} variant...")
        print(f" Description: {config['description']}")
        print(f"  Safety Level: {config['safety_level']}")
        
        return self.qemu.run_variant_test(variant_name, mbr_data, test_options)
    
    def test_all(self, options: dict = None) -> bool:
        """Test all MBR variants."""
        if not self.check_qemu():
            return False
        
        print(" Testing all MBR variants...")
        
        success_all = True
        for variant_name in self.variants:
            print(f"\n{'='*60}")
            if not self.test_variant(variant_name, options):
                success_all = False
        
        print(f"\n{'='*60}")
        if success_all:
            print(" All tests completed successfully!")
        else:
            print(" Some tests failed")
        
        return success_all
    
    def _load_variant_binary(self, variant_name: str) -> bytes:
        """Load MBR binary from disk or build it if needed."""
        binary_path = Path(f"dist/binaries/{variant_name}.bin")
        
        if binary_path.exists():
            try:
                with open(binary_path, 'rb') as f:
                    return f.read()
            except Exception as e:
                print(f" Error loading binary: {e}")
                return None
        else:
            # Try to build it
            print(f"🔨 Building {variant_name}...")
            if self._build_variant(variant_name):
                return self._load_variant_binary(variant_name)
            return None
    
    def _build_variant(self, variant_name: str) -> bool:
        """Build a variant."""
        variant = self.variants[variant_name]
        config = variant.get_config()
        
        asm_file = config['assembly_file']
        if not asm_file.exists():
            print(f" Assembly file not found: {asm_file}")
            return False
        
        # Create output directory
        dist_bin = Path("dist/binaries")
        dist_bin.mkdir(parents=True, exist_ok=True)
        
        # Compile assembly
        binary_file = dist_bin / f"{variant_name}.bin"
        success, msg = self.compiler.compile_asm_to_binary(asm_file, binary_file)
        
        if success:
            print(f" Built {variant_name}: {binary_file}")
        else:
            print(f" Build failed: {msg}")
        
        return success
    
    def create_test_images(self) -> bool:
        """Create test disk images for all variants."""
        if not self.check_qemu():
            return False
        
        print(" Creating test disk images...")
        
        variants_data = {}
        for variant_name in self.variants:
            mbr_data = self._load_variant_binary(variant_name)
            if mbr_data:
                variants_data[variant_name] = mbr_data
            else:
                print(f" Failed to load {variant_name}")
                return False
        
        return self.qemu.create_test_suite(variants_data)
    
    def list_variants(self):
        """List all available variants with test info."""
        print(" MBR Variants - Testing Information")
        print("=" * 60)
        
        for name, variant in self.variants.items():
            config = variant.get_config()
            test_opts = config['test_options']
            
            safety_emoji = {
                'safe': '',
                'destructive': '',
                'experimental': ''
            }.get(config['safety_level'], '❓')
            
            print(f"{safety_emoji} {name}")
            print(f"   📝 {config['display_name']}")
            print(f"     Timeout: {test_opts['timeout_seconds']}s")
            print(f"    Memory: {test_opts['memory_mb']}MB")
            print(f"    Snapshot: {'Yes' if test_opts['snapshot'] else 'No'}")
            print(f"    Isolated: {'Yes' if test_opts['isolated'] else 'No'}")
            print()


def main():
    parser = argparse.ArgumentParser(
        description="MBR Tools Testing System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --check-qemu           Check QEMU availability
  %(prog)s --list                 List variants with test info
  %(prog)s --test custom_message   Test specific variant
  %(prog)s --test-all             Test all variants
  %(prog)s --create-images        Create test disk images
        """
    )
    
    parser.add_argument('--check-qemu', action='store_true',
                    help='Check QEMU availability')
    parser.add_argument('--list', action='store_true',
                    help='List variants with testing information')
    parser.add_argument('--test', metavar='VARIANT',
                    help='Test specific variant')
    parser.add_argument('--test-all', action='store_true',
                    help='Test all variants')
    parser.add_argument('--create-images', action='store_true',
                    help='Create test disk images')
    parser.add_argument('--no-snapshot', action='store_true',
                    help='Disable snapshot mode for testing')
    parser.add_argument('--no-isolation', action='store_true',
                    help='Disable network isolation')
    parser.add_argument('--timeout', type=int, metavar='SECONDS',
                    help='Override test timeout')
    
    args = parser.parse_args()
    
    if not any([args.check_qemu, args.list, args.test, args.test_all, args.create_images]):
        parser.print_help()
        return
    
    tester = MBRTester()
    
    if args.check_qemu:
        tester.check_qemu()
        return
    
    if args.list:
        tester.list_variants()
        return
    
    # Prepare test options
    test_options = {}
    if args.no_snapshot:
        test_options['snapshot'] = False
    if args.no_isolation:
        test_options['isolated'] = False
    if args.timeout:
        test_options['timeout_seconds'] = args.timeout
    
    if args.test:
        tester.test_variant(args.test, test_options)
        return
    
    if args.test_all:
        tester.test_all(test_options)
        return
    
    if args.create_images:
        tester.create_test_images()
        return


if __name__ == "__main__":
    main()