import re
import unicodedata
import hashlib
import os
import importlib.util
from typing import List, Optional

class TextUtils:
    """Outils de traitement de texte pour l'analyse des emails."""
    
    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Normalise un texte : suppression des accents, mise en minuscules, nettoyage.
        
        Args:
            text (str): Texte brut.
        
        Returns:
            str: Texte normalisé.
        """
        if not text:
            return ""
        
        text = text.lower()
        text = unicodedata.normalize('NFKD', text)
        text = ''.join(c for c in text if not unicodedata.combining(c))
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text

    @staticmethod
    def extract_emails(text: str) -> List[str]:
        """
        Extrait toutes les adresses emails d'un texte brut.
        
        Args:
            text (str): Texte contenant potentiellement des emails.
        
        Returns:
            List[str]: Liste des emails trouvés.
        """
        if not text:
            return []
        
        pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
        return re.findall(pattern, text)

    @staticmethod
    def chunk_text(text: str, chunk_size: int = 2000) -> List[str]:
        """
        Divise un grand texte en morceaux plus petits (ex : pour API GPT).
        
        Args:
            text (str): Texte à découper.
            chunk_size (int): Taille maximale par morceau.
        
        Returns:
            List[str]: Liste de chunks.
        """
        if not text:
            return []
        
        words = text.split()
        chunks = []
        current_chunk = []

        for word in words:
            current_length = sum(len(w) + 1 for w in current_chunk)  # +1 pour les espaces
            if current_length + len(word) + 1 > chunk_size:
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]
            else:
                current_chunk.append(word)

        if current_chunk:
            chunks.append(' '.join(current_chunk))

        return chunks

class FileUtils:
    """Outils pour la gestion des fichiers."""

    @staticmethod
    def ensure_dir_exists(path: str) -> None:
        """
        Crée un répertoire s'il n'existe pas encore.
        
        Args:
            path (str): Chemin du répertoire.
        """
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)

    @staticmethod
    def calculate_hash(data: str) -> str:
        """
        Calcule le hash SHA256 d'une chaîne de caractères.
        
        Args:
            data (str): Données à hasher.
        
        Returns:
            str: Hash SHA256.
        """
        return hashlib.sha256(data.encode('utf-8')).hexdigest()

    @staticmethod
    def is_module_available(module_name: str) -> bool:
        """
        Vérifie si un module Python est disponible.
        
        Args:
            module_name (str): Nom du module à tester.
        
        Returns:
            bool: True si disponible, sinon False.
        """
        return importlib.util.find_spec(module_name) is not None
