{% set stocks = ["GOOG", "VMW", "APPL"] %}

create table agg_stocks as
select
    {% for stock in stocks %}
    sum(case when symbol = '{{stock}}' then price end) as {{stock}}_amount,
    {% endfor %}
    sum(price) as total_amount
from {{ raw_stocks }}
