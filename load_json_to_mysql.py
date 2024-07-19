import mysql.connector
import json
import glob

# MySQL connection setup
conn = mysql.connector.connect(
    host='your_host',
    user='your_user',
    password='your_password',
    database='your_database'
)
cursor = conn.cursor()

# Get all files matching the pattern 'etsy_api_basic_p' followed by a number and ending in '.json'
file_pattern = 'etsy_api_basic_p*.json'
files = glob.glob(file_pattern)

# Loop through each file and read the data
for filename in files:
    with open(filename, 'r') as f:
        data = json.load(f)
        # Flatten the nested lists
        for item in data:
            for result in item['results']:
                # Prepare the data for insertion
                listing_id = result.get('listing_id')
                title = result.get('title')
                price_amount = result['price'].get('amount') if result.get('price') else None
                price_currency_code = result['price'].get('currency_code') if result.get('price') else None
                price_divisor = result['price'].get('divisor') if result.get('price') else None
                shop_id = result.get('shop_id')
                description = result.get('description')
                views = result.get('views')
                num_favorers = result.get('num_favorers')
                original_creation_timestamp = result.get('original_creation_timestamp')
                last_modified_timestamp = result.get('last_modified_timestamp')

                # Insert the data into MySQL
                cursor.execute('''
                    INSERT INTO listings (
                        listing_id, title, price_amount, price_currency_code, price_divisor, shop_id, description, views, num_favorers, original_creation_timestamp, last_modified_timestamp
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, FROM_UNIXTIME(%s), FROM_UNIXTIME(%s))
                    ON DUPLICATE KEY UPDATE
                        title=VALUES(title), price_amount=VALUES(price_amount), price_currency_code=VALUES(price_currency_code), price_divisor=VALUES(price_divisor),
                        shop_id=VALUES(shop_id), description=VALUES(description), views=VALUES(views), num_favorers=VALUES(num_favorers),
                        original_creation_timestamp=VALUES(original_creation_timestamp), last_modified_timestamp=VALUES(last_modified_timestamp)
                ''', (
                    listing_id, title, price_amount, price_currency_code, price_divisor, shop_id, description, views, num_favorers, original_creation_timestamp, last_modified_timestamp
                ))

# Commit the transaction
conn.commit()

# Close the connection
cursor.close()
conn.close()
