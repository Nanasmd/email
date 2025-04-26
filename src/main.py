import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.config import Config
from fetcher.email_fetcher import EmailFetcher
from analyzer.email_analyzer import EmailAnalyzer
from database.project_database import ProjectDatabase
from reporter.report_generator import ReportGenerator
from core.logger import setup_logger

def main():
    config = Config()
    logger = setup_logger('Main', os.path.join(config.logs_dir, 'app.log'))
    logger.info("=== Démarrage de Email Project Extractor ===")

    try:
        fetcher = EmailFetcher(config)
        analyzer = EmailAnalyzer(config)
        database = ProjectDatabase(config)
        reporter = ReportGenerator(config)

        mail_conn = fetcher.connect()
        if not mail_conn:
            logger.error("Impossible de se connecter au serveur IMAP.")
            return
        
        raw_emails = fetcher.fetch_emails(mail_conn)
        fetcher.disconnect(mail_conn)

        analyzed_projects = analyzer.analyze_emails(raw_emails)

        for project_info in analyzed_projects:
            project_id = database.save_project(project_info)
            if project_id:
                full_project = database.get_full_project_data(project_id)
                reporter.generate_report(full_project)

        logger.info("=== Traitement terminé avec succès ===")
    except Exception as e:
        logger.exception(f"Erreur fatale: {e}")

if __name__ == "__main__":
    main()
