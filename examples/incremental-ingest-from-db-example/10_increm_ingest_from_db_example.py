from vdk.api.job_input import IJobInput


def run(job_input: IJobInput):

    # Get last_date property/parameter:
    #  - if the target table already exists, take the property value already stored in the DJ from the previous run
    #  - if the target table does not exist, set last_date to 01-01-1900 in oder to fetch all rows
    last_date = job_input.get_property("last_date", '01-01-1900')

    # Select the needed records from the source table using job_input's built-in method and a query parameter
    data = job_input.execute_query(
        f"""
        SELECT * FROM increm_ingest
        WHERE reported_date > '{last_date}'
        ORDER BY reported_date
        """
    )
    # Fetch table info containing the column names
    table_info = job_input.execute_query("PRAGMA table_info(increm_ingest)")

    # If any data is returned from the query, send the fetched records for ingestion
    if len(data) > 0:
        job_input.send_tabular_data_for_ingestion(
            data,
            column_names=[x[1] for x in table_info],
            destination_table="incremental_ingest_from_db_example"
        )

        # Reset the last_date property value to the latest date in the source db table
        job_input.set_all_properties(
            {
                "last_date": max([x[2] for x in data])
            }
        )

    print(f"Success! {len(data)} rows were inserted.")
