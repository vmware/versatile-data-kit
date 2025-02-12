# Copyright 2023-2025 Broadcom
# SPDX-License-Identifier: Apache-2.0
import logging
import os

from langchain_community.document_loaders import ConfluenceLoader
from vdk.api.job_input import IJobInput

log = logging.getLogger(__name__)


def fetch_confluence_space(url, token, space_key):
    try:
        # For more info regarding the LangChain ConfluenceLoader:
        # https://python.langchain.com/docs/integrations/document_loaders/confluence
        loader = ConfluenceLoader(url=url, token=token)
        documents = loader.load(
            space_key=space_key, include_attachments=True, limit=20, max_pages=20
        )
        return documents
    except Exception as e:
        log.error(f"Error fetching documents from Confluence: {e}")
        return None


def run(job_input: IJobInput):
    log.info(f"Starting job step {__name__}")

    confluence_url = os.environ.get("VDK_CONFLUENCE_URL")
    token = os.environ.get("VDK_CONFLUENCE_TOKEN")
    space_key = os.environ.get("VDK_CONFLUENCE_SPACE_KEY")

    docs = fetch_confluence_space(confluence_url, token, space_key)

    if docs:
        log.info(f"{len(docs)} documents fetched successfully.")
        log.info("Printing the first 50 chars of each doc")
        for i, doc in enumerate(docs):
            print(f"{i}: {doc.page_content[:50]}")
    else:
        log.error(f"Failed to fetch any documents from the space with key {space_key}.")
