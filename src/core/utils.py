# --- Importation des modules nécessaires ---
import re                   # Module pour gérer les expressions régulières
import unicodedata           # Module pour normaliser les caractères (ex : enlever les accents)
import hashlib               # Module pour générer des empreintes numériques (hash)
import os                    # Module pour la gestion de fichiers
import importlib.util        # Module pour vérifier si un module Python est disponible
from typing import List, Optional

# --- Classe pour les outils liés au traitement de texte ---
class TextUtils:
    """Outils de traitement de texte pour l'analyse des emails."""

    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Nettoie un texte : suppression des accents, mise en minuscules, suppression des caractères spéciaux.

        Args:
            text (str): Texte brut.

        Returns:
            str: Texte propre et normalisé.
        """
        if not text:
            return ""

        # Mise en minuscules
        text = text.lower()
        # Suppression des accents
        text = unicodedata.normalize('NFKD', text)
        text = ''.join(c for c in text if not unicodedata.combining(c))
        # Suppression de tout caractère qui n'est pas lettre/chiffre/espace
        text = re.sub(r'[^\w\s]', ' ', text)
        # Suppression des espaces multiples
        text = re.sub(r'\s+', ' ', text).strip()

        return text

    @staticmethod
    def extract_emails(text: str) -> List[str]:
        """
        Extrait toutes les adresses emails contenues dans un texte.

        Args:
            text (str): Texte brut.

        Returns:
            List[str]: Liste des emails détectés.
        """
        if not text:
            return []

        pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
        return re.findall(pattern, text)

    @staticmethod
    def chunk_text(text: str, chunk_size: int = 2000) -> List[str]:
        """
        Divise un long texte en morceaux plus petits de taille contrôlée.

        Args:
            text (str): Texte à découper.
            chunk_size (int): Taille maximale pour chaque morceau.

        Returns:
            List[str]: Liste de morceaux de texte.
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

# --- Classe pour les outils liés à la gestion des fichiers ---
class FileUtils:
    """Outils pour la gestion des fichiers."""

    @staticmethod
    def ensure_dir_exists(path: str) -> None:
        """
        Crée un dossier s'il n'existe pas.

        Args:
            path (str): Chemin du dossier.
        """
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)

    @staticmethod
    def calculate_hash(data: str) -> str:
        """
        Calcule le hash SHA256 d'une chaîne de caractères.

        Args:
            data (str): Texte à hasher.

        Returns:
            str: Empreinte numérique du texte.
        """
        return hashlib.sha256(data.encode('utf-8')).hexdigest()

    @staticmethod
    def is_module_available(module_name: str) -> bool:
        """
        Vérifie si un module Python est installé et accessible.

        Args:
            module_name (str): Nom du module à tester.

        Returns:
            bool: True si le module est disponible, sinon False.
        """
        return importlib.util.find_spec(module_name) is not None
