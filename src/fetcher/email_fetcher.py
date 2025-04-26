# --- Importation des modules nécessaires ---
import imaplib            # Module pour se connecter à une boîte mail via IMAP
import email              # Module pour manipuler les emails
import logging            # Module pour écrire des messages dans des fichiers de logs
from email import message_from_bytes  # Fonction pour convertir un email brut en objet manipulable
from email.message import Message     # Type utilisé pour les emails
from email.header import decode_header # Pour décoder les entêtes d'email
from typing import List               # Pour préciser les types de retour de fonctions

# --- Définition de la classe pour récupérer les emails ---
class EmailFetcher:
    def __init__(self, config):
        """
        Initialise la classe EmailFetcher avec la configuration donnée.

        Args:
            config: Configuration contenant les paramètres de connexion au serveur mail.
        """
        self.server = config.imap_server      # Adresse du serveur IMAP
        self.port = config.imap_port           # Port utilisé pour la connexion
        self.user = config.email_user          # Identifiant de connexion (adresse email)
        self.password = config.email_pass      # Mot de passe de l'email
        self.use_ssl = config.use_ssl          # Indique si la connexion doit être sécurisée (SSL)
        self.fetch_limit = config.fetch_limit  # Nombre maximum d'emails à récupérer
        self.logger = logging.getLogger('EmailFetcher')  # Système de journalisation pour cette classe

    def connect(self):
        """
        Se connecte au serveur IMAP et authentifie l'utilisateur.

        Returns:
            Connexion au serveur ou None en cas d'erreur.
        """
        try:
            # Utilise une connexion sécurisée si SSL est demandé
            if self.use_ssl:
                conn = imaplib.IMAP4_SSL(self.server, self.port)
            else:
                conn = imaplib.IMAP4(self.server, self.port)
            
            # Connexion au serveur avec identifiant et mot de passe
            conn.login(self.user, self.password)
            self.logger.info(f"Connecté au serveur IMAP : {self.server}")
            return conn
        except Exception as e:
            # En cas d'erreur de connexion, enregistre l'erreur et retourne None
            self.logger.error(f"Erreur de connexion IMAP: {e}")
            return None

    def fetch_emails(self, mail_conn, folder: str = "INBOX") -> List[Message]:
        """
        Récupère les emails présents dans un dossier donné.

        Args:
            mail_conn: Connexion active au serveur IMAP.
            folder (str): Nom du dossier à consulter (par défaut "INBOX").

        Returns:
            Liste d'objets Message représentant les emails récupérés.
        """
        try:
            mail_conn.select(folder)  # Sélectionne le dossier d'emails
            typ, data = mail_conn.search(None, 'ALL')  # Cherche tous les emails disponibles
            mail_ids = data[0].split()  # Liste des identifiants d'emails

            fetched_mails = []
            # Récupère uniquement les derniers emails selon la limite définie
            for mail_id in mail_ids[-self.fetch_limit:]:
                typ, msg_data = mail_conn.fetch(mail_id, '(RFC822)')  # Récupère le contenu complet de l'email
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        # Convertit les données brutes en objet email manipulable
                        msg = message_from_bytes(response_part[1])
                        fetched_mails.append(msg)

            self.logger.info(f"{len(fetched_mails)} emails récupérés.")
            return fetched_mails
        except Exception as e:
            # En cas d'erreur lors de la récupération, enregistre l'erreur et retourne une liste vide
            self.logger.error(f"Erreur lors de la récupération des emails: {e}")
            return []

    def disconnect(self, mail_conn):
        """
        Se déconnecte proprement du serveur IMAP.

        Args:
            mail_conn: Connexion active au serveur IMAP.
        """
        try:
            mail_conn.logout()  # Déconnexion du serveur
            self.logger.info("Déconnecté du serveur IMAP.")
        except Exception as e:
            # Si une erreur survient lors de la déconnexion, l'enregistrer comme avertissement
            self.logger.warning(f"Erreur lors de la déconnexion : {e}")
