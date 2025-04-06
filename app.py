import os
import logging

from flask import Flask, render_template, redirect, url_for, flash, session, g, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager, current_user, login_required

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create database base class
class Base(DeclarativeBase):
    pass

# Initialize extensions
db = SQLAlchemy(model_class=Base)
csrf = CSRFProtect()
login_manager = LoginManager()

# Create Flask application
app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # Needed for url_for to generate with https

# Configure the app
app.secret_key = os.environ.get("SESSION_SECRET", "catcharide-dev-key")

# Add API keys to the app configuration
app.config["GOOGLE_MAPS_API_KEY"] = os.environ.get("GOOGLE_MAPS_API_KEY", "")
app.config["GOOGLE_OAUTH_CLIENT_ID"] = os.environ.get("GOOGLE_OAUTH_CLIENT_ID", "")
app.config["GOOGLE_OAUTH_CLIENT_SECRET"] = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET", "")

# Get database configuration from environment variables
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", 
    f"postgresql://{os.environ.get('PGUSER', 'postgres')}:{os.environ.get('PGPASSWORD', 'password')}@{os.environ.get('PGHOST', 'localhost')}:{os.environ.get('PGPORT', '5432')}/{os.environ.get('PGDATABASE', 'catcharide')}"
)
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize extensions with app
db.init_app(app)
csrf.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# Register blueprints
with app.app_context():
    # Import models to ensure they're registered with SQLAlchemy
    from models import User
    
    # Import blueprints
    from auth.routes import auth_bp
    from auth.google_auth import google_auth_bp
    from drivers.routes import drivers_bp
    from passengers.routes import passengers_bp
    from routes.routes import routes_bp
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(google_auth_bp, url_prefix='/auth')  # Google OAuth has same prefix as regular auth
    app.register_blueprint(drivers_bp, url_prefix='/drivers')
    app.register_blueprint(passengers_bp, url_prefix='/passengers')
    app.register_blueprint(routes_bp, url_prefix='/routes')
    
    # Create tables if they don't exist
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# Context processor to make variables available to all templates
@app.context_processor
def inject_user():
    return dict(user=current_user)

# Context processor to make configuration available to all templates
@app.context_processor
def inject_config():
    return dict(config=app.config)
