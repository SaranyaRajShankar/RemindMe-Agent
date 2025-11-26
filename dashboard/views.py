from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
import os
import json
import sqlite3
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from database import init_db, save_user_token, get_all_users

# Initialize database
init_db()

# Store OAuth state temporarily (in production, use Redis or database)
oauth_states = {}


def home(request):
    """Main dashboard page"""
    return render(request, 'index.html')


@require_http_methods(["GET"])
def get_users(request):
    """Get all registered users"""
    try:
        users = get_all_users()
        user_list = [{"email": email, "id": idx} for idx, (email, _) in enumerate(users, 1)]
        return JsonResponse({"users": user_list, "count": len(user_list)})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def start_auth(request):
    """Start OAuth flow"""
    try:
        client_secrets_file = settings.OAUTH_CLIENT_SECRETS_FILE
        if not os.path.exists(client_secrets_file):
            return JsonResponse(
                {"error": "OAuth credentials file not found. Please add oauthCredentials.json"},
                status=500
            )
        
        flow = Flow.from_client_secrets_file(
            client_secrets_file,
            scopes=settings.OAUTH_SCOPES,
            redirect_uri=settings.OAUTH_REDIRECT_URI
        )
        
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        
        # Store state temporarily
        oauth_states[state] = flow
        
        return JsonResponse({
            "auth_url": authorization_url,
            "state": state
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def auth_callback(request):
    """OAuth callback handler"""
    error = request.GET.get('error')
    code = request.GET.get('code')
    state = request.GET.get('state')
    
    if error:
        return render(request, 'error.html', {
            'error': f"Authentication failed: {error}"
        })
    
    if not code or not state:
        return render(request, 'error.html', {
            'error': "Missing authorization code or state"
        })
    
    if state not in oauth_states:
        return render(request, 'error.html', {
            'error': "Invalid state parameter"
        })
    
    try:
        flow = oauth_states[state]
        flow.fetch_token(code=code)
        creds = flow.credentials
        
        # Get user email
        service = build('oauth2', 'v2', credentials=creds)
        user_info = service.userinfo().get().execute()
        email = user_info.get('email', '')
        
        if not email:
            return render(request, 'error.html', {
                'error': "Could not retrieve user email"
            })
        
        # Save user token to database
        save_user_token(email, creds)
        
        # Clean up state
        del oauth_states[state]
        
        return render(request, 'success.html', {
            'email': email
        })
        
    except Exception as e:
        return render(request, 'error.html', {
            'error': f"Error during authentication: {str(e)}"
        })


@csrf_exempt
@require_http_methods(["DELETE"])
def delete_user(request, email):
    """Delete a user from the database"""
    try:
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE email=?", (email,))
        conn.commit()
        deleted = cursor.rowcount > 0
        conn.close()
        
        if not deleted:
            return JsonResponse({"error": "User not found"}, status=404)
        
        return JsonResponse({"message": f"User {email} deleted successfully"})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@require_http_methods(["GET"])
def health(request):
    """Health check endpoint"""
    return JsonResponse({"status": "healthy"})

