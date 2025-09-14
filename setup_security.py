#!/usr/bin/env python3
"""
Script de configuration de la sécurité - À exécuter une fois
"""
import os
import secrets
from werkzeug.security import generate_password_hash # type: ignore

def setup_security():
    print("🔒 Configuration de la sécurité...")
    
    # Créer les dossiers nécessaires
    os.makedirs('data', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
    # 🔒 Générer une clé secrète si elle n'existe pas
    env_file = '.env'
    if not os.path.exists(env_file):
        secret_key = secrets.token_hex(32)
        with open(env_file, 'w') as f:
            f.write(f"SECRET_KEY={secret_key}\n")
            f.write("FLASK_DEBUG=False\n")
            f.write("FLASK_ENV=development\n")
        print(f"✅ Fichier .env créé avec SECRET_KEY")
    
    # 🔒 Générer un mot de passe admin sécurisé
    password_hash_file = 'data/.password_hash'
    if not os.path.exists(password_hash_file):
        admin_password = secrets.token_urlsafe(16)
        hashed_password = generate_password_hash(admin_password)
        
        with open(password_hash_file, 'w') as f:
            f.write(hashed_password)
        
        print(f"🔑 Mot de passe admin généré: {admin_password}")
        print("⚠️  Notez ce mot de passe et supprimez-le de la console!")
        print("⚠️  Ce mot de passe ne sera plus affiché!")
    
    print("✅ Configuration de sécurité terminée")

if __name__ == "__main__":
    setup_security()