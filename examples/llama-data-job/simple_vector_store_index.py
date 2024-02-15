# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import os
from datetime import datetime

from llama_index.core import Settings
from llama_index.core import SimpleDirectoryReader
from llama_index.core import VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.readers.confluence import ConfluenceReader
from vdk.api.job_input import IJobInput

log = logging.getLogger(__name__)


class ConfluenceDataSource:
    def __init__(self, confluence_url, token, space_key):
        self.confluence_url = confluence_url
        self.token = token
        self.space_key = space_key
        os.environ[
            "CONFLUENCE_API_TOKEN"
        ] = token  # ConfluenceReader works with env variables
        self.reader = ConfluenceReader(base_url=confluence_url)

    def fetch_confluence_documents(self, cql_query):
        try:
            # TODO: think about configurable limits ? or some streaming solution
            # How do we fit all documents in memory ?
            raw_documents = self.reader.load_data(cql=cql_query, max_num_results=10)
            return raw_documents
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

    confluence_reader = ConfluenceDataSource(confluence_url, token, space_key)

    documents = confluence_reader.fetch_updated_pages_in_confluence_space(
        last_date, parent_page_id
    )
    log.info(f"Found {len(documents)} updated pages")

    # This is buggy , it doesn't account for server timezone and local timezone
    # But also assumes that server clock and local clock are synchronized (which they are likely not)
    # The ts should be the one of the latest processed page.
    set_property(job_input, "last_date", datetime.now().strftime("%Y-%m-%d %H:%M"))

    Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
    index = VectorStoreIndex.from_documents(documents)
    index.storage_context.persist(persist_dir="./persist_dir")
