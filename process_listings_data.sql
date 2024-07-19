-- Remove non-active listings (if 'state' column exists)
DELETE FROM listings WHERE state != 'active';

-- Count listings with style value
SELECT COUNT(*) FROM listings WHERE JSON_LENGTH(style) > 0;

-- Check for missing values
SELECT COUNT(*) FROM listings WHERE
    title IS NULL OR
    price_amount IS NULL OR
    price_currency_code IS NULL OR
    shop_id IS NULL OR
    description IS NULL OR
    views IS NULL OR
    num_favorers IS NULL OR
    original_creation_timestamp IS NULL OR
    last_modified_timestamp IS NULL;

-- Remove duplicates based on listing_id
DELETE FROM listings
WHERE listing_id IN (
    SELECT listing_id
    FROM (
        SELECT listing_id,
               ROW_NUMBER() OVER (PARTITION BY listing_id ORDER BY listing_id) AS row_num
        FROM listings
    ) AS temp
    WHERE temp.row_num > 1
);

-- Check for duplicates based on specific columns and remove them
DELETE FROM listings
WHERE (title, price_amount, shop_id, description, views, num_favorers) IN (
    SELECT title, price_amount, shop_id, description, views, num_favorers
    FROM (
        SELECT title, price_amount, shop_id, description, views, num_favorers,
               ROW_NUMBER() OVER (PARTITION BY title, price_amount, shop_id, description, views, num_favorers ORDER BY listing_id) AS row_num
        FROM listings
    ) AS temp
    WHERE temp.row_num > 1
);

-- List of unique listing_ids
SELECT listing_id INTO OUTFILE '/path/to/listing_ids_cleaned.json'
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
FROM listings;

-- Update timestamps and calculate additional fields
UPDATE listings
SET original_creation_timestamp = FROM_UNIXTIME(original_creation_timestamp),
    last_modified_timestamp = FROM_UNIXTIME(last_modified_timestamp),
    days_active = DATEDIFF(CURDATE(), FROM_UNIXTIME(original_creation_timestamp)),
    days_since_last_modified = DATEDIFF(CURDATE(), FROM_UNIXTIME(last_modified_timestamp));

-- Handle currency conversion

CREATE TABLE currency_rates (
    currency_code VARCHAR(10) PRIMARY KEY,
    rate_to_gbp DECIMAL(10, 6)
);

-- Insert custom rates
INSERT INTO currency_rates (currency_code, rate_to_gbp) VALUES
('USD', 0.77,
('EUR', 0.84),
('DKK', 0.11),
('SEK', 0.072),
('AUD', 0.52),
('TRY', 0.023),
('CAD', 0.56),
('HKD', 0.099),
('PHP', 0.013),
('NOK', 0.071),
('CHF', 0.87),
('INR', 0.0092),
('MYR', 0.17),
('NZD', 0.47),
('ZAR', 0.042),
('ILS', 0.21),
('SGD', 0.57),
('IDR', 0.000048),
('MXN', 0.043),
('PLN', 0.20),
('TWD', 0.024),
('VND', 0.00003),
('MAD', 0.079);

-- Update price amounts based on currency conversion
UPDATE listings l
JOIN currency_rates cr ON l.price_currency_code = cr.currency_code
SET l.price_amount = CASE
    WHEN l.price_currency_code != 'GBP' THEN l.price_amount * cr.rate_to_gbp / l.price_divisor
    ELSE l.price_amount / l.price_divisor
END,
l.exchanged = CASE
    WHEN l.price_currency_code != 'GBP' THEN 'yes'
    ELSE 'no'
END;