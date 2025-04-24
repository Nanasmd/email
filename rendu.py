"""
Système d'analyse d'e-mails pour extraction d'informations de projets

Ce script permet d'analyser le contenu des e-mails pour identifier et extraire 
automatiquement les informations pertinentes sur les projets, en vue de leur intégration 
dans une base de données et fiche de suivi.

Fonctionnalités:
- Extraction d'e-mails depuis un serveur IMAP ou fichiers .eml
- Analyse NLP pour identifier les informations clés des projets
- Extraction des dates, noms de projets, participants, tâches, échéances, etc.
- Stockage dans une base de données SQL
- Génération de fiches de suivi
"""

import email
import imaplib
import re
import sqlite3
import pandas as pd
import os
import datetime
from email.header import decode_header
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
import spacy
from transformers import pipeline

# Téléchargement des ressources nécessaires
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')

# Charger le modèle spaCy pour le français
nlp = spacy.load('fr_core_news_md')

# Initialiser le pipeline de question-réponse de Hugging Face
qa_pipeline = pipeline("question-answering", model="camembert-base")

class EmailAnalyzer:
    def __init__(self, db_path="projects_db.sqlite"):
        """Initialise l'analyseur d'emails avec une connexion à la base de données"""
        self.db_path = db_path
        self.setup_database()
        
    def setup_database(self):
        """Crée la structure de la base de données si elle n'existe pas"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Création de la table des projets
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_name TEXT NOT NULL,
                description TEXT,
                start_date TEXT,
                end_date TEXT,
                status TEXT DEFAULT 'En cours',
                email_source TEXT,
                creation_date TEXT
            )
        ''')
        
        # Création de la table des participants
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS participants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                name TEXT NOT NULL,
                email TEXT,
                role TEXT,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            )
        ''')
        
        # Création de la table des tâches
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                description TEXT NOT NULL,
                deadline TEXT,
                status TEXT DEFAULT 'À faire',
                assigned_to INTEGER,
                FOREIGN KEY (project_id) REFERENCES projects (id),
                FOREIGN KEY (assigned_to) REFERENCES participants (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def connect_to_mail_server(self, username, password, imap_server='imap.gmail.com'):
        """Se connecte au serveur IMAP et récupère les e-mails"""
        try:
            mail = imaplib.IMAP4_SSL(imap_server)
            mail.login(username, password)
            return mail
        except Exception as e:
            print(f"Erreur de connexion au serveur mail: {e}")
            return None
    
    def fetch_emails(self, mail, folder='INBOX', limit=10, search_criteria='ALL'):
        """Récupère les emails depuis le serveur"""
        if not mail:
            return []
            
        mail.select(folder)
        status, data = mail.search(None, search_criteria)
        mail_ids = data[0].split()
        
        # Limiter le nombre d'emails à traiter
        if limit > 0:
            mail_ids = mail_ids[-limit:]
        
        emails = []
        for mail_id in mail_ids:
            status, data = mail.fetch(mail_id, '(RFC822)')
            for response_part in data:
                if isinstance(response_part, tuple):
                    message = email.message_from_bytes(response_part[1])
                    emails.append(message)
        
        return emails
    
    def process_email_file(self, file_path):
        """Traite un fichier email .eml"""
        with open(file_path, 'rb') as file:
            message = email.message_from_bytes(file.read())
            return message
    
    def extract_email_content(self, message):
        """Extrait le contenu textuel d'un email"""
        subject = ""
        if message['subject']:
            subject = decode_header(message['subject'])[0][0]
            if isinstance(subject, bytes):
                subject = subject.decode()
        
        sender = message['from'] if message['from'] else ""
        date = message['date'] if message['date'] else ""
        
        body = ""
        if message.is_multipart():
            for part in message.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                
                if "attachment" not in content_disposition:
                    if content_type == "text/plain":
                        try:
                            body_part = part.get_payload(decode=True).decode()
                            body += body_part
                        except:
                            pass
                    elif content_type == "text/html":
                        try:
                            import html2text
                            html = part.get_payload(decode=True).decode()
                            body += html2text.html2text(html)
                        except:
                            pass
        else:
            try:
                body = message.get_payload(decode=True).decode()
            except:
                body = message.get_payload()
        
        return {
            "subject": subject,
            "sender": sender,
            "date": date,
            "body": body
        }
    
    def extract_project_info(self, email_content):
        """
        Analyse le contenu de l'email pour extraire les informations du projet
        en utilisant des techniques de NLP
        """
        text = f"{email_content['subject']}\n\n{email_content['body']}"
        doc = nlp(text)
        
        # Initialisation des informations du projet
        project_info = {
            "project_name": None,
            "description": None,
            "start_date": None,
            "end_date": None,
            "participants": [],
            "tasks": []
        }
        
        # Extraction du nom du projet (souvent dans le sujet)
        if email_content['subject']:
            # Recherche de mots-clés typiques dans le sujet
            subject_lower = email_content['subject'].lower()
            project_keywords = ["projet", "project", "proposition", "proposition de projet"]
            
            for keyword in project_keywords:
                if keyword in subject_lower:
                    pattern = rf"{keyword}\s*:?\s*([^,\.;]+)"
                    match = re.search(pattern, subject_lower, re.IGNORECASE)
                    if match:
                        project_info["project_name"] = match.group(1).strip().title()
                        break
            
            # Si pas de match avec les mots-clés, utiliser le sujet complet
            if not project_info["project_name"]:
                project_info["project_name"] = email_content['subject'].strip()
        
        # Extraction des dates
        dates = []
        for ent in doc.ents:
            if ent.label_ == "DATE":
                dates.append(ent.text)
        
        if len(dates) >= 2:
            # Considérer la première date comme date de début et la dernière comme date de fin
            project_info["start_date"] = dates[0]
            project_info["end_date"] = dates[-1]
        elif len(dates) == 1:
            # Si une seule date est trouvée, la considérer comme date de début
            project_info["start_date"] = dates[0]
        
        # Extraction des personnes (participants potentiels)
        for ent in doc.ents:
            if ent.label_ == "PER":
                project_info["participants"].append({
                    "name": ent.text,
                    "email": None,
                    "role": None
                })
        
        # Extraction d'emails supplémentaires
        email_pattern = r'[\w\.-]+@[\w\.-]+'
        found_emails = re.findall(email_pattern, text)
        
        # Associer les emails aux participants ou ajouter de nouveaux participants
        for email_addr in found_emails:
            # Vérifier si l'email peut être associé à un participant existant
            matched = False
            for participant in project_info["participants"]:
                if participant["email"] is None:
                    participant["email"] = email_addr
                    matched = True
                    break
            
            # Si l'email ne correspond à aucun participant existant, l'ajouter comme nouveau
            if not matched:
                project_info["participants"].append({
                    "name": None,
                    "email": email_addr,
                    "role": None
                })
        
        # Extraction des tâches (phrases contenant des verbes d'action et éventuellement des dates)
        sentences = sent_tokenize(text)
        task_keywords = ["tâche", "task", "faire", "réaliser", "compléter", "livrer", "implémenter"]
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            is_task = False
            
            # Vérifier si la phrase contient un mot-clé de tâche
            for keyword in task_keywords:
                if keyword in sentence_lower:
                    is_task = True
                    break
            
            # Utiliser spaCy pour détecter les verbes à l'infinitif (souvent utilisés pour décrire les tâches)
            if not is_task:
                sent_doc = nlp(sentence)
                for token in sent_doc:
                    if token.pos_ == "VERB" and token.is_sent_start:
                        is_task = True
                        break
            
            if is_task:
                # Recherche d'une date limite potentielle dans la phrase
                deadline = None
                sent_doc = nlp(sentence)
                for ent in sent_doc.ents:
                    if ent.label_ == "DATE":
                        deadline = ent.text
                        break
                
                task = {
                    "description": sentence.strip(),
                    "deadline": deadline,
                    "assigned_to": None
                }
                project_info["tasks"].append(task)
        
        # Extraire la description du projet
        # Utiliser le pipeline de question-réponse pour trouver une description potentielle
        questions = [
            "De quoi parle ce projet ?",
            "Quel est l'objectif du projet ?",
            "Quelle est la description du projet ?"
        ]
        
        for question in questions:
            try:
                result = qa_pipeline(question=question, context=text)
                if result["score"] > 0.5:  # Seuil de confiance
                    project_info["description"] = result["answer"]
                    break
            except:
                continue
        
        # Si aucune description n'a été trouvée, utiliser les premières phrases du corps
        if not project_info["description"]:
            body_sentences = sent_tokenize(email_content['body'])
            if body_sentences:
                # Prendre les 2-3 premières phrases comme description
                project_info["description"] = " ".join(body_sentences[:min(3, len(body_sentences))])
        
        return project_info
    
    def save_project_to_db(self, project_info, email_source):
        """Enregistre les informations du projet dans la base de données"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Insérer le projet
        cursor.execute('''
            INSERT INTO projects 
            (project_name, description, start_date, end_date, email_source, creation_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            project_info["project_name"], 
            project_info["description"], 
            project_info["start_date"], 
            project_info["end_date"],
            email_source,
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        
        # Récupérer l'ID du projet inséré
        project_id = cursor.lastrowid
        
        # Insérer les participants
        for participant in project_info["participants"]:
            cursor.execute('''
                INSERT INTO participants
                (project_id, name, email, role)
                VALUES (?, ?, ?, ?)
            ''', (
                project_id,
                participant["name"],
                participant["email"],
                participant["role"]
            ))
        
        # Insérer les tâches
        for task in project_info["tasks"]:
            cursor.execute('''
                INSERT INTO tasks
                (project_id, description, deadline, assigned_to)
                VALUES (?, ?, ?, ?)
            ''', (
                project_id,
                task["description"],
                task["deadline"],
                task["assigned_to"]
            ))
        
        conn.commit()
        conn.close()
        
        return project_id
    
    def generate_project_report(self, project_id, output_format="html"):
        """Génère une fiche de suivi pour le projet"""
        conn = sqlite3.connect(self.db_path)
        
        # Récupérer les informations du projet
        project_df = pd.read_sql_query(f"SELECT * FROM projects WHERE id = {project_id}", conn)
        
        if project_df.empty:
            conn.close()
            return f"Projet avec ID {project_id} non trouvé."
            
        # Récupérer les participants
        participants_df = pd.read_sql_query(f"SELECT * FROM participants WHERE project_id = {project_id}", conn)
        
        # Récupérer les tâches
        tasks_df = pd.read_sql_query(f"SELECT * FROM tasks WHERE project_id = {project_id}", conn)
        
        conn.close()
        
        # Générer la fiche de suivi selon le format demandé
        if output_format.lower() == "html":
            return self._generate_html_report(project_df, participants_df, tasks_df)
        elif output_format.lower() == "markdown":
            return self._generate_markdown_report(project_df, participants_df, tasks_df)
        elif output_format.lower() == "csv":
            return self._generate_csv_report(project_df, participants_df, tasks_df)
        else:
            return "Format de sortie non pris en charge."
    
    def _generate_html_report(self, project_df, participants_df, tasks_df):
        """Génère une fiche de suivi au format HTML"""
        project = project_df.iloc[0]
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Fiche de suivi - {project['project_name']}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                h1 {{ color: #2c3e50; }}
                h2 {{ color: #3498db; margin-top: 30px; }}
                table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
                th, td {{ padding: 10px; text-align: left; border: 1px solid #ddd; }}
                th {{ background-color: #f2f2f2; }}
                .status {{ padding: 5px 10px; border-radius: 4px; }}
                .status-encours {{ background-color: #3498db; color: white; }}
                .status-termine {{ background-color: #2ecc71; color: white; }}
                .status-afaire {{ background-color: #e74c3c; color: white; }}
            </style>
        </head>
        <body>
            <h1>Fiche de suivi du projet: {project['project_name']}</h1>
            
            <h2>Informations générales</h2>
            <table>
                <tr><th>Description</th><td>{project['description']}</td></tr>
                <tr><th>Date de début</th><td>{project['start_date']}</td></tr>
                <tr><th>Date de fin</th><td>{project['end_date']}</td></tr>
                <tr><th>Statut</th><td><span class="status status-{project['status'].lower().replace(' ', '')}">{project['status']}</span></td></tr>
                <tr><th>Création de la fiche</th><td>{project['creation_date']}</td></tr>
            </table>
            
            <h2>Participants</h2>
            <table>
                <tr>
                    <th>Nom</th>
                    <th>Email</th>
                    <th>Rôle</th>
                </tr>
        """
        
        for _, participant in participants_df.iterrows():
            html += f"""
                <tr>
                    <td>{participant['name'] or 'Non spécifié'}</td>
                    <td>{participant['email'] or 'Non spécifié'}</td>
                    <td>{participant['role'] or 'Non spécifié'}</td>
                </tr>
            """
        
        html += """
            </table>
            
            <h2>Tâches</h2>
            <table>
                <tr>
                    <th>Description</th>
                    <th>Échéance</th>
                    <th>Statut</th>
                </tr>
        """
        
        for _, task in tasks_df.iterrows():
            status_class = task['status'].lower().replace(' ', '').replace('à', 'a')
            html += f"""
                <tr>
                    <td>{task['description']}</td>
                    <td>{task['deadline'] or 'Non spécifiée'}</td>
                    <td><span class="status status-{status_class}">{task['status']}</span></td>
                </tr>
            """
        
        html += """
            </table>
        </body>
        </html>
        """
        
        return html
    
    def _generate_markdown_report(self, project_df, participants_df, tasks_df):
        """Génère une fiche de suivi au format Markdown"""
        project = project_df.iloc[0]
        
        markdown = f"""
# Fiche de suivi du projet: {project['project_name']}

## Informations générales

- **Description:** {project['description']}
- **Date de début:** {project['start_date']}
- **Date de fin:** {project['end_date']}
- **Statut:** {project['status']}
- **Création de la fiche:** {project['creation_date']}

## Participants

| Nom | Email | Rôle |
|-----|-------|------|
"""
        
        for _, participant in participants_df.iterrows():
            markdown += f"| {participant['name'] or 'Non spécifié'} | {participant['email'] or 'Non spécifié'} | {participant['role'] or 'Non spécifié'} |\n"
        
        markdown += """
## Tâches

| Description | Échéance | Statut |
|-------------|----------|--------|
"""
        
        for _, task in tasks_df.iterrows():
            markdown += f"| {task['description']} | {task['deadline'] or 'Non spécifiée'} | {task['status']} |\n"
        
        return markdown
    
    def _generate_csv_report(self, project_df, participants_df, tasks_df):
        """Génère des fichiers CSV pour le projet, les participants et les tâches"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        project_id = project_df.iloc[0]['id']
        
        # Créer un dossier pour les rapports
        folder_name = f"project_{project_id}_report_{timestamp}"
        os.makedirs(folder_name, exist_ok=True)
        
        # Sauvegarder les DataFrames en CSV
        project_df.to_csv(f"{folder_name}/project.csv", index=False)
        participants_df.to_csv(f"{folder_name}/participants.csv", index=False)
        tasks_df.to_csv(f"{folder_name}/tasks.csv", index=False)
        
        return f"Rapports CSV générés dans le dossier: {folder_name}"

def main():
    # Exemple d'utilisation
    analyzer = EmailAnalyzer()
    
    # Option 1: Traiter un email à partir d'un fichier
    email_file = "example_email.eml"
    if os.path.exists(email_file):
        email_msg = analyzer.process_email_file(email_file)
        email_content = analyzer.extract_email_content(email_msg)
        project_info = analyzer.extract_project_info(email_content)
        project_id = analyzer.save_project_to_db(project_info, f"Fichier: {email_file}")
        
        print(f"Projet extrait et enregistré avec ID: {project_id}")
        
        # Générer une fiche de suivi
        report = analyzer.generate_project_report(project_id, "html")
        with open(f"project_{project_id}_report.html", "w", encoding="utf-8") as f:
            f.write(report)
        
        print(f"Fiche de suivi générée: project_{project_id}_report.html")
    
    """
    # Option 2: Récupérer et traiter des emails depuis un serveur IMAP
    # Décommentez et configurez selon vos besoins
    
    username = "votre_email@gmail.com"
    password = "votre_mot_de_passe_ou_mot_de_passe_app"
    
    mail = analyzer.connect_to_mail_server(username, password)
    if mail:
        # Récupérer les 5 derniers emails
        emails = analyzer.fetch_emails(mail, limit=5)
        
        for email_msg in emails:
            email_content = analyzer.extract_email_content(email_msg)
            project_info = analyzer.extract_project_info(email_content)
            
            # Ne sauvegarder que si un nom de projet a été détecté
            if project_info["project_name"]:
                project_id = analyzer.save_project_to_db(project_info, f"Email: {email_content['subject']}")
                print(f"Projet extrait et enregistré avec ID: {project_id}")
                
                # Générer une fiche de suivi
                report = analyzer.generate_project_report(project_id, "markdown")
                with open(f"project_{project_id}_report.md", "w", encoding="utf-8") as f:
                    f.write(report)
                
                print(f"Fiche de suivi générée: project_{project_id}_report.md")
        
        mail.logout()
    """

if __name__ == "__main__":
    main()
