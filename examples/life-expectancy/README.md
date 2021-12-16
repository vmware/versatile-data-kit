# Life Expectancy
This example provides the complete code to perform the following tasks:
- Data Ingestion from CSV
- Data Processing
- Data Publication in form of Visual Report/Dashboard

The directory is organized as follows:
* **life-expectancy** - contains jobs
* **le_utils** - contains some auxiliary_functions.

## Scenario

Researchers from the Department of Population History and Social Structure have to conduct a study on the life expectancy of Americans. The objective of the study is to understand over time which American states have the greatest life expectancy.

## Data Scoures
After extensive research, the researchers found two main datasets, both of which are available as CSV files:

- [U.S. Life Expectancy at Birth by State and Census Tract - 2010-2015](https://catalog.data.gov/dataset/u-s-life-expectancy-at-birth-by-state-and-census-tract-2010-2015)
- [U.S. State Life Expectancy by Sex, 2018](https://catalog.data.gov/dataset/u-s-state-life-expectancy-by-sex-2018)

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

## Requirements
To run this example, you need:
* Versatile Data Kit
* Trino DB
* Versatile Data Kit plugin for Trino

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

See the vdk-trino [Documentation Page](https://github.com/vmware/versatile-data-kit/tree/main/projects/vdk-plugins/vdk-trino "Documentation Page") for more details.

### Other Requirements
This example also requires the following Python libraries, which are included in the `requirement.txt` file:

```
inspect
math
numpy
pandas
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

Jobs from 10 to 60 are devoted to Data Ingestion:
* 01 - 03 ingest data in table `life_expectancy_2010_2015`
* 04 - 06 ingest data in table `life_expectancy_2018`

## Data Processing
Data Processing includes the following tasks:
* Clean tables
* Merge the cleaned datasets

### Clean tables
Table cleaning includes jobs from 07 to 10.  

**Tasks 07 - 08**  
Cleaning the `life_expectancy_2010_2015` table includes the following two operations:
* group records by County
* split the column `LifeExpectancyRange` in two decimal columns `MinLifeExpectancyRange` and `MaxLifeExpectancyRange`.

The output of the cleaning process for the `life_expectancy_2010_2015` table is stored in a new table, called `cleaned_life_expectancy_2010_2015`.

The following table shows an example of the `cleaned_life_expectancy_2010_2015` table:

| **State**     | **LifeExpectancy** | **MinLifeExpectancyRange** | **MaxLifeExpectancyRange** | **LifeExpectancyStandardError** |
| ------------- | ------------------------- | -------------------------- | -------------------------- | -------------------------------------- |
| **Florida**   | 78.38                     | 74.10                      | 82.15                      | 1.94                                   |
| **Georgia**   | 76.62                     | 70.38                      | 79.17                      | 1.82                                   |
| **Hawaii**    | 81.32                     | 79.09                      | 88.06                      | 1.94                                   |
| **New York**  | 80.33                     | 77.74                      | 85.87                      | 1.97                                   |
| **Kansas**    | 78.05                     | 73.95                      | 81.30                      | 1.81                                   |
| **Louisiana** | 75.37                     | 67.82                      | 77.87                      | 1.83                                   |
| **Oregon**    | 79.09                     | 76.45                      | 82.41                      | 1.76                                   |
| **Arizona**   | 78.37                     | 74.97                      | 81.47                      | 2.00                                   |
| **Alabama**   | 74.81                     | 65.64                      | 77.27                      | 1.72                                   |
| **Missouri**  | 76.96                     | 71.37                      | 79.92

**Tasks 09 - 10**  
Cleaning the `life_expectancy_2010_2015` table includes the following operations:
* rename column `LEB` to `LifeExpectancy`
* rename column `SE` to `LifeExpectancyStandardError`
* split the column `Quartile` in two decimal columns `MinLifeExpectancyRange` and `MaxLifeExpectancyRange`
* select only rows with `Sex = 'Total'`.

The following table shows an example of the `cleaned_life_expectancy_2018` table:

| **State**          | **LifeExpectancy** | **MinlifeExpectancyRange** | **MaxLifeExpectancyRange** | **LifeExpectancyStandardError** |
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

### Merge the two datasets
* Build a view that shows only the top 10 states with the greatest life expectancy
	* Order dataset
	* Take only the first 10 states
