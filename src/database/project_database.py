# --- Importation des modules nécessaires ---
import sqlite3                  # Module pour manipuler une base de données SQLite
import os
from core.logger import setup_logger   # Module pour configurer un système de journaux (logs)

# --- Définition de la classe pour gérer la base de données des projets ---
class ProjectDatabase:
    def __init__(self, config):
        """
        Initialise la classe ProjectDatabase.

        Args:
            config: Configuration contenant le chemin vers la base de données et les dossiers de logs.
        """
        self.db_path = config.database_path  # Chemin vers le fichier de la base de données SQLite
        self.logger = setup_logger("ProjectDatabase", os.path.join(config.logs_dir, 'project_database.log'))  # Création d'un logger dédié
        self._create_projects_table()  # Vérifie que la table nécessaire existe

    def _create_projects_table(self):
        """
        Crée la table 'projects' dans la base de données si elle n'existe pas encore.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT
                )
            """)  # Crée une table avec deux colonnes : id et contenu du projet
            conn.commit()  # Sauvegarde la création de la table
            self.logger.info("Table projects prête.")  # Log pour indiquer que la table est prête

    def save_project(self, project_data):
        """
        Enregistre un projet dans la base de données.

        Args:
            project_data: Le contenu du projet à sauvegarder.

        Returns:
            int: L'identifiant unique (id) du projet sauvegardé.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO projects (content) VALUES (?)", (project_data,))  # Insère le contenu du projet
            conn.commit()  # Sauvegarde l'insertion
            self.logger.info(f"Projet sauvegardé.")  # Log pour confirmer l'enregistrement
            return cursor.lastrowid  # Retourne l'id du nouveau projet inséré

    def get_full_project_data(self, project_id):
        """
        Récupère les informations complètes d'un projet grâce à son identifiant.

        Args:
            project_id: L'identifiant du projet à récupérer.

        Returns:
            tuple: Les données du projet sous forme (id, contenu).
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM projects WHERE id=?", (project_id,))  # Recherche du projet par son id
            return cursor.fetchone()  # Retourne le premier résultat trouvé (ou None)
