CREATE TABLE cleaned_life_expectancy_2018 AS
(SELECT State,
    LEB AS LifeExpectancy,
    cast(split(life_expectancy_2018.Quartile,' - ')[1] AS decimal(4,2)) AS MinLifeExpectancyRange,
    cast(split(life_expectancy_2018.Quartile,' - ')[2] AS decimal(4,2)) AS MaxLifeExpectancyRange,
    SE AS LifeExpectancyStandardError
FROM life_expectancy_2018
WHERE Sex = 'Total' and State <> 'United States'
)
