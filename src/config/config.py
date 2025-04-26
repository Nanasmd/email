# --- Importation des modules nécessaires ---
import os
from dotenv import load_dotenv    # Charge les variables d'environnement d'un fichier .env
import json

# --- Définition de la classe pour charger et préparer la configuration ---
class Config:
    def __init__(self, config_path="src/config/config.json"):
        """
        Initialise la configuration de l'application.
        
        Args:
            config_path (str): Chemin vers le fichier JSON de configuration.
        """
        load_dotenv()  # Charge d'abord les variables environnementales (.env)

        # Vérifie que le fichier de configuration existe
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Fichier de configuration introuvable: {config_path}")

        # Lecture du fichier JSON
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # --- Paramètres Email ---
        self.imap_server = data.get("imap_server")  # Serveur IMAP
        self.imap_port = data.get("imap_port")      # Port IMAP
        self.email_user = os.getenv("EMAIL_USER", data.get("email_user"))  # Email utilisateur (priorité à .env)
        self.email_pass = os.getenv("EMAIL_PASS", data.get("email_pass"))  # Mot de passe utilisateur (priorité à .env)
        self.use_ssl = data.get("use_ssl", True)    # SSL activé/désactivé
        self.fetch_limit = data.get("fetch_limit", 10)  # Limite d'emails à récupérer

        # --- Paramètres OpenAI ---
        self.openai_api_key = os.getenv("OPENAI_API_KEY", data.get("openai_api_key"))  # Clé API OpenAI
        self.gpt_model = data.get("gpt_model", "gpt-4")        # Modèle IA utilisé
        self.confidence_threshold = data.get("confidence_threshold", 0.75)  # Seuil minimal de confiance IA

        # --- Paramètres Base de données & Logs ---
        self.database_path = data.get("database_path", "projects.db")  # Chemin de la base de données
        self.reports_dir = data.get("reports_dir", "reports")          # Dossier pour les rapports
        self.logs_dir = data.get("logs_dir", "logs")                   # Dossier pour les logs
        self.max_log_size = data.get("max_log_size", 5242880)           # Taille max d'un fichier log
        self.backup_log_count = data.get("backup_log_count", 3)         # Nombre de sauvegardes de logs à garder
