# --- Importation des modules nécessaires ---
import openai                    # Utilisé pour interagir avec l'API OpenAI
from core.logger import setup_logger   # Pour configurer un système de journaux (logs)
import os                        # Pour la gestion des chemins de fichiers

# --- Définition de la classe pour analyser les emails avec l'IA ---
class EmailAnalyzer:
    def __init__(self, config):
        """
        Initialise l'EmailAnalyzer avec les paramètres nécessaires.

        Args:
            config: Objet contenant la configuration générale du projet.
        """
        openai.api_key = config.openai_api_key          # Configure la clé API OpenAI
        self.model = config.gpt_model                   # Modèle IA à utiliser (ex: GPT-4)
        self.confidence_threshold = config.confidence_threshold  # Seuil minimal de confiance pour les réponses (non utilisé ici mais disponible)
        self.logger = setup_logger("EmailAnalyzer", os.path.join(config.logs_dir, 'email_analyzer.log'))  # Mise en place du logger spécifique

    def analyze_emails(self, emails):
        """
        Analyse une liste d'emails pour détecter et extraire des projets IT.

        Args:
            emails: Liste d'objets email récupérés.

        Returns:
            List[str]: Liste des projets extraits sous forme de texte.
        """
        analyzed_projects = []  # Liste pour stocker les projets extraits

        for msg in emails:
            # --- Récupération du contenu texte brut de l'email ---
            if msg.is_multipart():
                # Si l'email contient plusieurs parties (ex: texte et pièce jointe)
                content = ""
                for part in msg.walk():
                    content_type = part.get_content_type()
                    if content_type == "text/plain":  # On prend uniquement la partie texte
                        content += part.get_payload(decode=True).decode()
            else:
                # Si l'email est simple (non multipart)
                content = msg.get_payload(decode=True).decode()

            try:
                # --- Analyse du contenu de l'email par OpenAI ---
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "Tu es un assistant pour détecter les projets IT dans un email."},
                        {"role": "user", "content": f"Voici l'email:\n{content}\nExtrais les projets."}
                    ],
                    temperature=0.2,  # Faible température = réponses précises et contrôlées
                    max_tokens=500    # Limite du nombre de mots générés
                )
                # --- Récupération et stockage du résultat ---
                result = response['choices'][0]['message']['content']
                self.logger.info(f"Projet analysé : {result}")
                analyzed_projects.append(result)

            except Exception as e:
                # --- Gestion des erreurs ---
                self.logger.error(f"Erreur d'analyse : {e}")

        return analyzed_projects  # Retourne la liste des projets extraits
