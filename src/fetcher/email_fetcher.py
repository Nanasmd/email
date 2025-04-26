import imaplib
import email
import logging
from email import message_from_bytes
from email.message import Message
from email.header import decode_header
from typing import List

class EmailFetcher:
    def __init__(self, config):
        self.server = config.imap_server
        self.port = config.imap_port
        self.user = config.email_user  # ici
        self.password = config.email_pass
        self.use_ssl = config.use_ssl
        self.fetch_limit = config.fetch_limit
        self.logger = logging.getLogger('EmailFetcher')

    def connect(self):
        try:
            if self.use_ssl:
                conn = imaplib.IMAP4_SSL(self.server, self.port)
            else:
                conn = imaplib.IMAP4(self.server, self.port)
            conn.login(self.user, self.password)  # 🔥 correction ici
            self.logger.info(f"Connecté au serveur IMAP : {self.server}")
            return conn
        except Exception as e:
            self.logger.error(f"Erreur de connexion IMAP: {e}")
            return None

    def fetch_emails(self, mail_conn, folder: str = "INBOX") -> List[Message]:
        try:
            mail_conn.select(folder)
            typ, data = mail_conn.search(None, 'ALL')
            mail_ids = data[0].split()

            fetched_mails = []
            for mail_id in mail_ids[-self.fetch_limit:]:
                typ, msg_data = mail_conn.fetch(mail_id, '(RFC822)')
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = message_from_bytes(response_part[1])  # Utiliser directement message_from_bytes
                        fetched_mails.append(msg)
            self.logger.info(f"{len(fetched_mails)} emails récupérés.")
            return fetched_mails
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des emails: {e}")
            return []

    def disconnect(self, mail_conn):
        try:
            mail_conn.logout()
            self.logger.info("Déconnecté du serveur IMAP.")
        except Exception as e:
            self.logger.warning(f"Erreur lors de la déconnexion : {e}")
