import flask # type: ignore
from flask import Flask, render_template, request, redirect, url_for, flash, session, make_response, jsonify, send_from_directory # type: ignore
import os
import html
import json
import secrets
from datetime import timedelta
from functools import wraps
import logging
from logging.handlers import RotatingFileHandler
from flask_caching import Cache # type: ignore

# Configuration de l'application
app = Flask(__name__)
app.config['DEBUG'] = True

# Configuration sécurisée
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Configuration du caching
cache = Cache(config={'CACHE_TYPE': 'SimpleCache', 'CACHE_DEFAULT_TIMEOUT': 300})
cache.init_app(app)

# Configuration du logging
if not os.path.exists('logs'):
    os.makedirs('logs')

file_handler = RotatingFileHandler('logs/portfolio.log', maxBytes=10240, backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)
app.logger.info('Portfolio startup')

# Décorateur pour les routes nécessitant une authentification
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash('Veuillez vous connecter pour accéder à cette page.', 'warning')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# Fonction pour charger les projets
def load_projects():
    projects = []
    try:
        projects_file = os.path.join(app.root_path, 'data', 'projects.json')
        if os.path.exists(projects_file):
            with open(projects_file, "r", encoding="utf-8") as f:
                projects = json.load(f)
                
            # Trier les projets par date de completion (les plus récents d'abord)
            projects.sort(key=lambda x: x.get('completion_date', ''), reverse=True)
        else:
            # Données par défaut si le fichier n'existe pas
            projects = [
                {
                    "id": 1,
                    "title": "Application E-commerce",
                    "category": "web",
                    "description": "Plateforme de vente en ligne avec gestion des paiements et interface moderne.",
                    "image": "img/projects/placeholder.jpg",
                    "technologies": ["HTML", "CSS", "JavaScript", "Python"],
                    "live_link": "#",
                    "github_link": "#"
                }
            ]
            app.logger.warning('Fichier projects.json non trouvé, utilisation des données par défaut')
            
    except json.JSONDecodeError as e:
        app.logger.error(f'Erreur de parsing JSON: {str(e)}')
        flash('Erreur dans le format des données projets.', 'danger')
    except Exception as e:
        app.logger.error(f'Erreur lors du chargement des projets: {str(e)}')
        flash('Erreur lors du chargement des projets.', 'danger')
    
    return projects

# Vérification des dossiers nécessaires au démarrage
def ensure_directories():
    required_dirs = ['data', 'logs']
    for directory in required_dirs:
        if not os.path.exists(directory):
            os.makedirs(directory)
            app.logger.info(f'Dossier créé: {directory}')

# Exécutez la vérification au démarrage
ensure_directories()

# Routes principales
@app.route("/")
@cache.cached(timeout=300)  # Cache 5 minutes
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/experience")
def experience():
    return render_template("experience.html")

@app.route("/projects")
def projects():
    projects_data = load_projects()
    return render_template("projects.html", projects=projects_data)

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        # Validation des données
        name = html.escape(request.form.get("name", "").strip())
        email = html.escape(request.form.get("email", "").strip())
        message = html.escape(request.form.get("message", "").strip())
        
        # Validation avancée
        errors = []
        if not name:
            errors.append("Le nom est obligatoire.")
        if not email or '@' not in email:
            errors.append("L'email est invalide.")
        if not message or len(message) < 10:
            errors.append("Le message doit contenir au moins 10 caractères.")
        
        if errors:
            for error in errors:
                flash(error, "danger")
        else:
            try:
                # Création du dossier data s'il n'existe pas
                if not os.path.exists('data'):
                    os.makedirs('data')
                
                # Sauvegarde du message
                with open("data/messages.txt", "a", encoding="utf-8") as f:
                    f.write(f"{name} <{email}>: {message}\n")
                
                app.logger.info(f'Nouveau message de {name} ({email})')
                flash("Merci pour votre message ! Nous vous répondrons bientôt.", "success")
                return redirect(url_for("contact"))
                
            except Exception as e:
                app.logger.error(f'Erreur lors de la sauvegarde du message: {str(e)}')
                flash("Une erreur s'est produite. Veuillez réessayer.", "danger")
    
    return render_template("contact.html")

# Routes d'administration
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    # Redirection si déjà connecté
    if session.get('logged_in'):
        return redirect(url_for('admin_dashboard'))
    
    if request.method == "POST":
        password = request.form.get("password", "")
        # Vérification sécurisée du mot de passe
        correct_password = os.environ.get('ADMIN_PASSWORD', 'C@ciestm0nPortfolio')
        
        if secrets.compare_digest(password, correct_password):
            session['logged_in'] = True
            session.permanent = True
            app.logger.info('Connexion admin réussie')
            flash('Connexion réussie.', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            app.logger.warning('Tentative de connexion admin échouée')
            flash('Mot de passe incorrect.', 'danger')
    
    return render_template("admin_login.html")

@app.route("/admin/reset-password", methods=["GET", "POST"])
def admin_reset_password():
    """Route pour réinitialiser le mot de passe admin"""
    if request.method == "POST":
        # Vérification basique
        secret_question = request.form.get("secret_question", "")
        
        # Question secrète - changez-la selon vos besoins
        if secret_question.strip().lower() == "chat":
            new_password = secrets.token_urlsafe(12)
            
            # Utilisation d'une variable d'environnement
            os.environ['ADMIN_PASSWORD'] = new_password
            
            flash(f"Mot de passe réinitialisé: {new_password}", "success")
            app.logger.warning(f'MOT DE PASSE RÉINITIALISÉ: {new_password}')
            return redirect(url_for("admin_login"))
        else:
            flash("Réponse incorrecte à la question secrète", "danger")
    
    return render_template("admin_reset_password.html")

@app.route("/admin")
@login_required
def admin_dashboard():
    messages = []
    try:
        # Vérifier si le dossier data existe
        if not os.path.exists('data'):
            os.makedirs('data')
            flash('Dossier data créé.', 'info')
        
        # Vérifier et lire les messages
        messages_file = 'data/messages.txt'
        if os.path.exists(messages_file):
            with open(messages_file, "r", encoding="utf-8") as f:
                messages = [msg.strip() for msg in f if msg.strip()]
        else:
            # Créer le fichier s'il n'existe pas
            with open(messages_file, "w", encoding="utf-8") as f:
                pass  # Fichier vide
            flash('Fichier messages créé.', 'info')
            
    except Exception as e:
        app.logger.error(f'Erreur lecture messages: {str(e)}')
        flash('Erreur lors de la lecture des messages.', 'danger')
    
    return render_template("admin.html", messages=messages)

@app.route("/admin/clear-messages", methods=["POST"])
@login_required
def clear_messages():
    try:
        messages_file = 'data/messages.txt'
        if os.path.exists(messages_file):
            os.remove(messages_file)
            app.logger.info('Tous les messages ont été effacés')
            return jsonify({"success": True, "message": "Messages effacés avec succès"})
        else:
            return jsonify({"success": False, "message": "Aucun message à effacer"})
    except Exception as e:
        app.logger.error(f'Erreur lors de l\'effacement des messages: {str(e)}')
        return jsonify({"success": False, "message": "Erreur lors de l'effacement"}), 500

@app.route("/admin/logout")
def admin_logout():
    session.pop('logged_in', None)
    flash('Déconnexion réussie.', 'info')
    app.logger.info('Déconnexion admin')
    return redirect(url_for('admin_login'))

# Route pour la vérification Google Search Console
@app.route('/google-verification-xJGVxYq19qHwht6OQEoPa-Ca7nAZarAtqoa4cqix6wI.html')
def google_verification():
    """Route spéciale pour la vérification Google Search Console"""
    try:
        return send_from_directory('static', 'google-verification.html')
    except FileNotFoundError:
        # Fallback si le fichier n'existe pas
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <meta name="google-site-verification" content="xJGVxYq19qHwht6OQEoPa-Ca7nAZarAtqoa4cqix6wI" />
            <title>Google Verification</title>
        </head>
        <body>
            <p>Google Search Console verification successful</p>
        </body>
        </html>
        '''
def google_verification():
    """Route spéciale pour la vérification Google Search Console"""
    return send_from_directory('static', 'google-verification.html')

# Sitemap pour le SEO
@app.route('/sitemap.xml')
def sitemap():
    base_url = request.host_url.rstrip('/')
    pages = [
        {'url': base_url + url_for('home'), 'priority': '1.0'},
        {'url': base_url + url_for('about'), 'priority': '0.8'},
        {'url': base_url + url_for('experience'), 'priority': '0.8'},
        {'url': base_url + url_for('projects'), 'priority': '0.9'},
        {'url': base_url + url_for('contact'), 'priority': '0.7'},
    ]
    
    sitemap_xml = render_template('sitemap.xml', pages=pages)
    response = make_response(sitemap_xml)
    response.headers['Content-Type'] = 'application/xml'
    return response

# Health check endpoint
@app.route('/health')
def health_check():
    return {'status': 'healthy', 'message': 'Portfolio application is running'}

# Headers de sécurité
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response

# Gestion des erreurs
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f'Erreur 500: {str(error)}')
    return render_template('500.html'), 500

if __name__ == "__main__":
    # Debug: afficher toutes les routes enregistrées
    with app.app_context():
        print("=== ROUTES REGISTERED ===")
        for rule in app.url_map.iter_rules():
            print(f"{rule.endpoint}: {rule.rule}")
    
    # Ne pas utiliser debug=True en production
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)