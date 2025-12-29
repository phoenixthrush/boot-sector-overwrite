"""
Custom Message MBR Variant

This variant displays a custom message with colors on boot.
"""

from pathlib import Path
from typing import Dict, Any


class CustomMessageVariant:
    """Custom message MBR variant with friendly text."""
    
    def __init__(self):
        self.name = "custom_message"
        self.display_name = "Custom Message"
        self.description = "Displays a custom knock-knock joke message with colors"
        self.safety_level = "safe"  # safe, destructive, experimental
        self.category = "message"
    
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
                'Text display',
                'Color support',
                'Screen clearing',
                'Custom message'
            ],
            'test_options': {
                'timeout_seconds': 15,
                'memory_mb': 64,
                'snapshot': True,
                'isolated': True
            }
        }
    
    def get_safety_warning(self) -> str:
        """Get safety warning for this variant."""
        return f"""
  {self.display_name} MBR Variant

Safety Level: {self.safety_level.upper()}

This MBR variant is considered SAFE and only displays a text message.
It does not modify disk data or perform destructive operations.

However, writing any MBR to a physical drive will overwrite the existing
boot sector and may make the drive unbootable.

Always test with QEMU first!
"""