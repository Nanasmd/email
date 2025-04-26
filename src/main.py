# --- Importation des modules nécessaires ---
import os
import sys

# Ajoute le dossier parent au chemin d'importation pour accéder aux modules internes
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# --- Importation des composants du projet ---
from config.config import Config          # Chargement de la configuration (paramètres du projet)
from fetcher.email_fetcher import EmailFetcher    # Module pour récupérer les emails
from analyzer.email_analyzer import EmailAnalyzer # Module pour analyser les emails
from database.project_database import ProjectDatabase  # Module pour enregistrer les projets dans une base de données
from reporter.report_generator import ReportGenerator   # Module pour générer des rapports à partir des projets
from core.logger import setup_logger         # Module pour gérer les journaux d'activité (logs)

# --- Définition de la fonction principale ---
def main():
    # Initialisation de la configuration et du système de logs
    config = Config()
    logger = setup_logger('Main', os.path.join(config.logs_dir, 'app.log'))
    logger.info("=== Démarrage de Email Project Extractor ===")

    try:
        # Création des objets principaux
        fetcher = EmailFetcher(config)     # Outil pour se connecter à la boîte mail
        analyzer = EmailAnalyzer(config)   # Outil pour analyser le contenu des emails
        database = ProjectDatabase(config) # Outil pour enregistrer les projets extraits
        reporter = ReportGenerator(config) # Outil pour créer des rapports des projets

        # Connexion au serveur de messagerie
        mail_conn = fetcher.connect()
        if not mail_conn:
            # Si la connexion échoue, enregistrer l'erreur et arrêter le programme
            logger.error("Impossible de se connecter au serveur IMAP.")
            return
        
        # Récupération des emails disponibles
        raw_emails = fetcher.fetch_emails(mail_conn)

        # Déconnexion propre du serveur mail après récupération
        fetcher.disconnect(mail_conn)

        # Analyse des emails pour extraire les projets
        analyzed_projects = analyzer.analyze_emails(raw_emails)

        # Traitement de chaque projet trouvé
        for project_info in analyzed_projects:
            # Sauvegarde du projet dans la base de données
            project_id = database.save_project(project_info)
            if project_id:
                # Récupération des données complètes du projet
                full_project = database.get_full_project_data(project_id)
                # Génération d'un rapport pour le projet
                reporter.generate_report(full_project)

        # Enregistrement dans les logs que tout s'est déroulé correctement
        logger.info("=== Traitement terminé avec succès ===")

    except Exception as e:
        # En cas d'erreur imprévue, l'erreur est enregistrée dans les logs
        logger.exception(f"Erreur fatale: {e}")

# --- Exécution du programme ---
if __name__ == "__main__":
    main()
