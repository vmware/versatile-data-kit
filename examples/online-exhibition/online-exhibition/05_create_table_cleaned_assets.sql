CREATE TABLE cleaned_assets AS (
    SELECT
        SUBSTRING(country, 3, LENGTH(country)-4) AS country,
        SUBSTRING(edmPreview, 3, LENGTH(edmPreview)-4) AS edmPreview,
        SUBSTRING(provider, 3, LENGTH(provider)-4) AS provider,
        SUBSTRING(title, 3, LENGTH(title)-4) AS title,
        SUBSTRING(rights, 3, LENGTH(rights)-4) AS rights
    FROM assets
)
