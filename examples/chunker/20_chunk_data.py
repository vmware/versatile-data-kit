# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import logging
import pathlib
import re

from config import CHUNK_OVERLAP
from config import CHUNK_SIZE
from config import CHUNKS_JSON_FILE_LOCATION
from config import CLEANED_DOCUMENTS_JSON_FILE_LOCATION
from nltk.tokenize import word_tokenize
from vdk.api.job_input import IJobInput

log = logging.getLogger(__name__)


class ChunkerFactory:
    @staticmethod
    def get_chunker(strategy_name: str, **kwargs):
        chunkers = {
            "fixed": FixedSizeChunker,
            "wiki": WikiSectionChunker,
        }
        if strategy_name in chunkers:
            return (
                chunkers[strategy_name](**kwargs)
                if strategy_name == "fixed"
                else chunkers[strategy_name]()
            )
        else:
            raise ValueError(
                f"Unknown chunking strategy: {strategy_name}. "
                f"Supported strategies: {list(chunkers.keys())}"
            )


class Chunker:
    """
    Splits text into chunks.
    """

    def chunk(self, documents: dict):
        raise NotImplementedError("The chunking strategy is not supported.")


class FixedSizeChunker(Chunker):
    """
    Splits text into chunks of fixed size with overlap between neighbouring ones.
    """

    def __init__(self, chunk_size, chunk_overlap):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk(self, documents):
        chunked_documents = []
        for doc in documents:
            tokens = word_tokenize(doc["data"])
            chunks = [
                {
                    "metadata": {
                        "title": f"{doc['metadata']['title']}",
                        "id": f"{doc['metadata']['id']}",
                        "source": f"{doc['metadata']['title']}",
                        "deleted": f"{doc['metadata']['deleted']}",
                    },
                    "data": tokens[i : i + self.chunk_size],
                }
                for i in range(0, len(tokens), self.chunk_size - self.chunk_overlap)
            ]
            chunked_documents.extend(chunks)
        return chunked_documents


class WikiSectionChunker(Chunker):
    """
    Splits Wiki articles into chunks.
    """

    def __init__(self):
        pass

    def chunk(self, documents):
        chunked_documents = []
        for doc in documents:
            sections = re.split(
                r"\n==+ [^=]+ ==+\n", doc["data"]
            )  # Wiki section headers are identified by ==
            for i, section in enumerate(sections):
                if section.strip():
                    chunked_documents.append(
                        {
                            "metadata": {
                                "title": f"{doc['metadata']['title']}",
                                "id": f"{doc['metadata']['id']}",
                                "source": f"{doc['metadata']['title']}",
                                "deleted": f"{doc['metadata']['deleted']}",
                            },
                            "data": section.strip(),
                        }
                    )
        return chunked_documents


def load_documents(json_file_path: str):
    """
    Loads documents from JSON file.

    :param json_file_path: Path to the JSON file containing documents.
    :return: List of documents.
    """
    with open(json_file_path, encoding="utf-8") as file:
        return json.load(file)


def store(name, content):
    json_data = json.dumps(content, indent=4)
    with open(name, "w") as file:
        file.write(json_data)


def run(job_input: IJobInput):
    log.info(f"Starting job step {__name__}")

    data_job_dir = pathlib.Path(job_input.get_job_directory())
    input_json = data_job_dir / CLEANED_DOCUMENTS_JSON_FILE_LOCATION
    output_json = data_job_dir / CHUNKS_JSON_FILE_LOCATION
    chunk_size = CHUNK_SIZE
    chunk_overlap = CHUNK_OVERLAP
    chunking_strategy = job_input.get_property("chunking_strategy", "fixed")

    documents = load_documents(input_json)
    print(documents)
    chunker = ChunkerFactory.get_chunker(
        chunking_strategy, chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    chunked_documents = chunker.chunk(documents)
    print(chunked_documents)
    if chunked_documents:
        log.info(
            f"{len(chunked_documents)} documents chunks created using the {chunking_strategy} chunking strategy."
        )
        store(output_json, chunked_documents)
        log.info(f"Chunks saved to {output_json}")
