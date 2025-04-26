import openai
from core.logger import setup_logger
import os

class EmailAnalyzer:
    def __init__(self, config):
        openai.api_key = config.openai_api_key
        self.model = config.gpt_model
        self.confidence_threshold = config.confidence_threshold
        self.logger = setup_logger("EmailAnalyzer", os.path.join(config.logs_dir, 'email_analyzer.log'))

    def analyze_emails(self, emails):
        analyzed_projects = []
        for msg in emails:
            if msg.is_multipart():
                content = ""
                for part in msg.walk():
                    content_type = part.get_content_type()
                    if content_type == "text/plain":
                        content += part.get_payload(decode=True).decode()
            else:
                content = msg.get_payload(decode=True).decode()

            try:
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "Tu es un assistant pour détecter les projets IT dans un email."},
                        {"role": "user", "content": f"Voici l'email:\n{content}\nExtrais les projets."}
                    ],
                    temperature=0.2,
                    max_tokens=500
                )
                result = response['choices'][0]['message']['content']
                self.logger.info(f"Projet analysé : {result}")
                analyzed_projects.append(result)
            except Exception as e:
                self.logger.error(f"Erreur d'analyse : {e}")
        return analyzed_projects
