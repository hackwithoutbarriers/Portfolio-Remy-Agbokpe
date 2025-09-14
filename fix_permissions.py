#!/usr/bin/env python3
import os
import sys

print("🔧 Réparation des permissions et dossiers...")

# Créer les dossiers manquants
for folder in ['data', 'logs']:
    if not os.path.exists(folder):
        os.makedirs(folder)
        print(f"✅ Dossier créé: {folder}")

# Créer les fichiers manquants
for file in ['data/messages.txt', 'data/projects.json']:
    if not os.path.exists(file):
        with open(file, 'w') as f:
            if file.endswith('.json'):
                f.write('[]')
        print(f"✅ Fichier créé: {file}")

# Vérifier les permissions
try:
    os.chmod('data', 0o755)
    os.chmod('logs', 0o755)
    print("✅ Permissions configurées")
except:
    print("⚠️  Impossible de changer les permissions")

print("✅ Réparation terminée!")