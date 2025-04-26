📚 Email Project Extractor - Mode d'emploi

👩‍💻 Présentation du projet

Le but de ce projet est de récupérer automatiquement des emails,
analyser leur contenu avec l'intelligence artificielle (GPT-4),
extraire les informations de projet (titre, description, client...),
puis stocker tout cela proprement dans une base de données SQLite et générer des rapports.

Tout a été conçu avec une architecture propre, professionnelle et modulaire.

🛠️ Technologies utilisées

Python 3.11+

OpenAI GPT-4 API

SQLite3

IMAP Client pour lire les emails

Pandas pour manipuler les données

Logging pour suivre les événements de l’application

📂 Architecture du projet

arduino

email/
├── src/
│   ├── analyzer/
│   ├── config/
│   ├── core/
│   ├── database/
│   ├── fetcher/
│   ├── reporter/
│   └── main.py
├── fiches/
├── logs/
├── reports/
├── requirements.txt
├── run.sh
├── clean.sh
└── README.md

🔥 Mise en place étape par étape

1. Cloner le projet

bash

git clone https://github.com/Nanasmd/email.git
cd email

3. Créer un environnement virtuel Python
   
bash

python3 -m venv .venv
source .venv/bin/activate
(À refaire à chaque fois que vous revenez travailler dessus)

3. Installer les dépendances nécessaires
   
bash

pip install -r requirements.txt

5. Remplir les informations de connexion email + OpenAI
   
Ouvre le fichier src/config/config.json et remplis :

json

{
  "imap_server": "imap.gmail.com",
  "imap_port": 993,
  "email_user": "VOTRE_EMAIL",
  "email_pass": "VOTRE_MOT_DE_PASSE_EMAIL",
  "openai_api_key": "VOTRE_CLE_OPENAI",
  ...
}
Note : Attention aux guillemets "..." autour de chaque valeur.

5. Lancer l'application
bash

./run.sh

Le script :

Active automatiquement l'environnement virtuel .venv

Lance l'application

Gère la sortie proprement

🧹 Nettoyer le projet après usage
Quand vous voulez tout remettre à zéro :

bash

./clean.sh

Cela va supprimer :

L'environnement .venv

La base de données projects.db

Les logs

Les rapports

Les fiches générées

💡 Comment fonctionne l'application ?

Connexion à votre boîte mail via IMAP

Récupération des derniers emails

Envoi du contenu à GPT-4 pour analyse automatique

Extraction des informations importantes

Stockage dans une base SQLite

Génération de rapports PDF

Archivage automatique de tout

📋 Résumé rapide de l'organisation technique

Composant	Rôle
fetcher/email_fetcher.py	Connexion et récupération des emails
analyzer/email_analyzer.py	Analyse des emails via GPT-4
database/project_database.py	Stockage dans SQLite
reporter/report_generator.py	Génération des rapports
core/logger.py	Gestion propre des logs
config/config.json	Centralisation de toutes les configurations

❗ Points importants

⚙️ Toujours activer .venv avant de lancer l'application

🔐 Ne partagez jamais votre email_pass ou openai_api_key

📜 Si besoin d'arrêter ou réinitialiser → utiliser clean.sh

🏆 Félicitations !

Grâce à ce projet, vous :

Savez lire des mails en Python

Savez utiliser une API GPT-4

Savez organiser un projet proprement
