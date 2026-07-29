# engine/backends/__init__.py
"""
GenOTT Generative Backend Infrastructure
"""

from engine.backends.wan.backend import WANBackend

__all__ = ["WANBackend"]
