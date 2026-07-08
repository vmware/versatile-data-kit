CREATE TABLE daily_revenue AS
SELECT
    order_date,
    SUM(quantity * unit_price) AS revenue
FROM raw_orders
WHERE status = 'PAID'
GROUP BY order_date;
