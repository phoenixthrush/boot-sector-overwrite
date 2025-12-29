"""MBR Variants package

This package contains different Master Boot Record variants
with their assembly source code and configuration.
"""

from .custom_message.variant import CustomMessageVariant
from .empty.variant import EmptyVariant
from .memz.variant import MemzVariant

__all__ = ['CustomMessageVariant', 'EmptyVariant', 'MemzVariant']