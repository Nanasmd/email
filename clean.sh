#!/bin/bash

echo "🧹 Nettoyage du projet en cours..."

# Désactivation de l'environnement virtuel si actif
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "🚪 Désactivation de l'environnement virtuel..."
    deactivate
fi

# Suppression de l'environnement virtuel
if [ -d ".venv" ]; then
    echo "🗑️ Suppression de l'environnement virtuel (.venv)..."
    rm -rf .venv
fi

# Suppression de la base de données
if [ -f "projects.db" ]; then
    echo "🗂️ Suppression du fichier de base de données (projects.db)..."
    rm -f projects.db
fi

# Suppression des répertoires fiches, reports, logs
for dir in fiches reports logs; do
    if [ -d "$dir" ]; then
        echo "📂 Suppression du dossier $dir/..."
        rm -rf "$dir"
    fi
done

echo "✅ Nettoyage terminé ! Ton projet est propre comme un sou neuf 👑"
