# --- Importation des modules nécessaires ---
import json   # Module pour lire un fichier JSON
import os     # Module pour gérer les chemins et fichiers

# --- Définition de la classe pour charger un fichier de configuration brut ---
class ConfigLoader:
    @staticmethod
    def load_config(config_path="src/config/config.json"):
        """
        Charge la configuration JSON brute depuis un fichier donné.

        Args:
            config_path (str): Chemin du fichier de configuration JSON.

        Returns:
            dict: Contenu du fichier de configuration.
        """
        # Vérifie que le fichier existe
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Fichier de configuration introuvable: {config_path}")

        # Lecture et chargement du JSON
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        return config  # Retourne la configuration sous forme de dictionnaire
