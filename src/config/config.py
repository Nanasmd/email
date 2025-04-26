import os
from dotenv import load_dotenv
import json


class Config:
    def __init__(self, config_path="src/config/config.json"):
        load_dotenv()

        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Fichier de configuration introuvable: {config_path}")
        
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Email
        self.imap_server = data.get("imap_server")
        self.imap_port = data.get("imap_port")
        self.email_user = os.getenv("EMAIL_USER", data.get("email_user"))
        self.email_pass = os.getenv("EMAIL_PASS", data.get("email_pass"))
        self.use_ssl = data.get("use_ssl", True)
        self.fetch_limit = data.get("fetch_limit", 10)

        # OpenAI
        self.openai_api_key = os.getenv("OPENAI_API_KEY", data.get("openai_api_key"))
        self.gpt_model = data.get("gpt_model", "gpt-4")
        self.confidence_threshold = data.get("confidence_threshold", 0.75)

        # Base de données et Logs
        self.database_path = data.get("database_path", "projects.db")
        self.reports_dir = data.get("reports_dir", "reports")
        self.logs_dir = data.get("logs_dir", "logs")
        self.max_log_size = data.get("max_log_size", 5242880)
        self.backup_log_count = data.get("backup_log_count", 3)
