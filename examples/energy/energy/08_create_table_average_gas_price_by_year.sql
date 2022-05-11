CREATE TABLE average_gas_price_by_year AS
(SELECT extract(YEAR from CAST(Date AS date)) AS Year,
    avg(Price) AS Price
FROM natural_gas_prices
GROUP BY extract(YEAR from CAST(Date AS date))
)
