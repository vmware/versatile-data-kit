CREATE TABLE merged_life_expectancy AS
(SELECT us_regions.State,
    LifeExpectancy,
    MinLifeExpectancyRange,
    MaxLifeExpectancyRange,
    '2010-2015' AS Period,
    Region,
    0 AS GDP
FROM
    cleaned_life_expectancy_2010_2015 JOIN us_regions ON us_regions.State = cleaned_life_expectancy_2010_2015.State
)
UNION
(SELECT us_regions.State,
    LifeExpectancy,
    MinLifeExpectancyRange,
    MaxLifeExpectancyRange,
    '2018' AS Period,
    Region,
    Year2018 AS GDP
FROM cleaned_life_expectancy_2018
    JOIN us_regions ON us_regions.State = cleaned_life_expectancy_2018.State
    INNER JOIN us_gdp ON us_gdp.County = cleaned_life_expectancy_2018.State
WHERE Year2018 > 100000000
)
