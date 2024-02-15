# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0

# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import csv
import logging
import pathlib

from config import DOCUMENTS_CSV_FILE_LOCATION
from langchain_community.document_loaders import ConfluenceLoader
from vdk.api.job_input import IJobInput

log = logging.getLogger(__name__)


def fetch_confluence_space(url, token, space_key):
    try:
        # For more info regarding the LangChain ConfluenceLoader:
        # https://python.langchain.com/docs/integrations/document_loaders/confluence
        loader = ConfluenceLoader(url=url, token=token)
        documents = loader.load(
            space_key=space_key, include_attachments=True, limit=50, max_pages=50
        )
        return documents
    except Exception as e:
        log.error(f"Error fetching documents from Confluence: {e}")
        return None


def write_documents_to_csv(documents, filename):
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        for doc in documents:
            writer.writerow([doc.page_content])


def run(job_input: IJobInput):
    log.info(f"Starting job step {__name__}")

    confluence_url = job_input.get_property(
        "confluence_url", "https://yoansalambashev.atlassian.net/"
    )
    # since the Confluence space is public, no need to generate API token
    token = ""
    space_key = job_input.get_property("space_key", "RESEARCH")
    data_job_dir = pathlib.Path(job_input.get_job_directory())
    output_csv = data_job_dir / DOCUMENTS_CSV_FILE_LOCATION

    docs = fetch_confluence_space(confluence_url, token, space_key)

    if docs:
        log.info(f"{len(docs)} documents fetched successfully.")
        write_documents_to_csv(docs, output_csv)
        log.info(f"Documents written to {output_csv}")
    else:
        log.error(f"Failed to fetch any documents from the space with key {space_key}.")
