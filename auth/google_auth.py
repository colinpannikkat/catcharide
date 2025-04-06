import json
import os
import logging
import requests
from flask import Blueprint, redirect, request, url_for, flash, session, current_app
from flask_login import login_user, logout_user, login_required
from oauthlib.oauth2 import WebApplicationClient
from app import db
from models import User

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Google OAuth configuration
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_OAUTH_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET")
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

# OAuth client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)

# Blueprint definition
google_auth_bp = Blueprint('google_auth', __name__)

@google_auth_bp.route('/google_login')
def google_login():
    """
    Redirect user to Google's OAuth 2.0 authorization endpoint.
    """
    try:
        # Find out what URL to hit for Google login
        google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
        authorization_endpoint = google_provider_cfg["authorization_endpoint"]

        # Use the library to construct the request for Google login and provide
        # scopes that let you retrieve user's profile from Google
        request_uri = client.prepare_request_uri(
            authorization_endpoint,
            # Replacing http:// with https:// is important as the external
            # protocol must be https to match the URI whitelisted in Google Console
            redirect_uri=request.base_url.replace("http://", "https://") + "/callback",
            scope=["openid", "email", "profile"],
        )
        return redirect(request_uri)
    except Exception as e:
        logger.error(f"Error in Google login process: {str(e)}")
        flash("An error occurred during Google authentication. Please try again.", "danger")
        return redirect(url_for("auth.login"))

@google_auth_bp.route('/google_login/callback')
def callback():
    """
    Handle the OAuth 2.0 callback from Google and login or register user.
    """
    try:
        # Get authorization code Google sent back
        code = request.args.get("code")
        
        # If there's no code, something went wrong
        if not code:
            flash("Authentication failed. Please try again.", "danger")
            return redirect(url_for("auth.login"))

        # Find out what URL to hit to get tokens
        google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
        token_endpoint = google_provider_cfg["token_endpoint"]

        # Prepare and send request to get tokens
        token_url, headers, body = client.prepare_token_request(
            token_endpoint,
            # Replacing http:// with https:// is important as the external
            # protocol must be https to match the URI whitelisted
            authorization_response=request.url.replace("http://", "https://"),
            redirect_url=request.base_url.replace("http://", "https://"),
            code=code,
        )
        
        # Make sure the client id and secret are not None
        if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
            logger.error("Missing Google OAuth client credentials")
            flash("Google authentication is not properly configured.", "danger")
            return redirect(url_for("auth.login"))
            
        token_response = requests.post(
            token_url,
            headers=headers,
            data=body,
            auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
        )

        # Parse the tokens
        client.parse_request_body_response(json.dumps(token_response.json()))

        # Get user info from Google
        userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
        uri, headers, body = client.add_token(userinfo_endpoint)
        userinfo_response = requests.get(uri, headers=headers, data=body)
        
        userinfo = userinfo_response.json()
        
        # Verify user's email
        if not userinfo.get("email_verified"):
            flash("User email not verified by Google.", "danger")
            return redirect(url_for("auth.login"))
        
        # Get user data
        user_email = userinfo["email"]
        user_name = userinfo.get("given_name", "")
        user_last_name = userinfo.get("family_name", "")
        
        # Check if user exists in database
        user = User.query.filter_by(email=user_email).first()
        
        # If user doesn't exist, create a new account
        if not user:
            # Create a new user
            user = User(
                first_name=user_name,
                last_name=user_last_name,
                email=user_email,
                phone_number=f"google_{userinfo.get('sub', '')[:10]}",  # Use part of Google ID as a placeholder
                is_verified=True  # Mark as verified since Google verified the email
            )
            
            # Generate a random password for the user
            import secrets
            random_password = secrets.token_urlsafe(16)
            user.set_password(random_password)
            
            # Save user to database
            db.session.add(user)
            db.session.commit()
            flash("Your account has been created with Google. Please update your phone number in profile settings.", "info")
        else:
            flash("Login successful via Google!", "success")
        
        # Log in the user
        login_user(user)
        
        # Redirect to next page or home
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('index')
        
        return redirect(next_page)
        
    except Exception as e:
        logger.error(f"Error in Google callback process: {str(e)}")
        flash("An error occurred during Google authentication. Please try again.", "danger")
        return redirect(url_for("auth.login"))