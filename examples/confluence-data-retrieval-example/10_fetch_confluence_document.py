# Copyright 2023-2025 Broadcom
# SPDX-License-Identifier: Apache-2.0
import logging
import os

from langchain_community.document_loaders import ConfluenceLoader
from vdk.api.job_input import IJobInput

log = logging.getLogger(__name__)


def fetch_confluence_document(url, token, document_id):
    try:
        # For more info regarding the LangChain ConfluenceLoader:
        # https://python.langchain.com/docs/integrations/document_loaders/confluence
        loader = ConfluenceLoader(url=url, token=token)
        documents = loader.load(page_ids=[document_id])
        return documents[0] if documents else None
    except Exception as e:
        log.error(f"Error fetching document with ID {document_id} from Confluence: {e}")
        return None


def run(job_input: IJobInput):
    log.info(f"Starting job step {__name__}")

    confluence_url = os.environ.get("VDK_CONFLUENCE_URL")
    token = os.environ.get("VDK_CONFLUENCE_TOKEN")
    doc_id = os.environ.get("VDK_CONFLUENCE_DOC_ID")

    doc = fetch_confluence_document(confluence_url, token, doc_id)

    if doc:
        log.info(f"Document with ID {doc_id} fetched successfully.")
        print(doc.page_content)
    else:
        log.error(f"Failed to fetch the document with ID {doc_id}.")
