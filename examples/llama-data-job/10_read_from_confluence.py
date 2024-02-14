# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import logging
import os
from datetime import datetime

from vdk.api.job_input import IJobInput
from llama_index.readers.confluence import ConfluenceReader
from confluence_document import ConfluenceDocument
log = logging.getLogger(__name__)


def read_json_file(file_path):
    try:
        with open(file_path) as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        log.error(f"Error reading JSON file: {e}")
        return None


def write_json_file(file_path, data):
    try:
        with open(file_path, "w") as file:
            json.dump(data, file, indent=4)
    except OSError as e:
        log.error(f"Error writing JSON file: {e}")


def update_saved_documents(file_path, new_docs):
    existing_docs = read_json_file(file_path) or []

    if (
        isinstance(existing_docs, list)
        and existing_docs
        and isinstance(existing_docs[0], dict)
    ):
        existing_docs = [
            ConfluenceDocument(
                doc["metadata"], doc["data"], doc["metadata"].get("deleted", False)
            )
            for doc in existing_docs
        ]

    existing_docs_dict = {doc.metadata["id"]: doc for doc in existing_docs}

    for doc in new_docs:
        existing_docs_dict[doc.metadata["id"]] = doc

    updated_docs_list = list(existing_docs_dict.values())

    serialized_docs = [doc.serialize() for doc in updated_docs_list]
    write_json_file(file_path, serialized_docs)


def flag_deleted_pages(file_path, current_confluence_documents):
    existing_docs = read_json_file(file_path)
    if existing_docs is None:
        log.error("Existing documents not found. Exiting.")
        return

    existing_docs = [
        ConfluenceDocument(
            doc["metadata"], doc["data"], doc["metadata"].get("deleted", False)
        )
        for doc in existing_docs
    ]

    current_page_ids = {doc.metadata["id"] for doc in current_confluence_documents}

    num_deleted = 0
    for doc in existing_docs:
        if doc.metadata["id"] not in current_page_ids:
            doc.metadata["deleted"] = True
            num_deleted += 1
    log.info(f"Found {num_deleted} deleted pages.")

    serialized_docs = [doc.serialize() for doc in existing_docs]
    write_json_file(file_path, serialized_docs)


class ConfluenceDataSource:

    def __init__(self, confluence_url, token, space_key):
        self.confluence_url = confluence_url
        self.token = token
        self.space_key = space_key
        os.environ['CONFLUENCE_API_TOKEN'] = token  # ConfluenceReader works with env variables
        self.reader = ConfluenceReader(base_url=confluence_url)

    def fetch_confluence_documents(self, cql_query):
        try:
            # TODO: think about configurable limits ? or some streaming solution
            # How do we fit all documents in memory ?
            raw_documents = self.reader.load_data(cql=cql_query, max_num_results=10, limit=50)
            return [
                ConfluenceDocument(doc.metadata, doc.text)
                for doc in raw_documents
            ]
        except Exception as e:
            log.error(f"Error fetching documents from Confluence: {e}")
            raise e

    def fetch_updated_pages_in_confluence_space(
        self, last_date="1900-02-06 17:54", parent_page_id=None
    ):
        # TODO: this really should be called not when page is read but after it's successfully processed.
        cql_query = (
            f"lastModified > '{last_date}' and type = page and space = {self.space_key}"
        )

        if parent_page_id:
            # https://developer.atlassian.com/server/confluence/cql-field-reference/#ancestor
            cql_query += f" and ancestor = {parent_page_id}"

        return self.fetch_confluence_documents(cql_query)

    def fetch_all_pages_in_confluence_space(self, parent_page_id=None):
        # TODO: this is very inefficient as we are actually downloading everything
        cql_query = f"type = page and space = {self.space_key}"
        if parent_page_id:
            cql_query += f" and ancestor = {parent_page_id}"
        return self.fetch_confluence_documents(cql_query)


def get_value(job_input, key: str, default_value=None):
    return job_input.get_arguments().get(
        key, job_input.get_property(key, os.environ.get(key.upper(), default_value))
    )


def set_property(job_input: IJobInput, key, value):
    props = job_input.get_all_properties()
    props[key] = value
    job_input.set_all_properties(props)


def run(job_input: IJobInput):
    log.info(f"Starting job step {__name__}")

    confluence_url = get_value(job_input, "confluence_url")
    token = get_value(job_input, "confluence_token")
    space_key = get_value(job_input, "confluence_space_key")
    parent_page_id = get_value(job_input, "confluence_parent_page_id")
    last_date = get_value(job_input, "last_date", "1900-01-01 12:00")
    data_file = get_value(
        job_input,
        "data_file",
        os.path.join(job_input.get_temporary_write_directory(), "confluence_data.json"),
    )

    confluence_reader = ConfluenceDataSource(confluence_url, token, space_key)

    updated_docs = confluence_reader.fetch_updated_pages_in_confluence_space(
        last_date, parent_page_id
    )
    log.info(f"Found {len(updated_docs)} updated pages")
    update_saved_documents(data_file, updated_docs)

    # This is buggy , it doesn't account for server timezone and local timezone
    # But also assumes that server clock and local clock are synchronized (which they are likely not)
    # The ts should be the one of the latest processed page.
    set_property(job_input, "last_date", datetime.now().strftime("%Y-%m-%d %H:%M"))

    flag_deleted_pages(
        data_file,
        confluence_reader.fetch_all_pages_in_confluence_space(parent_page_id),
    )