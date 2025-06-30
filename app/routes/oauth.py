from flask import Blueprint, request, redirect, jsonify
import requests
import os

oauth_bp = Blueprint('oauth', __name__)

CLIENT_ID = os.environ['GOOGLE_OAUTH_CLIENT_ID']
CLIENT_SECRET = os.environ['GOOGLE_OAUTH_CLIENT_SECRET']
REDIRECT_URI = os.environ['OAUTH_REDIRECT_URI']

@oauth_bp.route('/oauth2/auth')
def oauth_authorize():
    google_auth_url = (
        'https://accounts.google.com/o/oauth2/v2/auth'
        '?response_type=code'
        f'&client_id={CLIENT_ID}'
        f'&redirect_uri={REDIRECT_URI}'
        '&scope=https://www.googleapis.com/auth/spreadsheets'
    )
    return redirect(google_auth_url)

@oauth_bp.route('/oauth2/token', methods=['POST'])
def oauth_token():
    code = request.form.get('code')
    token_resp = requests.post('https://oauth2.googleapis.com/token', data={
        'code': code,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI,
        'grant_type': 'authorization_code'
    })
    return jsonify(token_resp.json()), token_resp.status_code
