import sqlite3
import os
from core.logger import setup_logger

class ProjectDatabase:
    def __init__(self, config):
        self.db_path = config.database_path
        self.logger = setup_logger("ProjectDatabase", os.path.join(config.logs_dir, 'project_database.log'))
        self._create_projects_table()

    def _create_projects_table(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT
                )
            """)
            conn.commit()
            self.logger.info("Table projects prête.")

    def save_project(self, project_data):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO projects (content) VALUES (?)", (project_data,))
            conn.commit()
            self.logger.info(f"Projet sauvegardé.")
            return cursor.lastrowid

    def get_full_project_data(self, project_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM projects WHERE id=?", (project_id,))
            return cursor.fetchone()
