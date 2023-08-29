# VEP-2421: Universal Database Enhancement Proposal

* **Author(s):** Maximiliaan Sobry (maxsobry@gmail.com)
* **Status:** draft

- [Summary](#summary)
- [Glossary](#glossary)
- [Motivation](#motivation)
- [Requirements and goals](#requirements-and-goals)
- [High-level design](#high-level-design)
- [Detailed design](#detailed-design)
- [Implementation stories](#implementation-stories)
- [Alternatives](#alternatives)

## Summary


This is a proposal for creating a universal Database plugin, than can be used for ingesting data from multiple databases.
As an result it will make the process easier and faster because there wouldn't be a need for having multiple plugins for each database. 
This plugin will be a all-in-one plugin that can handle ingestion's from multiple databases.


## Glossary

DAL: Database Abstraction Layer



## Motivation

Implementing a Universal Database Plugin takes away the work of creating a new plugin on every Database the user request. 
Therefore if a new Database should be added for ingestion, this can be implemented faster. Above that having one plugin will result in having a better support, easier management and debugging. 


## Requirements and goals

With this UniversalDB-Plugin we are trying to achieve a plugin that is able to handle all/multiple databases for ingestion.
Above that by generalizing a plugin and making it multi functional it will make it easier to modify and debug the plugin.
And it will also let us focus on one plugin instead of multiple plugins. 
This plugin will be able to work with databases that are using the PEP249 standard and are using the same SQL queries.


This is for all type of users that want to use different types of databases for ingestion and for this they will only need to download just one plugin.
By generalizing a plugin for universal databases ingestion we would be able focus on flexibility and simplicity.



## High-level design


How do we implement this universal Database plugin? 
For changing the plugin to a universal plugin for multiple databases we would need to change: 
Setup.py, Requirements.txt, Configuration.py, Connection.py, Plugin.py, Ingestion.py and test_plugin.py.
The desired outcome of this plugin would be to be able to use multiple databases that are using the PEP249 standard and the same SQL Queries.
We can test this outcome by writing a test-plugin that creates a temporary database file and tries to ingest on a given destination table.
If this test is succesfull we can check if the plugin will pass the github checks.




## Detailed design


This design is based on the 'vdk-sqlite' modification to 'vdk-duckdb'(VDK-DuckDB: Introducing a new database plugin #2561).
In the section of the detailed design I will go over the exact things that need to be modified or changed for each file.
If the modification is succesfull, we would be able to use every database that is using PEP249 and SQL queries.

For the modification of the Configuration, we need to modify 5 things.
-Generelizing the constants, configuration classes.
-Take into account the different fie extensions of each database.
-Supports the connection strings (Add entries for: Hostname/IP, Port, Username, Password, Database Name).
-Support for other Configuration parameters
-Refactor the 'add_definition' function (make it more generic).

For the modification of the Ingestion, we need to modify 4 things.
-We need to create a DAL (Database Abstraction Layer) for base classes or interfaces and also for switching between databases.
-Modify the connection handling, for example make use of the library 'SQL Alchemy'. This is for the connection handling of multiple databases.
-Query Construction, make sure that the databases implement use the same SQL queries.
-Data type mapping. '__python_value_to_duckdb_type' maps Python data types to DuckDB. But this differs between databases.

For the modification of the Connection, we need to modify 6 things.
-Use of the Database drivers. For each datbase a driver or library is required to connect to it.
-Database Configuration. Databases need multiple configuration parameters (Host, port, username, password, database name, etc.)
So extend the class to accept these as parameters.
-Abstract Database Operations: Create an abstract base class that defines the methods any database connection class should implement. 
-Implement Database-specific Classes. Example DuckDBConnection.
-Modify the connection establishment. Each database has it's way of establishing a connection.
-Modify the cursor and methods. These Cursors and Methods vary per database.

For the modification of the Plugin, we need to modify 6 things.
-The database Configuration should be modified to be able to accepts database type, connection string and other related parameters.
-Database Connection Factory. Implement a connection factory method that connects to different databases based on the type. Also update the 'initialize_job'
-Generalize the Query tool. 'duckdb_query' function needs adjustments based on the different databases.
-Update the Command Line integration. Rename and adjust the command to be more generic.
-Ensure that all the necessary databases drivers and libraries are installed.
-Handle the variability. Different databases have different SQL dialects and features.

For the modification of the Plugin we can make a test-plugin that creates a temporary database file, establishes connection,
defines a destination table and eventually tries to ingest using the payload.

Regarding the Capacity, Availability, Performance, Troubleshooting, Operability it will be the same as the other database plugins.




## Alternatives

No alternatives where considered.
