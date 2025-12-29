"""
Empty MBR Variant

This variant creates an empty MBR that only contains boot signature.
"""

from pathlib import Path
from typing import Dict, Any


class EmptyVariant:
    """Empty MBR variant - minimal boot sector."""
    
    def __init__(self):
        self.name = "empty"
        self.display_name = "Empty MBR"
        self.description = "Minimal MBR with only boot signature - effectively wipes the boot sector"
        self.safety_level = "destructive"  # safe, destructive, experimental
        self.category = "utility"
    
    def get_config(self) -> Dict[str, Any]:
        """Get variant configuration."""
        return {
            'name': self.name,
            'display_name': self.display_name,
            'description': self.description,
            'safety_level': self.safety_level,
            'category': self.category,
            'assembly_file': Path(__file__).parent / 'boot.asm',
            'features': [
                'Minimal code',
                'Boot signature only',
                'Infinite loop',
                'Boot sector wipe'
            ],
            'test_options': {
                'timeout_seconds': 5,
                'memory_mb': 32,
                'snapshot': True,
                'isolated': True
            }
        }
    
    def get_safety_warning(self) -> str:
        """Get safety warning for this variant."""
        return f"""
🚨 {self.display_name} MBR Variant

Safety Level: {self.safety_level.upper()}

⚠️  WARNING: This variant is DESTRUCTIVE!

This MBR will:
- Wipe existing boot sector
- Prevent the drive from booting
- Make the system unbootable until MBR is restored

Use cases:
- Emergency MBR wipe
- Boot sector cleanup
- Testing recovery procedures

CRITICAL:
- Back up important data before use
- Only test with QEMU or spare hardware
- Keep MBR backup for recovery

This should only be used intentionally for disk wiping!
"""