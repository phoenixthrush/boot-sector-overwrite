"""
MEMZ MBR Variant

This variant creates visual effects similar to MEMZ malware (harmless version).
"""

from pathlib import Path
from typing import Dict, Any


class MemzVariant:
    """MEMZ-style MBR variant with visual effects."""
    
    def __init__(self):
        self.name = "memz"
        self.display_name = "MEMZ Style"
        self.description = "Harmless MEMZ-inspired visual effects with colorful graphics"
        self.safety_level = "experimental"  # safe, destructive, experimental
        self.category = "visual"
    
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
                'Graphics mode',
                'Color animations',
                'Visual effects',
                'Text overlays'
            ],
            'test_options': {
                'timeout_seconds': 20,
                'memory_mb': 128,
                'snapshot': True,
                'isolated': True
            }
        }
    
    def get_safety_warning(self) -> str:
        """Get safety warning for this variant."""
        return f"""
⚠️  {self.display_name} MBR Variant

Safety Level: {self.safety_level.upper()}

This MBR variant contains visual effects inspired by MEMZ:
- Colorful graphics and animations
- Text overlays and effects
- Graphics mode switching

Important Notes:
- This version is HARMLESS and only displays visuals
- Does not contain malicious code
- Does not modify disk data
- Safe for testing with QEMU

However, this variant is EXPERIMENTAL:
- May not work on all hardware
- Graphics mode may cause issues on some systems
- Only test in virtualized environments

Always test with QEMU before real hardware!
"""