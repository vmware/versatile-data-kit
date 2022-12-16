from vdk.api.job_input import IJobInput
import os
import re

CURR_FILE_PATH = os.path.dirname(os.path.abspath(__file__))
SQL_FILES_FOLDER = "02-requisite-sql-scripts"


def run(job_input: IJobInput):
    job_arguments = job_input.get_arguments()

    check = job_arguments.get("check")
    target_table = f'{job_arguments.get("target_schema")}.{job_arguments.get("target_table")}'
    tmp_table = job_arguments.get("tmp_table")

    if check:

        clone_table(job_input=job_input, orig_table_name=target_table,
                    clone_table_name=tmp_table)

        tmp_table_schema = tmp_table.split('.')[0]
        tmp_table_name = tmp_table.split('.')[1]
        insert_into_tmp = get_query('02-insert-into-target.sql').format(target_schema=tmp_table_schema,
                                                                        target_table=tmp_table_name)
        job_input.execute_statement(insert_into_tmp)

        if check(tmp_table):
            insert_into_target = get_query('02-insert-into-target.sql').format(source_schema=tmp_table_schema,
                                                                             source_view=tmp_table_name)
            job_input.execute_query(insert_into_target)
        else:
            raise Exception('The data is not passing the quality checks!')

    else:
        insert_into_target = get_query('02-insert-into-target.sql')
        job_input.execute_query(insert_into_target)


def get_query(sql_file_name):
    query_full_path = os.path.join(
        CURR_FILE_PATH,
        SQL_FILES_FOLDER,
        sql_file_name
    )

    with open(query_full_path) as query:
        content = query.read()
        return content


def clone_table(job_input, orig_table_name, clone_table_name):
    orig_create_table_statement = extract_create_table_statement(job_input=job_input, table_name=orig_table_name)
    orig_create_table_statement = clean_statements_for_comparison(orig_create_table_statement)

    create_table_like(job_input=job_input, orig_table_name=orig_table_name, clone_table_name=clone_table_name)

    clone_create_table_statement = extract_create_table_statement(job_input=job_input, table_name=clone_table_name)
    clone_create_table_statement = clean_statements_for_comparison(clone_create_table_statement)

    if orig_create_table_statement != clone_create_table_statement:
        job_input.execute_query(f'DROP TABLE {clone_table_name}')
    create_table_like(job_input=job_input, orig_table_name=orig_table_name, clone_table_name=clone_table_name)

    return clone_create_table_statement


def clean_statements_for_comparison(create_table_statement):
    create_table_statement = remove_location(create_table_statement)
    create_table_statement = remove_table_properties(create_table_statement)
    return remove_create_table_prefix(create_table_statement)


def extract_create_table_statement(job_input, table_name):
    return job_input.execute_query(
        f'SHOW CREATE TABLE {table_name}')[0][0]


def create_table_like(job_input, orig_table_name, clone_table_name):
    job_input.execute_query(f"CREATE TABLE IF NOT EXISTS {clone_table_name} LIKE {orig_table_name}")


def remove_location(create_table_statement):
    location_match = re.search("\nLOCATION '(.*)'", create_table_statement)
    if location_match:
        create_table_statement = create_table_statement.replace(location_match.group(), '')
    return create_table_statement


def remove_create_table_prefix(create_table_statement):
    print(create_table_statement)
    table_prefix_match = re.search("CREATE TABLE(.*)\\(", create_table_statement)
    return create_table_statement.replace(table_prefix_match.group(), '', 1)


def remove_table_properties(create_table_statement):
    table_properties_match = re.search("\nTBLPROPERTIES \\((.*)\\)", create_table_statement)
    if table_properties_match:
        create_table_statement = create_table_statement.replace(table_properties_match.group(), '')
    return create_table_statement
