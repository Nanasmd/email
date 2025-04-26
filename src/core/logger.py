# --- Importation des modules nécessaires ---
import logging                     # Module pour la gestion des logs
from logging.handlers import RotatingFileHandler  # Pour limiter la taille des fichiers de logs
import os

# --- Fonction pour configurer un système de journalisation ---
def setup_logger(name: str, log_file: str, level=logging.INFO):
    """
    Configure un logger qui écrit à la fois dans un fichier et sur la console.
    
    Args:
        name (str): Nom du logger.
        log_file (str): Chemin vers le fichier de log.
        level (int): Niveau de journalisation (par défaut: INFO).
    
    Returns:
        logger: Objet logger configuré.
    """
    # Format des messages dans les logs
    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')

    # Crée le dossier du fichier log s'il n'existe pas
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # Crée un handler pour écrire dans un fichier, avec rotation automatique des fichiers
    handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=5)
    handler.setFormatter(formatter)

    # Crée un handler pour afficher aussi les logs dans la console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # Initialise le logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Évite d'ajouter plusieurs fois les mêmes handlers
    if not logger.handlers:
        logger.addHandler(handler)
        logger.addHandler(console_handler)

    return logger
