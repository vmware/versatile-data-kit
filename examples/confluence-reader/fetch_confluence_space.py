# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import json
from datetime import datetime

from langchain_community.document_loaders import ConfluenceLoader
from vdk.api.job_input import IJobInput

log = logging.getLogger(__name__)


def update_saved_documents(file_path, new_docs):
    try:
        with open(file_path, 'r') as file:
            existing_docs = json.load(file)

        if isinstance(existing_docs, list):
            existing_docs = {doc['id']: doc for doc in existing_docs}
    except (FileNotFoundError, json.JSONDecodeError):
        existing_docs = {}

    if not existing_docs:
        with open(file_path, 'w') as file:
            json.dump(list(new_docs), file, indent=4)
    else:
        for doc in new_docs:
            existing_docs[doc['id']] = doc

        with open(file_path, 'w') as file:
            json.dump(list(existing_docs.values()), file, indent=4)


def flag_deleted_pages(file_path, current_confluence_pages):
    try:
        with open(file_path, 'r') as file:
            existing_docs = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        print("File not found or invalid format. Exiting.")
        return

    # convert to a set of IDs for faster lookup
    current_page_ids = set(page.metadata['id'] for page in current_confluence_pages)

    # flag deleted pages
    for doc in existing_docs:
        if doc['id'] not in current_page_ids:
            doc['deleted'] = True

    with open(file_path, 'w') as file:
        json.dump(existing_docs, file, indent=4)


class ConfluenceDataSource:
    def __init__(self, confluence_url, token, space_key):
        self.confluence_url = confluence_url
        self.token = token
        self.space_key = space_key
        self.loader = ConfluenceLoader(url=self.confluence_url, token=self.token)

    def fetch_updated_pages_in_confluence_space(self):
        try:
            with open('last_modification.txt', 'r') as file:
                last_date = file.read().strip()

            cql_query = f"lastModified > '{last_date}' and type = page and space = {self.space_key}"

            current_date_time = datetime.now()
            formatted_current_date_time = current_date_time.strftime("%Y-%m-%d %H:%M")

            with open('last_modification.txt', 'w') as file:
                file.write(formatted_current_date_time)

            documents = self.loader.load(cql=cql_query, limit=5, max_pages=5)

            return documents
        except Exception as e:
            log.error(f"Error fetching documents from Confluence: {e}")
            return None

    def fetch_all_pages_in_confluence_space(self):
        try:
            cql_query = f"type = page and space = {self.space_key}"

            documents = self.loader.load(cql=cql_query, limit=5, max_pages=5)

            return documents
        except Exception as e:
            log.error(f"Error fetching documents from Confluence: {e}")
            return None


def run(job_input: IJobInput):
    log.info(f"Starting job step {__name__}")

    confluence_url = job_input.get_property(
        "confluence_url", ""
    )
    token = job_input.get_property(
        "confluence_token", ""
    )
    space_key = job_input.get_property(
        "confluence_space_key", ""
    )

    confluence_reader = ConfluenceDataSource(confluence_url, token, space_key)

    file_path = 'confluence_data.json'

    # check updatesfd
    docs = confluence_reader.fetch_updated_pages_in_confluence_space()
    docs_metadata = []
    for doc in docs:
        docs_metadata.append(doc.metadata)
    update_saved_documents(file_path, docs_metadata)

    # check for deletions
    flag_deleted_pages(file_path, confluence_reader.fetch_all_pages_in_confluence_space())


# ignore pictures for the comment but we need to generally handle them
