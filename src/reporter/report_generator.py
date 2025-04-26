# --- Importation des modules nécessaires ---
import os
from core.logger import setup_logger  # Module pour configurer un système de journaux (logs)

# --- Définition de la classe responsable de générer les rapports de projet ---
class ReportGenerator:
    def __init__(self, config):
        """
        Initialise la classe ReportGenerator.

        Args:
            config: Configuration contenant les chemins pour les rapports et les logs.
        """
        self.reports_dir = config.reports_dir  # Dossier où les rapports seront stockés
        self.logger = setup_logger("ReportGenerator", os.path.join(config.logs_dir, 'report_generator.log'))  # Mise en place d'un logger spécifique
        os.makedirs(self.reports_dir, exist_ok=True)  # Crée le dossier des rapports si ce n'est pas déjà fait

    def generate_report(self, project):
        """
        Génère un rapport texte pour un projet donné.

        Args:
            project: Tuple contenant l'identifiant du projet et son contenu.
        """
        project_id, project_content = project  # Décomposition du projet : identifiant et contenu
        filename = os.path.join(self.reports_dir, f"project_{project_id}.txt")  # Définir le chemin du fichier de rapport

        try:
            # Ouvre le fichier et écrit le contenu du projet
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(project_content)
            # Si réussi, écrire une information dans les logs
            self.logger.info(f"Rapport généré: {filename}")
        except Exception as e:
            # Si une erreur survient pendant la génération, l’enregistrer dans les logs
            self.logger.error(f"Erreur lors de la génération du rapport: {e}")
