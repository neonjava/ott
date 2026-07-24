# engine/model_manager/__init__.py
"""
GenOTT Model Manager Subsystem
Handles model discovery, weight management, CUDA/CPU device selection, memory cleanup, lazy loading, and hot unloading.
"""

from .manager import ModelManager

__all__ = ["ModelManager"]
