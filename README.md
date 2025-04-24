#
README — Système d’analyse intelligente d’e-mails pour projets

⸻

Objectif du projet

Ce projet vise à analyser automatiquement des e-mails afin d’en extraire les informations importantes concernant des projets. L’idée est simple : vous recevez des e-mails au sujet de projets, de leurs échéances, de rôles et de participants. Le système lit ces e-mails, comprend leur contenu, extrait ce qui est important, et stocke le tout dans une base de données. Il peut ensuite générer une fiche de suivi en format HTML, Markdown ou CSV.

⸻

Fonctionnalités principales
	•	Récupération des e-mails depuis un serveur (comme Gmail)
	•	Lecture de fichiers e-mails (.eml)
	•	Extraction automatique des informations suivantes :
	•	Nom du projet
	•	Description
	•	Participants (noms, e-mails, rôles)
	•	Tâches à réaliser
	•	Dates importantes (début, fin, délais)
	•	Utilisation de l’intelligence artificielle (IA) pour comprendre le contenu des mails
	•	Stockage des données dans une base locale (SQLite)
	•	Génération automatique de rapports de projet visuels et clairs

⸻

Pour qui est ce projet ?
	•	Les chefs de projets qui reçoivent beaucoup d’e-mails et veulent automatiser le suivi
	•	Les responsables d’équipe ou freelances gérant plusieurs clients/projets
	•	Toute personne souhaitant transformer des e-mails bruts en données exploitables facilement

⸻

Ce qu’il faut retenir, sans être développeur :
	1.	Le système lit vos mails automatiquement.
	2.	Il utilise une forme d’intelligence pour comprendre de quoi il est question.
	3.	Il résume tout cela dans un tableau clair, avec qui fait quoi, quand et sur quel projet.
	4.	Il crée un rapport que vous pouvez imprimer, partager ou envoyer.

⸻

Structure du projet (vue simple)
	•	main.py — Point de démarrage du projet
	•	email_processor.py — S’occupe de la récupération et lecture des e-mails
	•	nlp_extractor.py — Fait parler l’intelligence artificielle pour comprendre les mails
	•	db_manager.py — Stocke et organise les données dans une base de données
	•	report_generator.py — Crée les rapports de suivi du projet
	•	config.py — Fichier de configuration (comme un panneau de contrôle)
	•	utils.py — Outils techniques communs à tout le système

⸻

Installation rapide (pour les développeurs)

pip install -r requirements.txt
python main.py



⸻

Exemple d’usage
	•	Vous déposez un fichier .eml dans le dossier du projet
	•	Vous lancez le programme
	•	Il extrait les infos : projet “Refonte Site Web”, deadline 15 mai, tâches, personnes concernées
	•	Il crée un joli fichier HTML avec toutes les infos dedans

⸻

Limites actuelles
	•	Fonctionne mieux avec des e-mails bien structurés
	•	Peut ne pas comprendre des mails très vagues ou ambigus

⸻

Avenir du projet
	•	Interface graphique (pas besoin de code)
	•	Intégration avec d’autres outils comme Notion, Trello ou Slack
	•	Système d’apprentissage par retour utilisateur (IA améliorée par vos corrections)

⸻

Conclusion

Ce système vous permet de gagner du temps, de l’organisation et de la clarté. Si vous êtes submergé.e par les e-mails, ce projet transforme le bruit en information claire et utile.

Un assistant de gestion de projet intelligent, personnalisé, à votre service.
