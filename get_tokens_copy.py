import time
import json

def get_tokens():
    # Wait for the user to authorize and the server to save token_data.json
    while True:
        try:
            with open('token_data.json', 'r') as f:
                token_data = json.load(f)
                break
        except FileNotFoundError:
            time.sleep(1)
    
    return token_data

if __name__ == '__main__':
    print("Please authorize the application in your web browser.")

    # Wait for the token data to be available
    tokens = get_tokens()

    # Print token information
    print("Access Token:", tokens.get('access_token'))
    print("Refresh Token:", tokens.get('refresh_token'))
    print("Expires In:", tokens.get('expires_in'))
    print("Token Type:", tokens.get('token_type'))