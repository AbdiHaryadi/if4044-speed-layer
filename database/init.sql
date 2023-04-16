CREATE TABLE IF NOT EXISTS socmed_aggs_socmedaggs (
    social_media VARCHAR(16) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    count INT,
    unique_count INT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    PRIMARY KEY (social_media, timestamp)
);