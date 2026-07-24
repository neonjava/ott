# engine/model_manager/__init__.py
"""
GenOTT Model Manager Subsystem
Handles model discovery, weight management, CUDA/CPU device selection, memory cleanup, 
lazy loading, hot unloading, model installation, and model registry.
"""

from .manager import ModelManager
from .registry import ModelRegistry
from .installer import ModelInstaller

__all__ = ["ModelManager", "ModelRegistry", "ModelInstaller"]
