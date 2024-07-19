CREATE TABLE listings (
    listing_id BIGINT PRIMARY KEY,
    title VARCHAR(255),
    price_amount DECIMAL(10, 2),
    price_currency_code VARCHAR(10),
    price_divisor INT,
    shop_id BIGINT,
    description TEXT,
    views INT,
    num_favorers INT,
    original_creation_timestamp TIMESTAMP,
    last_modified_timestamp TIMESTAMP,
    exchanged VARCHAR(10)
);