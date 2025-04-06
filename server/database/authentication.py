import os
from flask import Blueprint, request, jsonify
import google.oauth2.id_token
import google.auth.transport.requests

# Import DatabaseDriver, connection_params, and User from driver.py
from driver import DatabaseDriver, connection_params, User

# Create an instance of DatabaseDriver using your connection parameters.
db = DatabaseDriver(connection_params)

auth_bp = Blueprint('auth', __name__)

# Import the CLIENT_ID from environment variables.
CLIENT_ID = os.getenv('REACT_APP_GOOGLE_CLIENT_ID')

@auth_bp.route('/checkUser', methods=['POST'])
def check_user():
    # Step 1: Get the token from the request payload.
    data = request.get_json()
    token = data.get("token")
    
    if not token:
        return jsonify({"error": "Missing token"}), 400

    try:
        # Step 2: Verify the token with Google's OAuth utility.
        request_adapter = google.auth.transport.requests.Request()
        id_info = google.oauth2.id_token.verify_oauth2_token(token, request_adapter, CLIENT_ID)
        
        # Step 3: Extract user information from the token.
        email = id_info.get("email")
        given_name = id_info.get("given_name")
        family_name = id_info.get("family_name")
        full_name = id_info.get("name")  # Full name (if available)
        
        if not email:
            return jsonify({"error": "Email not found in token"}), 400

        # Debug log
        print("User Info from Google:", given_name, family_name, email)
        
        # Step 4: Query the database using your provided method.
        user = db.get_user_by_email(email)
        if user:
            # User exists: return user details along with Google info.
            return jsonify({
                "exists": True,
                "user": {
                    "id": user.id,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "phone_number": user.phone_number,
                    "is_verified": user.is_verified
                },
                "google_info": {
                    "given_name": given_name,
                    "family_name": family_name,
                    "email": email,
                    "full_name": full_name
                }
            })
        else:
            # User does not exist: return Google info to assist with registration.
            return jsonify({
                "exists": False,
                "google_info": {
                    "given_name": given_name,
                    "family_name": family_name,
                    "email": email,
                    "full_name": full_name
                }
            })
    except Exception as e:
        print("Error verifying token:", e)
        return jsonify({"error": "Invalid token"}), 401
