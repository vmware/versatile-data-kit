# VDK local differential privacy plugin

This plugin adds support to VDK for anonymizing data before sending it for ingestion.

In most differential privacy algorithm we assume that the data curator(database owner) can be trusted.
The actual real data is stored in the database.
The analyst can't be trusted and so noise is added to the result of the database queries.

However this plugin should be used when the database curator is not trusted.
In this case we want to apply noise to the database before sending it to the curator.

At the moment we support noise on two different types of data.
1. [Boolean data with Random response](https://programming-dp.com/ch13.html#randomized-response)
2. [Enum type data with Unary encoding](https://programming-dp.com/ch13.html#unary-encoding)


## Usage

```
pip install local-differential-privacy
```

### Configuration

(`vdk config-help` is useful command to browse all config options of your installation of vdk)

| Name                                            | Description                                                                                                                                                           | (example)  Value |
|-------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|---|
| differential_privacy_randomized_response_fields | Map with entity/table name and list of attributes names that need to be privatized using random response.The column must be of type booleanChecks are case sensitive. | Default value is: '{"table_name": ["column_name"]}'.
|differential_privacy_unary_encoding_fields | Map with entity/table name and list of attributes names that need to be privatized using unary encoding.Checks are case sensitive.                                    | Default value is: '{"table_name": {"column_name":["DOMAIN_VALUE_ONE", "DOMAIN_VALUE_TWO","DOMAIN_VALUE_THREE"]}}'.


## Build and testing

```
pytest
```
