#!/bin/bash

echo "👑 Démarrage de Email Project Extractor..."

# Activer l'environnement virtuel
if [ -d ".venv" ]; then
    echo "🐍 Activation de l'environnement virtuel..."
    source .venv/bin/activate
else
    echo "❗ Environnement virtuel non trouvé. Création en cours..."
    python3 -m venv .venv
    source .venv/bin/activate
fi

# Installer les dépendances
echo "📦 Installation des dépendances..."
pip install --upgrade pip
pip install -r requirements.txt

# Lancer l'application
echo "🚀 Lancement de l'application..."
python3 src/main.py

# Fin
echo "✅ Application terminée."
