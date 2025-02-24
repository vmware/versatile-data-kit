# Copyright 2023-2025 Broadcom
# SPDX-License-Identifier: Apache-2.0
import logging
import os
from datetime import datetime

from confluence_document import ConfluenceDocument
from langchain_community.document_loaders import ConfluenceLoader
from vdk.api.job_input import IJobInput
from vdk.plugin.storage.database_storage import DatabaseStorage

log = logging.getLogger(__name__)


def merge_docs(existing_docs, new_docs) -> list:
    if existing_docs:
        existing_docs_dict = {doc.metadata["id"]: doc for doc in existing_docs}

        for doc in new_docs:
            existing_docs_dict[doc.metadata["id"]] = doc
        return list(existing_docs_dict.values())
    else:
        return new_docs


def flag_deleted_pages(existing_docs, current_confluence_documents):
    if existing_docs is None:
        log.error("Existing documents not found. Exiting.")
        return

    current_page_ids = {doc.metadata["id"] for doc in current_confluence_documents}

    num_deleted = 0
    for doc in existing_docs:
        if doc.metadata["id"] not in current_page_ids:
            doc.metadata["deleted"] = True
            num_deleted += 1
    log.info(f"Found {num_deleted} deleted pages.")


class ConfluenceDataSource:
    """
    A class for retrieving and managing data from a Confluence space.

    This class provides methods to interact with Confluence data, including fetching updated pages,
    retrieving all pages, fetching updated documents by parent ID, flagging deleted pages, and updating saved documents.

    Attributes:
        confluence_url (str): The URL of the Confluence instance.
        token (str): The authentication token for accessing Confluence.
        space_key (str): The key of the Confluence space to retrieve data from.
        loader (ConfluenceLoader): An instance of the ConfluenceLoader for data retrieval.

    Methods:
        fetch_updated_pages_in_confluence_space(): Fetches updated pages in the Confluence space based on the last modification date.
        fetch_all_pages_in_confluence_space(): Retrieves all pages in the Confluence space.
        flag_deleted_pages(): Flags deleted pages based on the current Confluence data.
        update_saved_documents(): Updates the saved documents in the JSON file with the latest data.

    """

    def __init__(self, confluence_url, token, space_key):
        self.confluence_url = confluence_url
        self.token = token
        self.space_key = space_key
        self.loader = ConfluenceLoader(url=self.confluence_url, token=self.token)

    def fetch_confluence_documents(self, cql_query):
        # TODO: think about configurable limits ? or some streaming solution
        # How do we fit all documents in memory ?
        raw_documents = self.loader.load(cql=cql_query, limit=50, max_pages=200)
        return [
            ConfluenceDocument(doc.metadata, doc.page_content) for doc in raw_documents
        ]

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
        # the rest api offer expand query parameter for that but langchain loader limits all expansion to return body always.
        # See https://docs.atlassian.com/atlassian-confluence/REST/5.5/
        # We can hack around with by subclassing ContentFormat enum ? and try to convince library devs to add metadata only response in the loader
        cql_query = f"type = page and space = {self.space_key}"
        if parent_page_id:
            cql_query += f" and ancestor = {parent_page_id}"
        return self.fetch_confluence_documents(cql_query)


def get_value(job_input, key: str, default_value=None):
    value = os.environ.get(key.upper(), default_value)
    value = job_input.get_property(key, value)
    value = job_input.get_secret(key, value)
    return job_input.get_arguments().get(key, value)


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
    last_date = (
        job_input.get_property(confluence_url, {})
        .setdefault(space_key, {})
        .setdefault(parent_page_id, {})
        .get("last_date", "1900-01-01 12:00")
    )
    storage_name = get_value(job_input, "storage_name", "confluence_data")
    storage = DatabaseStorage(get_value(job_input, "storage_connection_string"))
    # TODO: this is not optimal . We just care about the IDs, we should not need to retrieve everything
    existing_docs = storage.retrieve(storage_name)
    if existing_docs:
        existing_docs = [ConfluenceDocument(**doc) for doc in existing_docs]

    confluence_reader = ConfluenceDataSource(confluence_url, token, space_key)
    updated_docs = confluence_reader.fetch_updated_pages_in_confluence_space(
        last_date, parent_page_id
    )
    log.info(f"Found {len(updated_docs)} updated pages")
    all_docs = merge_docs(existing_docs, updated_docs)

    # This is buggy , it doesn't account for server timezone and local timezone
    # But also assumes that server clock and local clock are synchronized (which they are likely not)
    # The ts should be the one of the latest processed page.
    set_property(job_input, "last_date", datetime.now().strftime("%Y-%m-%d %H:%M"))

    flag_deleted_pages(
        all_docs,
        confluence_reader.fetch_all_pages_in_confluence_space(parent_page_id),
    )

    # TODO: it would be better to save each page in separate row.
    # But that's quick solution for now to pass the data to the next job

    log.info(f"Store {len(all_docs)} documents in {storage_name}")
    # TODO: why not use job_input.send_object_for_ingestion ... it's our ingestion interface
    storage.store(storage_name, [doc.serialize() for doc in all_docs])
