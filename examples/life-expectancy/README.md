# Life Expectancy
This example provides the complete code to perform the following tasks:
- Data Ingestion from CSV
- Data Processing
- Data Publication in form of Visual Report/Dashboard

The directory is organized as follows:
* **life-expectancy** - contains jobs
* **resources** - contains some additional files used by the dashboard
* `dashboard.py` - contains the code to generate the dashboard

## Scenario

Researchers from the Department of Population History and Social Structure have to conduct a study on the life expectancy of Americans. The objective of the study is to understand over time which American states have the greatest life expectancy.

## Data Sources
After extensive research, the researchers found two main datasets, both of which are available as CSV files:

- [U.S. Life Expectancy at Birth by State and Census Tract - 2010-2015](https://catalog.data.gov/dataset/u-s-life-expectancy-at-birth-by-state-and-census-tract-2010-2015)
- [U.S. State Life Expectancy by Sex, 2018](https://catalog.data.gov/dataset/u-s-state-life-expectancy-by-sex-2018)

In addition to the previous datasets, the researchers found the following additional datasets:
- [U.S. Gross Domestic Product by County](https://www.bea.gov/data/gdp/gdp-county-metro-and-other-areas)
- [U.S. Census Bureau Regions and Divisions](https://raw.githubusercontent.com/cphalpert/census-regions/master/us%20census%20bureau%20regions%20and%20divisions.csv)

The dataset **U.S. Life Expectancy at Birth by State and Census Tract - 2010-2015** contains 73,121 records relating to the life expectancy of Americans, divided by state and county and relating to the period 2010-2015. For each record, the following information is available:

- State
- County
- Census Tract Number
- Life Expectancy
- Life Expectancy Range
- Life Expectancy Standard Error

For some records, some fields are missing.

The following table shows an excerpt from the dataset:

| **State** | **County** | **Census Tract Number** | **Life Expectancy** | **Life Expectancy Range** | **Life Expectancy Standard Error** |
| --- | --- | --- | --- | --- | --- |
| **Alabama** | (blank) | | 75.5 | 75.2-77.5 | 0.0328 |
| **Alabama** | Autauga County, AL | 0201.00 | 73.1 | 56.9-75.1 | 2.2348 |
| **Alabama** | Autauga County, AL | 0202.00 | 76.9 | 75.2-77.5 | 3.3453 |
| **Alabama** | Autauga County, AL | 0203.00 | | | |
| **Alabama** | Autauga County, AL | 0204.00 | 75.4 | 75.2-77.5 | 1.0216 |
| **Alabama** | Autauga County, AL | 0205.00 | 79.4 | 77.6-79.5 | 1.1768 |
| **Alabama** | Autauga County, AL | 0206.00 | 73.1 | 56.9-75.1 | 1.5519 |
| **Alabama** | Autauga County, AL | 0207.00 | | |  |
| **Alabama** | Autauga County, AL | 0208.01 | 78.3 | 77.6-79.5 | 2.3861 |
| **Alabama** | Autauga County, AL | 0208.02 | 76.9 | 75.2-77.5 | 1.2628 |
| **Alabama** | Autauga County, AL | 0209.00 | 73.9 | 56.9-75.1 | 1.5923 |

The dataset **U.S. State Life Expectancy by Sex, 2018** contains 156 records relating to the life expectancy of Americans in 2018, divided by state and sex (male, female, total). For each record, the following information is available:

- State
- Sex
- LEB - Life Expectancy at birth
- SE - Life Expectancy Standard Error
- Quartile - Life Expectancy Range

The following table shows an excerpt from the dataset:

| **State** | **Sex** | **LEB** | **SE** | **Quartile** |
| --- | --- | --- | --- | --- |
| **United States** | Total | 78.7 | | \* |
| **West Virginia** | Total | 74.4 | 114 | 74.4 - 77.2 |
| **Mississippi** | Total | 74.6 | 88 | 74.4 - 77.2 |
| **Alabama** | Total | 75.1 | 67 | 74.4 - 77.2 |
| **Kentucky** | Total | 75.3 | 68 | 74.4 - 77.2 |
| **Tennessee** | Total | 75.5 | 57 | 74.4 - 77.2 |
| **Arkansas** | Total | 75.6 | 86 | 74.4 - 77.2 |
| **Oklahoma** | Total | 75.6 | 73 | 74.4 - 77.2 |

The dataset **U.S. Gross Domestic Product by County** contains 3,163 records, related to the U.S. real Gross Domestic Product, by County, referring to the period years 2017–2020.
The dataset contains many columns. For each record, the following information is extracted:
- County
- 2017
- 2018
- 2019
- 2020

The following table shows an excerpt from the dataset:

| **County**        | **2017** | **2018** | **2019** | **2020** |
| ----------------- | ------------ | ------------ | ------------ | ------------ |
| **United States** | 18079084000  | 18606787000  | 19032672000  | 18384687000  |
| **Alabama**       | 197566622    | 200800889    | 203383898    | 196906061    |
| **Autauga**       | 1587695      | 1602077      | 1540762      | 1520973      |
| **Baldwin**       | 6453588      | 6799715      | 7134734      | 6985901      |
| **Barbour**       | 721125       | 730518       | 729105       | 687074       |
| **Bibb**          | 353234       | 353016       | 380453       | 388330       |
| **Blount**        | 920401       | 967135       | 932215       | 881874       |
| **Bullock**       | 225304       | 235358       | 247229       | 250385       |
| **Butler**        | 584855       | 609244       | 615641       | 574717       |

The dataset **U.S. Census Bureau Regions and Divisions** contains 51 records related to mapping between each U.S. County and its Region. For each record, the following information is extracted:
- State
- State Code
- Region
- Division

The following table shows an excerpt from the dataset:

| **State**                | **StateCode** | **Region** | **Division**       |
| ------------------------ | ------------- | ---------- | ------------------ |
| **Alaska**               | AK            | West       | Pacific            |
| **Alabama**              | AL            | South      | East South Central |
| **Arkansas**             | AR            | South      | West South Central |
| **Arizona**              | AZ            | West       | Mountain           |
| **California**           | CA            | West       | Pacific            |
| **Colorado**             | CO            | West       | Mountain           |
| **Connecticut**          | CT            | Northeast  | New England        |
| **District of Columbia** | DC            | South      | South Atlantic     |
| **Delaware**             | DE            | South      | South Atlantic     |

## Requirements
To run this example, you need:
* Versatile Data Kit
* Trino DB
* Versatile Data Kit plugin for Trino
* Streamlit

### Versatile Data Kit
If you have not done so already, you can install Versatile Data Kit and the plugins required for this example by running the following commands from a terminal:

```
pip install quickstart-vdk
```

Note that Versatile Data Kit requires Python 3.7+. See the [Installation Page](https://github.com/vmware/versatile-data-kit/wiki/Installation#install-sdk "Installation page") for more details.

### Trino DB
This example also requires Trino DB installed. See the Trino [Official Documentation](https://trino.io/ "Official Documentation") for more details about installation.

### Versatile Data Kit Plugin for Trino
Since this example requires Trino, you should also install the Versatile Data Kit plugin for Trino:

```
pip install vdk-trino
```

See the vdk-trino [Documentation Page](https://github.com/vmware/versatile-data-kit/tree/main/projects/vdk-plugins/vdk-trino) for more details.

### Streamlit
The final dashboard/report is built in [streamlit](https://streamlit.io/).
You can install streamlit through the following command:

```
pip install streamlit
```

See the streamlit [Documentation Page](https://docs.streamlit.io/library/get-started/installation) for more details.

### Other Requirements
This example also requires the following Python libraries, which are included in the `requirement.txt` file:

```
inspect
math
numpy
openpyxl
pandas
```

The following Python libraries are required by the dashboard:
```
altair
```

## Configuration

### Trino DB
In this example Trino is running locally, with the following minimal `config.properties` configuration file:

```
coordinator=true
node-scheduler.include-coordinator=true
http-server.http.port=8080
query.max-memory=5GB
query.max-memory-per-node=1GB
query.max-total-memory-per-node=2GB
discovery.uri=http://127.0.0.1:8080
http-server.https.enabled=false

```

In addition, the Trino DB exploits the MySQL catalog, with the following configuration (file `mysql.properties` located in the catalog folder of the Trino server:

```
connector.name=mysql
connection-url=jdbc:mysql://localhost:3306
connection-user=root
connection-password=
allow-drop-table=true
```

More complex configurations can be used too.

Finally, this example assumes that an empty schema, called `life-expectancy` exists on the MySQL server.

### Versatile Data Kit
The Life Expectancy Data Job runs with the following configuration (`config.ini`):

```
db_default_type=TRINO
ingest_method_default = trino
trino_catalog = mysql
trino_use_ssl =
trino_host = localhost
trino_port = 8080
trino_user = root
trino_schema = life-expectancy
trino_ssl_verify =
```

## Data Ingestion
Data Ingestion uploads in the database the two CSV tables, defined in the Data Source section. For each table, data Ingestion is performed through the following steps:
* delete the existing table (if any)
* create a new table
* ingest table values directly from the CSV file.

The path to the CSV file is specified as a URL, thus this example requires an active Internet connection to work properly.

Jobs from 01 to 12 are devoted to Data Ingestion:
* 01 - 03 ingest data in table `life_expectancy_2010_2015`
* 04 - 06 ingest data in table `life_expectancy_2018`
* 07 - 09 ingest data in table `us_regions`
* 10 - 12 ingest data in table `us_gdp`
## Data Processing
Data Processing includes the following tasks:
* Clean tables
* Merge the cleaned tables

### Clean tables
Table cleaning includes jobs from 13 to 18.

**Tasks 13 - 14**
Cleaning the `life_expectancy_2010_2015` table includes the following two operations:
* group records by County
* split the column `LifeExpectancyRange` in two decimal columns `MinLifeExpectancyRange` and `MaxLifeExpectancyRange`.

The output of the cleaning process for the `life_expectancy_2010_2015` table is stored in a new table, called `cleaned_life_expectancy_2010_2015`.

The following table shows an example of the `cleaned_life_expectancy_2010_2015` table:

| **State**                | **LifeExpectancy** | **MinLifeExpectancyRange** | **MaxLifeExpectancyRange** | **LifeExpectancyStandardError** |
| ------------------------ | ------------------ | -------------------------- | -------------------------- | ------------------------------- |
| **Alabama**              | 75.50              | 75.20                      | 77.50                      | 0.03                            |
| **Alaska**               | 78.80              | 77.60                      | 79.50                      | 0.10                            |
| **Arizona**              | 79.90              | 79.60                      | 81.60                      | 0.03                            |
| **Arkansas**             | 76.00              | 75.20                      | 77.50                      | 0.04                            |
| **California**           | 81.30              | 79.60                      | 81.60                      | 0.01                            |
| **Colorado**             | 80.50              | 79.60                      | 81.60                      | 0.03                            |
| **Connecticut**          | 80.90              | 79.60                      | 81.60                      | 0.04                            |
| **Delaware**             | 78.70              | 77.60                      | 79.50                      | 0.08                            |
| **District of Columbia** | 78.50              | 77.60                      | 79.50                      | 0.10                            |
| **Florida**              | 80.10              | 79.60                      | 81.60                      | 0.02                            |

**Tasks 15 - 16**
Cleaning the `life_expectancy_2018` table includes the following operations:
* rename column `LEB` to `LifeExpectancy`
* rename column `SE` to `LifeExpectancyStandardError`
* split the column `Quartile` in two decimal columns `MinLifeExpectancyRange` and `MaxLifeExpectancyRange`
* select only rows with `Sex = 'Total'`.

The following table shows an example of the `cleaned_life_expectancy_2018` table:

| **State**          | **LifeExpectancy** | **MinLifeExpectancyRange** | **MaxLifeExpectancyRange** | **LifeExpectancyStandardError** |
| ------------------ | ------------------ | -------------------------- | -------------------------- | ------------------------------- |
| **West Virginia**  | 74.4               | 74.40                      | 77.20                      | 0.1                             |
| **Mississippi**    | 74.6               | 74.40                      | 77.20                      | 0.1                             |
| **Alabama**        | 75.1               | 74.40                      | 77.20                      | 0.1                             |
| **Kentucky**       | 75.3               | 74.40                      | 77.20                      | 0.1                             |
| **Tennessee**      | 75.5               | 74.40                      | 77.20                      | 0.1                             |
| **Arkansas**       | 75.6               | 74.40                      | 77.20                      | 0.1                             |
| **Oklahoma**       | 75.6               | 74.40                      | 77.20                      | 0.1                             |
| **Louisiana**      | 75.6               | 74.40                      | 77.20                      | 0.1                             |
| **South Carolina** | 76.5               | 74.40                      | 77.20                      | 0.1                             |
| **Missouri**       | 76.6               | 74.40                      | 77.20                      | 0.1                             |

### Merge the cleaned tables
Jobs 17 and 18 are devoted to vertical merging between the two cleaned datasets `cleaned_life_expectancy_2010_2015`, `cleaned_life_expectancy_2018`, `us_gdp` and `us_regions`. Vertical merging means that the second dataset is appended to the first dataset and three new columns, called `Period`, `GDP` and `Region`, are added to the resulting table, named `merged_life_expectancy`.
The `GDP` attribute is set only for records with `Period = '2018'`. For the other records, it is set to `0`, since it is not available.

The following table shows an example of the `merged_life_expectancy` table:

| **State**       | **LifeExpectancy** | **MinlifeExpectancyRange** | **MaxLifeExpectancyRange** | **Period** | **Region** | **GDP**   |
| --------------- | ------------------ | -------------------------- | -------------------------- | ---------- | ---------- | --------- |
| **Oklahoma**    | 75.60              | 74.40                      | 77.20                      | 2018       | South      | 197358323 |
| **Connecticut** | 80.90              | 79.60                      | 81.60                      | 2010-2015  | Northeast  | 0         |
| **Michigan**    | 78.20              | 77.60                      | 79.50                      | 2010-2015  | Midwest    | 0         |
| **Mississippi** | 74.90              | 56.90                      | 75.10                      | 2010-2015  | South      | 0         |
| **Nebraska**    | 79.60              | 79.60                      | 81.60                      | 2010-2015  | Midwest    | 0         |
| **Virginia**    | 79.00              | 78.70                      | 79.30                      | 2018       | South      | 477819754 |
| **Alaska**      | 78.80              | 77.60                      | 79.50                      | 2010-2015  | West       | 0         |
| **California**  | 81.30              | 79.60                      | 81.60                      | 2010-2015  | West       | 0         |
| **Ohio**        | 77.60              | 77.60                      | 79.50                      | 2010-2015  | Midwest    | 0         |

## Data Publication
The `dashboard.py` script contains a dashboard/report on the Life Expectancy.
To run the report, simply run the following command:

```
streamlit run dashboard.py
```
