# Energy
The objective of this scenario is to build an app that shows the relationship between Natural Gas prices in the U.S. and the temperature.
The app uses VDK to ingest and process the following two CSV datasets:
* [Natural Gas Prices from 1997 to 2020](https://datahub.io/core/natural-gas)
* [U.S. Climate Extremes Index from 1910 to 2020](https://www.ncdc.noaa.gov/extremes/cei/graph/ne/01-12/2)


This example provides the complete code to perform the following tasks:

* Data Ingestion from CSV
* Data Processing
* Data Publication in form of an innteractive App

The directory is organized as follows:

* energy - contains jobs
* dashboard.py - contains the code to generate the app

## Scenario
An American natural gas supplier has hired a team of data scientists to find out if there is a correlation between price trends and climatic conditions (minimum temperatures).
Analysts found two datasets:
* [Natural Gas Prices from 1997 to 2020](https://datahub.io/core/natural-gas)
* [U.S. Climate Extremes Index from 1910 to 2020](https://www.ncdc.noaa.gov/extremes/cei/graph/ne/01-12/2)


## Data Source

The Natural Gas Prices dataset contains 5,953 records, provided by the U.S. Energy Information Administration(EIA). Each record contains the daily price of natural gas.
For each record, the following information is available:
* Date (provided on a daily basis)
* Price (in dollars)

The following table shows an excerpt of the dataset:
| Date       | Price                                                 |
| ---------- | ----------------------------------------------------- |
| 1997-01-07 | 3.819999999999999840127884453977458178997039794921875 |
| 1997-01-08 | 3.79999999999999982236431605997495353221893310546875  |
| 1997-01-09 | 3.609999999999999875655021241982467472553253173828125 |
| 1997-01-10 | 3.9199999999999999289457264239899814128875732421875   |
| 1997-01-13 | 4                                                     |
| 1997-01-14 | 4.0099999999999997868371792719699442386627197265625   |
| 1997-01-15 | 4.339999999999999857891452847979962825775146484375    |
| 1997-01-16 | 4.70999999999999996447286321199499070644378662109375  |
| 1997-01-17 | 3.910000000000000142108547152020037174224853515625    |
| 1997-01-20 | 3.2599999999999997868371792719699442386627197265625   |
| 1997-01-21 | 2.9900000000000002131628207280300557613372802734375   |

The U.S. Climate Extremes Index dataset contains 112 records. For each record, many parameters can be downloaded. Data Analysts select the following information:
* Date (provided on an annual basis)
* Percentage of minimum temperature much above normal
* Percentage of minimum temperature much below normal.

The following table shows an excerpt of the dataset:

| **Date** | Much Above Normal | Much Below Normal |
| -------- | ----------------- | ----------------- |
| **1910** | 0.00              | 3.90              |
| **1911** | 3.70              | 7.60              |
| **1912** | 0.00              | 52.80             |
| **1913** | 1.50              | 0.00              |
| **1914** | 0.00              | 79.40             |
| **1915** | 0.00              | 0.10              |
| **1916** | 0.00              | 18.40             |
| **1917** | 0.00              | 99.70             |
| **1918** | 0.00              | 45.40             |
| **1919** | 0.00              | 0.00              |

## Requirements

To run this example, you need:

* Versatile Data Kit
* Trino DB
* Versatile Data Kit plugin for Trino
* Streamlit

For more details on how to install Versatile Data Kit, Trino DB, Streamlit and Versatile Data Kit plugin for Trino, please refer to [this link](https://github.com/vmware/versatile-data-kit/tree/main/examples/life-expectancy).

### Other Requirements
This example also requires the following Python libraries, which are included in the requirement.txt file:
```
pandas
```

## Configuration
The following example uses the same configuration as the [Life Expectancy](https://github.com/vmware/versatile-data-kit/tree/main/examples/life-expectancy) scenario, with the only difference on the trino schema used by the Versatile Data Kit configuration file:
```
trino_schema = energy
```

## Data Ingestion
Data Ingestion uploads in the database output of CSV files, defined in the Data Source section. Data Ingestion is performed through the following steps:

* delete the existing table (if any)
* create a new table
* ingest table values directly from the CSV.

To access the CSV file, this example requires an active Internet connection to work properly.

Jobs 01-03 are devoted to Data Ingestion of the Natural Gas Prices dataset. The output of the CSV file is imported in a tables, named `nataural_gas_prices`.

Jobs 04-06 are devoted to Data Ingestion of the U.S. Climate Extremes Index dataset. The output of the CSV file is imported in a tables, named `climate_extremes_index`.

## Data Processing
Data Processing includes two steps:
* building an annual view of the `natural_gas_prices` with the average value of natural gas price
* merging the two tables, the previous one and `climate_extremes_index`. Values are normalized in the interval [0,1] thus making possible a comparison among them.

Jobs 07-08 are devoted to the first step. The produced output is stored in a table, called `average_gas_price_by_year`.

The following table shows an example of the produced table:

| **Year** | **Price**          |
| -------- | ------------------ |
| **2002** | 3.3756000000000026 |
| **2010** | 4.369722222222219  |
| **2017** | 2.9880308880308877 |
| **2018** | 3.152661290322578  |
| **2006** | 6.731244979919681  |
| **2011** | 3.9963095238095225 |
| **1998** | 2.0883665338645407 |
| **2008** | 8.862529644268777  |
| **2009** | 3.942658730158732  |
| **2012** | 2.7544841269841265 |

Jobs 09-10 are devoted to the second step. The produced output is stored in a table, called `merged_tables`.

The following table shows an example of the produced table:

| **Year** | **NormPrice**       | **NormTemperatureMuchAboveNormal** | **NormTemperatureMuchBelowNormal** |
| -------- | ------------------- | ---------------------------------- | ---------------------------------- |
| **2002** | 0.38088448055944574 | 0.054384017758046625               | 0                                  |
| **2010** | 0.4930558652684487  | 0.12430632630410655                | 0.14666666666666667                |
| **2017** | 0.3371532742870077  | 0.8213096559378469                 | 0                                  |
| **2018** | 0.355729280111502   | 0.48834628190899004                | 0                                  |
| **2006** | 0.7595173443817639  | 0.43396226415094347                | 0                                  |
| **2011** | 0.45092199227721136 | 0.1598224195338513                 | 0.013333333333333334               |
| **1998** | 0.2356400054712422  | 0.8135405105438402                 | 0                                  |
| **2008** | 1                   | 0.0033296337402885685              | 0.04                               |
| **2009** | 0.4448683263596609  | 0.006659267480577137               | 0                                  |
| **2012** | 0.31080111859094284 | 0.8867924528301888                 | 0                                  |

## Data Publication
The `dashboard.py` script contains an app on the Online Exhibition, showing the preview of all the artworks contained in the database. To run the app, simply run the following command:
```
streamlit run dashboard.py
```
