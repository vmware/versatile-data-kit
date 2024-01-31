# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import json
from datetime import datetime

from langchain_community.document_loaders import ConfluenceLoader
from vdk.api.job_input import IJobInput

log = logging.getLogger(__name__)


def save_documents(self, file_path, new_docs):
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


class ConfluenceDataSource:
    def __init__(self):
        self.confluence_url = "https://confluence.eng.vmware.com/"
        self.token = "Njc0Nzk0NDMyNzcxOiFRTi5TYXYo/KJCNn54GuBAlQ7w"
        self.space_key = "SuperCollider"
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

    confluence_reader = ConfluenceDataSource()

    file_path = 'confluence_data.json'
    docs = confluence_reader.fetch_updated_pages_in_confluence_space()
    docs_metadata = []
    for doc in docs:
        docs_metadata.append(doc.metadata)
    save_documents(file_path, docs_metadata)

    if docs:
        log.info(f"{len(docs)} documents fetched successfully.")
        log.info("Printing the first 50 chars of each doc")
        for i, doc in enumerate(docs):
            print("\n")
            print(doc.metadata)
            print("\n")
    else:
        log.error(f"Failed to fetch any documents from the space with key {space_key}.")

