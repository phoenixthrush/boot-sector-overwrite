# MBR Tools 

A comprehensive Python-based build and testing system for Master Boot Record (MBR) variants with QEMU integration for safe testing.

##  IMPORTANT SAFETY WARNING

**This software writes to disk boot sectors. Misuse can result in:**
- Permanent data loss
- Unbootable systems
- Hardware damage in extreme cases

**ALWAYS test with QEMU first!**
- Never use on production systems
- Backup all important data
- Use virtual machines or spare hardware
- Understand exactly what each variant does

##  Features

- ** Python-based build system** - No more batch files
- ** QEMU testing integration** - Safe, isolated testing
- ** Safety mechanisms** - Multiple layers of protection
- ** Cross-platform** - Windows, Linux, macOS support
- ** Modular design** - Easy to add new variants
- ** Fast compilation** - Uses system compilers

##  Project Structure

```
mbr-tools/
├── src/
│   ├── common/              # Shared utilities
│   │   ├── mbr_writer.py   # MBR writing functionality
│   │   ├── compiler.py     # Cross-platform compilation
│   │   └── qemu_runner.py  # QEMU testing
│   ├── variants/           # MBR variants
│   │   ├── custom_message/ # Friendly message variant
│   │   ├── empty/         # Empty MBR (destructive)
│   │   └── memz/          # MEMZ-style effects
│   └── tools/             # Build tools
├── dist/                  # Build outputs
├── docs/                  # Documentation
├── tests/                 # Test suite
├── build.py              # Main build script
├── test.py               # Main test script
└── requirements.txt      # Python dependencies
```

## Quick Start Quick Start

### Prerequisites

1. **Python 3.7+** - Build system
2. **NASM** - Assembly compiler
   - Windows: https://www.nasm.us/
   - Linux: `sudo apt install nasm`
   - macOS: `brew install nasm`
3. **C++ Compiler** - For executables
   - Windows: MinGW-w64 or MSVC
   - Linux: `sudo apt install g++`
   - macOS: `brew install gcc`
4. **QEMU** - For testing (recommended)
   - Windows: https://qemu.weilnetz.de/w64/
   - Linux: `sudo apt install qemu-system-x86`
   - macOS: `brew install qemu`

### Basic Usage

```bash
# Check dependencies
python build.py --check

# List available variants
python build.py --list

# Build specific variant
python build.py --build custom_message

# Build all variants
python build.py --build-all

# Test with QEMU (safe)
python test.py --test custom_message

# Test all variants
python test.py --test-all
```

##  Available Variants

###  Custom Message (Safe)
- **Description**: Displays a friendly knock-knock joke with colors
- **Safety**: Safe - only displays text
- **Features**: Text display, color support, screen clearing
- **Use**: Safe testing, demonstration

###  Empty MBR (Destructive)
- **Description**: Minimal MBR with only boot signature
- **Safety**: Destructive - wipes boot sector
- **Features**: Infinite loop, boot sector wipe
- **Use**: Emergency wipe, testing recovery

###  MEMZ Style (Experimental)
- **Description**: Harmless MEMZ-inspired visual effects
- **Safety**: Experimental - visual effects only
- **Features**: Graphics, animations, colorful effects
- **Use**: Visual testing, demonstration

##  Testing with QEMU

QEMU provides completely isolated testing without risking real hardware:

```bash
# Test specific variant
python test.py --test memz

# Test all variants with custom timeout
python test.py --test-all --timeout 60

# Create test disk images
python test.py --create-images

# Test without snapshot (risky)
python test.py --test custom_message --no-snapshot
```

### QEMU Safety Features

- ** Snapshot mode**: Changes are temporary
- ** Network isolation**: No internet access
- ** Memory limits**: Prevents resource exhaustion
- ** Auto-shutdown**: Prevents infinite loops

##  Advanced Usage

### Building Individual Variants

```bash
# Build with automatic testing
python build.py --build memz --test

# Build all and test with custom options
python build.py --build-all --test

# List variant details
python build.py --list
```

### Testing Options

```bash
# Extended testing
python test.py --test memz --timeout 120

# Testing without safety features
python test.py --test-all --no-snapshot --no-isolation

# Create disk images for manual testing
python test.py --create-images
```

### Safety Levels

- ** Safe**: No destructive behavior
- ** Experimental**: May have unexpected behavior
- ** Destructive**: Will modify/disk data

##  Safety Guidelines

###  DO
- Always test with QEMU first
- Back up important data
- Use virtual machines
- Read variant descriptions
- Understand safety warnings

###  DON'T
- Test on production systems
- Use without understanding
- Ignore safety warnings
- Test on important data
- Assume variants are harmless

### 🔄 Recovery Procedures

1. **MBR Backup**: Always backup before testing
2. **Recovery Tools**: Keep bootable recovery media
3. **Test Environment**: Use disposable VMs
4. **Documentation**: Read all safety warnings

##  Adding New Variants

1. **Create variant directory**:
   ```bash
   mkdir src/variants/my_variant
   ```

2. **Create assembly file** (`boot.asm`):
   ```nasm
   BITS    16
   ORG     0x7c00
   start:
       ; Your code here
       jmp $
   times 510 - ($-$$) db 0
   dw        0xaa55
   ```

3. **Create variant class** (`variant.py`):
   ```python
   class MyVariant:
       def __init__(self):
           self.name = "my_variant"
           self.display_name = "My Variant"
           self.description = "Description of my variant"
           self.safety_level = "safe"  # safe, destructive, experimental
   ```

4. **Register in build system**:
   ```python
   from variants.my_variant.variant import MyVariant
   
   # Add to variants dict
   self.variants['my_variant'] = MyVariant()
   ```

## 🐛 Troubleshooting

### Build Issues
```bash
# Check dependencies
python build.py --check

# Verify NASM installation
nasm -version

# Verify C++ compiler
g++ --version
```

### QEMU Issues
```bash
# Check QEMU installation
python test.py --check-qemu

# Test basic QEMU
qemu-system-i386 --version
```

### Common Problems

**NASM not found**: Install from https://www.nasm.us/
**C++ compiler missing**: Install MinGW-w64 (Windows) or build-essential (Linux)
**QEMU unavailable**: Install from package manager or official site
**Permission denied**: Check file permissions and run as admin if needed

##  Documentation

- `docs/safety-warning.md` - Detailed safety information
- `docs/qemu-guide.md` - QEMU usage guide
- `docs/variant-descriptions.md` - Variant details

## Contributing Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new variants
4. Update documentation
5. Submit pull request

## License License

MIT License - See LICENSE file for details

## Support Support

- **Issues**: Create GitHub issue
- **Safety**: Read all warnings before use
- **Testing**: Always use QEMU first

---

** Remember: This is powerful software. Use responsibly and test safely!**