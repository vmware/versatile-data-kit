CREATE TABLE merged_tables AS
(SELECT Year,
    (Price / (SELECT max(Price) FROM average_gas_price_by_year)) AS NormPrice,
    (MuchAboveNormal / (SELECT max(MuchAboveNormal) FROM climate_extremes_index
 WHERE CAST(climate_extremes_index.Date AS integer) IN (SELECT Year from average_gas_price_by_year)
    )) AS NormTemperatureMuchAboveNormal,
    (MuchBelowNormal / (SELECT max(MuchBelowNormal) FROM climate_extremes_index WHERE CAST(climate_extremes_index.Date AS integer) IN (SELECT Year from average_gas_price_by_year)
    )) AS NormTemperatureMuchBelowNormal
FROM average_gas_price_by_year INNER JOIN climate_extremes_index
ON average_gas_price_by_year.Year = CAST(climate_extremes_index.Date AS integer)
)
