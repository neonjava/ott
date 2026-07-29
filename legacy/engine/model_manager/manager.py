# engine/model_manager/manager.py
import os
import gc
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class ModelManager:
    """
    Manages discovery, weight download, version detection, memory optimization, 
    lazy loading, and hot unloading for generative model backends.
    """

    def __init__(self, base_models_dir: str = "models", third_party_dir: str = "third_party"):
        self.base_models_dir = os.path.abspath(base_models_dir)
        self.third_party_dir = os.path.abspath(third_party_dir)
        self.loaded_models: Dict[str, Any] = {}
        self.device = self.detect_device()

    def detect_device(self) -> str:
        """
        Detects available CUDA hardware or falls back to CPU.
        """
        try:
            import torch
            if torch.cuda.is_available():
                return f"cuda:{torch.cuda.current_device()}"
        except ImportError:
            pass
        return "cpu"

    def discover_models(self) -> List[Dict[str, Any]]:
        """
        Discovers locally available model backends and checkpoint weights.
        """
        discovered = []
        backends = ["wan", "hunyuanvideo", "cogvideox", "ltx-video", "mochi"]
        for backend in backends:
            backend_path = os.path.join(self.third_party_dir, backend)
            weights_path = os.path.join(self.base_models_dir, backend)
            is_installed = os.path.exists(backend_path)
            weights_exist = os.path.exists(weights_path) and len(os.listdir(weights_path)) > 0 if os.path.exists(weights_path) else False
            
            discovered.append({
                "name": backend,
                "installed": is_installed,
                "weights_present": weights_exist,
                "path": backend_path,
                "weights_dir": weights_path
            })
        return discovered

    def get_version(self, model_name: str) -> str:
        """
        Detects version of installed backend model.
        """
        if model_name == "wan":
            return "2.1-open-source"
        return "1.0.0"

    def lazy_load(self, model_name: str, loader_fn: Any, *args: Any, **kwargs: Any) -> Any:
        """
        Loads model lazily into memory if not already present.
        """
        if model_name in self.loaded_models:
            logger.info(f"Model {model_name} already loaded in memory.")
            return self.loaded_models[model_name]

        logger.info(f"Lazy loading model {model_name}...")
        model = loader_fn(*args, **kwargs)
        self.loaded_models[model_name] = model
        return model

    def hot_unload(self, model_name: str) -> bool:
        """
        Unloads model from memory and triggers garbage collection and CUDA cache clearing.
        """
        if model_name in self.loaded_models:
            del self.loaded_models[model_name]
            gc.collect()
            try:
                import torch
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
            except ImportError:
                pass
            logger.info(f"Successfully hot-unloaded model {model_name}")
            return True
        return False

    def unload_all(self):
        """
        Unloads all loaded models.
        """
        keys = list(self.loaded_models.keys())
        for key in keys:
            self.hot_unload(key)

    def download_weights(self, model_name: str, target_dir: Optional[str] = None) -> str:
        """
        Prepares weight destination folder and returns target path.
        """
        dest = target_dir or os.path.join(self.base_models_dir, model_name)
        os.makedirs(dest, exist_ok=True)
        # Log download instruction / trigger download helper
        logger.info(f"Target directory for {model_name} weights ready at {dest}")
        return dest
