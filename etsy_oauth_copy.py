import requests
import pkce
import webbrowser
from flask import Flask, request, jsonify, redirect
import json
import subprocess

# Configuration
client_id = 'i123' #Input your own client ID
redirect_uri = 'http://localhost:5000/callback' #Change for your redirect URI
scope = 'listings_r'
state = 'some_random_string'

# Generate code verifier and code challenge
code_verifier = pkce.generate_code_verifier(length=128)
code_challenge = pkce.get_code_challenge(code_verifier)

# Save code_verifier to a file
with open('code_verifier.txt', 'w') as f:
    f.write(code_verifier)

# Construct the authorization URL
auth_url = (
    f"https://www.etsy.com/oauth/connect?response_type=code&client_id={client_id}"
    f"&redirect_uri={redirect_uri}&scope={scope}&state={state}"
    f"&code_challenge={code_challenge}&code_challenge_method=S256"
)

# Create Flask app
app = Flask(__name__)

@app.route('/')
def index():
    return redirect(auth_url)

@app.route('/callback')
def callback():
    auth_code = request.args.get('code')
    received_state = request.args.get('state')

    if received_state != state:
        return "State mismatch error", 400

    # Exchange authorization code for access token
    token_data = exchange_code_for_token(auth_code)
    
    if token_data is None:
        return "Failed to get access token", 400

    # Save token data to a file
    with open('token_data.json', 'w') as f:
        f.write(json.dumps(token_data))

    return jsonify(token_data)

def exchange_code_for_token(auth_code):
    token_url = 'https://api.etsy.com/v3/public/oauth/token'
    
    # Read the code_verifier from the file
    with open('code_verifier.txt', 'r') as f:
        code_verifier = f.read()
    
    data = {
        'grant_type': 'authorization_code',
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'code': auth_code,
        'code_verifier': code_verifier,
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.post(token_url, data=data, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        return None

if __name__ == '__main__':
    webbrowser.open('http://localhost:5000')
    app.run(debug=True)