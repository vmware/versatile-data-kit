CREATE TABLE cleaned_life_expectancy_2010_2015 AS
(SELECT State,
    LifeExpectancy,
    cast(split(life_expectancy_2010_2015.LifeExpectancyRange,'-')[1] AS decimal(4,2)) AS MinLifeExpectancyRange,
    cast(split(life_expectancy_2010_2015.LifeExpectancyRange,'-')[2] AS decimal(4,2)) AS MaxLifeExpectancyRange,
    LifeExpectancyStandardError
FROM life_expectancy_2010_2015
WHERE County = '(blank)'
)
