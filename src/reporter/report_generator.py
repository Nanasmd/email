import os
from core.logger import setup_logger

class ReportGenerator:
    def __init__(self, config):
        self.reports_dir = config.reports_dir
        self.logger = setup_logger("ReportGenerator", os.path.join(config.logs_dir, 'report_generator.log'))
        os.makedirs(self.reports_dir, exist_ok=True)

    def generate_report(self, project):
        project_id, project_content = project
        filename = os.path.join(self.reports_dir, f"project_{project_id}.txt")
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(project_content)
            self.logger.info(f"Rapport généré: {filename}")
        except Exception as e:
            self.logger.error(f"Erreur lors de la génération du rapport: {e}")
