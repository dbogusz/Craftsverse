import subprocess
import time
import json
from datetime import datetime, timedelta
from enum import Enum
import etsyv3
from etsyv3 import EtsyAPI

# Define the SortOn and SortOrder enums based on documentation
class SortOn(Enum):
    CREATED = "created"
    PRICE = "price"
    UPDATED = "updated"
    SCORE = "score"

class SortOrder(Enum):
    ASC = "asc"
    ASCENDING = "ascending"
    DESC = "desc"
    DESCENDING = "descending"

def fetch_etsy_data(access_token, client_id, refresh_token, min_price, max_price, name = 'test.json', save = False):
    data = []
    total_count = []
    offset_division = []

    expires_in = datetime.now() + timedelta(hours=1)
    product_search = EtsyAPI(keystring=client_id, token=access_token, expiry=expires_in, refresh_token=refresh_token)

    min_price = min_price
    max_price = max_price
    test = product_search.find_all_listings_active(keywords='cosplay', sort_on=SortOn.CREATED,
                sort_order=SortOrder.DESC, min_price=min_price, max_price = max_price)

    total_count = int(test['count'])
    offset_division = int(total_count/100)

    if offset_division > 120:
        print("There are too many data points for the max offset: " + str(total_count))
    else:
        for i in range(0, offset_division):
            data.append(product_search.find_all_listings_active(keywords='cosplay', limit=100, offset=100*i, sort_on=SortOn.CREATED,
                    sort_order=SortOrder.DESC, min_price=min_price, max_price = max_price))
        
        if save == True:
            json.dump(data, open(str(name)+".json", 'w'))
            print('There were approximately ' + str(len(data[0]['results'])*offset_division) + ' data points collected and saved to file.')
        else: 
             print('There were approximately ' + str(len(data[0]['results'])*offset_division) + ' data points collected.')

def run_flask_app():
    return subprocess.Popen(['python', 'etsy_oauth.py'])

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
    # Start the Flask app
    flask_process = run_flask_app()

    print("Please authorize the application in your web browser.")

    # Wait for the token data to be available
    tokens = get_tokens()

    # Print token information
    print("Access Token:", tokens.get('access_token'))
    print("Refresh Token:", tokens.get('refresh_token'))
    print("Expires In:", tokens.get('expires_in'))
    print("Token Type:", tokens.get('token_type'))

    # Fetch data from Etsy
    access_token = tokens.get('access_token')
    refresh_token = tokens.get('refresh_token')
    client_id = '123' #Input your own client ID

    fetch_etsy_data(access_token, client_id, refresh_token, min_price = 3.0, max_price = 4.0, name = '', save = False)

    # Terminate the Flask server
    flask_process.terminate()