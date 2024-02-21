# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import json
import logging
import pickle

import numpy as np
from common.database_storage import DatabaseStorage
from config import get_value
from vdk.api.job_input import IJobInput

log = logging.getLogger(__name__)


def run(job_input: IJobInput):
    log.info(f"Starting job step {__name__}")

    input_embeddings_path = get_value(job_input, "output_embeddings")

    with open(input_embeddings_path, "rb") as file:
        embeddings = pickle.load(file)
    storage = DatabaseStorage(get_value(job_input, "storage_connection_string"))
    storage_name = get_value(job_input, "storage_name", "confluence_data")
    documents = json.loads(storage.retrieve(storage_name))

    # TODO: our postgres plugin doesn't support updates (upserts) so updating with same ID fails.

    for i, document in enumerate(documents):
        composite_id = document["metadata"]["id"]

        metadata_payload = {
            "id": composite_id,
            "title": document["metadata"]["title"],
            "source": document["metadata"]["source"],
            "data": document["data"],
            "deleted": document["metadata"]["deleted"],
        }
        job_input.send_object_for_ingestion(
            payload=metadata_payload,
            destination_table=get_value(job_input, "destination_metadata_table"),
        )

        embedding_payload = {
            "id": composite_id,
            "embedding": embeddings[i].tolist()
            if isinstance(embeddings[i], np.ndarray)
            else embeddings[i],
        }
        job_input.send_object_for_ingestion(
            payload=embedding_payload,
            destination_table=get_value(job_input, "destination_embeddings_table"),
        )
