"""
MBR Tools - Common functionality package

This package provides shared utilities for building and testing
Master Boot Record (MBR) variants safely using QEMU.
"""

__version__ = "1.0.0"
__author__ = "Phoenixthrush"

from .mbr_writer import MBRWriter
from .compiler import MBRCompiler
from .qemu_runner import QEMURunner

__all__ = ['MBRWriter', 'MBRCompiler', 'QEMURunner']