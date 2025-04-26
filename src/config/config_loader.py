import json
import os

class ConfigLoader:
    @staticmethod
    def load_config(config_path="src/config/config.json"):
        """Charge la configuration JSON à partir du fichier spécifié"""
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Fichier de configuration introuvable: {config_path}")
        
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        
        return config
