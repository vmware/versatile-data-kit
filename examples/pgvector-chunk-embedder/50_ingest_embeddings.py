# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import logging
import pathlib
import pickle

import numpy as np
from config import DOCUMENTS_JSON_FILE_LOCATION
from config import EMBEDDINGS_PKL_FILE_LOCATION
from vdk.api.job_input import IJobInput

log = logging.getLogger(__name__)


def run(job_input: IJobInput):
    log.info(f"Starting job step {__name__}")

    data_job_dir = pathlib.Path(job_input.get_job_directory())
    input_embeddings_path = data_job_dir / EMBEDDINGS_PKL_FILE_LOCATION
    input_documents_path = data_job_dir / DOCUMENTS_JSON_FILE_LOCATION

    with open(input_embeddings_path, "rb") as file:
        embeddings = pickle.load(file)
    with open(input_documents_path) as file:
        documents = json.load(file)

    print(len(documents), len(embeddings))

    # TODO: our postgres plugin doesn't support updates (upserts) so updating with same ID fails.

    for i, document in enumerate(documents):
        metadata_payload = {
            "id": document["metadata"]["id"],
            "title": document["metadata"]["title"],
            "data": document["data"],
            "source": document["metadata"]["source"],
            "deleted": document["metadata"]["deleted"],
        }
        job_input.send_object_for_ingestion(
            payload=metadata_payload,
            destination_table=job_input.get_property("destination_metadata_table"),
        )

        for chunk_id, chunk_embedding in enumerate(embeddings[i]):
            embedding_list = (
                chunk_embedding.tolist()
                if isinstance(chunk_embedding, np.ndarray)
                else chunk_embedding
            )

            embedding_payload = {
                "id": document["metadata"]["id"],
                "chunk_id": chunk_id,
                "embedding": embedding_list,
            }

            job_input.send_object_for_ingestion(
                payload=embedding_payload,
                destination_table=job_input.get_property(
                    "destination_embeddings_table"
                ),
            )
