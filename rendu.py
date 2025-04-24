# email_processor.py
import email
import imaplib
import os
import logging
from email.header import decode_header
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor
from utils import Utils

logger = logging.getLogger(__name__)

class EmailProcessor:
    def __init__(self, config):
        self.config = config
        self._cache = {}

    def connect_to_imap(self, credentials: Optional[Dict] = None) -> Optional[imaplib.IMAP4_SSL]:
        if credentials is None:
            server = self.config.get("imap", "server")
            port = self.config.get("imap", "port")
            use_ssl = self.config.get("imap", "use_ssl")
            import getpass
            username = input("Nom d'utilisateur IMAP: ")
            password = getpass.getpass("Mot de passe IMAP: ")
        else:
            server = credentials.get("server", self.config.get("imap", "server"))
            port = credentials.get("port", self.config.get("imap", "port"))
            use_ssl = credentials.get("use_ssl", self.config.get("imap", "use_ssl"))
            username = credentials.get("username")
            password = credentials.get("password")
            if not username or not password:
                logger.error("Identifiants IMAP manquants")
                return None

        try:
            mail = imaplib.IMAP4_SSL(server, port) if use_ssl else imaplib.IMAP4(server, port)
            mail.login(username, password)
            logger.info(f"Connexion réussie au serveur IMAP {server}")
            return mail
        except Exception as e:
            logger.error(f"Erreur de connexion IMAP: {e}")
            return None

    def fetch_emails(self, mail, folder='INBOX', limit=10, criteria='ALL') -> List[email.message.Message]:
        emails = []
        try:
            mail.select(folder)
            status, data = mail.search(None, criteria)
            mail_ids = data[0].split()[-limit:]
            with ThreadPoolExecutor(max_workers=min(10, len(mail_ids))) as executor:
                futures = [executor.submit(self._fetch_single_email, mail, i) for i in mail_ids]
                for f in futures:
                    msg = f.result()
                    if msg:
                        emails.append(msg)
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des emails: {e}")
        return emails

    def _fetch_single_email(self, mail, mail_id):
        try:
            status, data = mail.fetch(mail_id, '(RFC822)')
            if status != 'OK':
                return None
            return email.message_from_bytes(data[0][1])
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de l'email {mail_id}: {e}")
            return None

    def extract_email_content(self, msg: email.message.Message) -> Dict[str, str]:
        subject = self._decode_header(msg.get("Subject", ""))
        sender = self._decode_header(msg.get("From", ""))
        date = msg.get("Date", "")
        body = self._extract_body(msg)
        return {
            "subject": subject,
            "sender": sender,
            "date": date,
            "body": body
        }

    def _decode_header(self, value):
        try:
            parts = decode_header(value)
            return ''.join([part.decode(enc or 'utf-8') if isinstance(part, bytes) else part for part, enc in parts])
        except:
            return value

    def _extract_body(self, message):
        if message.is_multipart():
            for part in message.walk():
                if part.get_content_type() == "text/plain" and 'attachment' not in str(part.get("Content-Disposition")):
                    return part.get_payload(decode=True).decode(part.get_content_charset() or 'utf-8', errors='replace')
        else:
            return message.get_payload(decode=True).decode(message.get_content_charset() or 'utf-8', errors='replace')
        return ""

# nlp_extractor.py
import spacy
from transformers import pipeline
from nltk.tokenize import sent_tokenize

class NLPExtractor:
    def __init__(self, config):
        self.config = config
        self.nlp = spacy.load("fr_core_news_md")
        self.qa = pipeline("question-answering", model="camembert-base", cache_dir=config.get("nlp", "cache_dir"))

    def extract_info(self, content):
        text = content['subject'] + '\n' + content['body']
        doc = self.nlp(text)
        info = {"project_name": content['subject'], "participants": [], "dates": [], "tasks": [], "description": ""}

        for ent in doc.ents:
            if ent.label_ == 'PER':
                info['participants'].append(ent.text)
            if ent.label_ == 'DATE':
                info['dates'].append(ent.text)

        for sent in sent_tokenize(text):
            if any(k in sent.lower() for k in ["faire", "implémenter", "réaliser"]):
                info['tasks'].append(sent.strip())

        for q in ["Quel est l'objectif du projet ?", "De quoi parle ce projet ?"]:
            try:
                res = self.qa(question=q, context=text)
                if res['score'] > self.config.get("nlp", "confidence_threshold"):
                    info['description'] = res['answer']
                    break
            except:
                continue

        return info

# db_manager.py
import sqlite3
from datetime import datetime

class DBManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, description TEXT, date_added TEXT
        )""")
        c.execute("""
        CREATE TABLE IF NOT EXISTS participants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER, name TEXT,
            FOREIGN KEY(project_id) REFERENCES projects(id)
        )""")
        c.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER, description TEXT,
            FOREIGN KEY(project_id) REFERENCES projects(id)
        )""")
        conn.commit()
        conn.close()

    def save_project(self, info):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("INSERT INTO projects (name, description, date_added) VALUES (?, ?, ?)",
                  (info['project_name'], info['description'], datetime.now().isoformat()))
        project_id = c.lastrowid

        for p in info['participants']:
            c.execute("INSERT INTO participants (project_id, name) VALUES (?, ?)", (project_id, p))
        for t in info['tasks']:
            c.execute("INSERT INTO tasks (project_id, description) VALUES (?, ?)", (project_id, t))
        conn.commit()
        conn.close()
        return project_id

# utils.py
import re
import hashlib

class Utils:
    @staticmethod
    def calculate_hash(data):
        return hashlib.sha256(data.encode('utf-8')).hexdigest()

    @staticmethod
    def extract_emails(text):
        return re.findall(r'[\w\.-]+@[\w\.-]+', text)

# config.py
import json
import os

class Config:
    def __init__(self, path="config.json"):
        self.path = path
        if os.path.exists(path):
            with open(path, 'r') as f:
                self.cfg = json.load(f)
        else:
            self.cfg = self.default_config()
            with open(path, 'w') as f:
                json.dump(self.cfg, f, indent=4)

    def default_config(self):
        return {
            "imap": {"server": "imap.gmail.com", "port": 993, "use_ssl": True},
            "nlp": {"confidence_threshold": 0.5, "cache_dir": ".model_cache"},
            "database": {"path": "projects.sqlite"}
        }

    def get(self, *keys):
        cfg = self.cfg
        for key in keys:
            cfg = cfg.get(key, {})
        return cfg if cfg else None
