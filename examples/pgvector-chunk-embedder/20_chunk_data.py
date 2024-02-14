# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import logging
import pathlib
import re

from bs4 import BeautifulSoup
from config import CHUNK_OVERLAP
from config import CHUNK_SIZE
from config import CHUNKS_PKL_FILE_LOCATION
from config import CLEANED_DOCUMENTS_JSON_FILE_LOCATION
from nltk.tokenize import word_tokenize
from vdk.api.job_input import IJobInput

log = logging.getLogger(__name__)


class ChunkerFactory:
    @staticmethod
    def get_chunker(strategy_name, **kwargs):
        chunkers = {
            "fixed": FixedSizeChunker,
            "html": HTMLHeaderChunker,
            "wiki": WikiSectionChunker,
            "git_class": GitClassChunker,
            "git_func": GitFunctionChunker,
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
    def chunk(self, documents):
        raise NotImplementedError("The chunking strategy is not supported.")


class FixedSizeChunker(Chunker):
    def __init__(self, chunk_size, chunk_overlap):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk(self, documents):
        chunked_documents = []
        for doc in documents:
            tokens = word_tokenize(doc["data"])
            chunks = [
                {"id": doc["metadata"]["id"], "chunk": tokens[i : i + self.chunk_size]}
                for i in range(0, len(tokens), self.chunk_size - self.chunk_overlap)
            ]
            chunked_documents.extend(chunks)
        return chunked_documents


class HTMLHeaderChunker(Chunker):
    def __init__(self):
        pass

    def chunk(self, documents):
        chunked_documents = []
        for doc in documents:
            soup = BeautifulSoup(doc["data"], "html.parser")
            for header_level in range(1, 7):  # <h1> to <h6>
                for header in soup.find_all(f"h{header_level}"):
                    next_node = header
                    chunk = ""
                    while True:
                        next_node = next_node.nextSibling
                        if not next_node or next_node.name in [
                            f"h{i}" for i in range(1, 7)
                        ]:
                            break
                        if isinstance(next_node, str):
                            chunk += next_node.strip()
                        else:
                            chunk += next_node.get_text(strip=True)
                    if chunk:
                        chunked_documents.append(
                            {"id": doc["metadata"]["id"], "chunk": chunk}
                        )
        return chunked_documents


class WikiSectionChunker(Chunker):
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
                        {"id": f"{doc['metadata']['id']}", "section": section.strip()}
                    )
        return chunked_documents


class GitChunker(Chunker):
    """
    Chunks Git code by the specified regex pattern.
    """

    def __init__(self, pattern):
        self.pattern = pattern
        self.compiled_pattern = re.compile(self.pattern)

    def chunk(self, documents):
        chunked_documents = []
        for doc in documents:
            current_chunk = []
            for line in doc["data"].split("\n"):
                if self.compiled_pattern.match(line):
                    if current_chunk:
                        chunked_documents.append(
                            {
                                "id": doc["metadata"]["id"],
                                "chunk": "\n".join(current_chunk),
                            }
                        )
                        current_chunk = []
                current_chunk.append(line)
            if current_chunk:
                chunked_documents.append(
                    {"id": doc["metadata"]["id"], "chunk": "\n".join(current_chunk)}
                )
        return chunked_documents


class GitFunctionChunker(GitChunker):
    """
    Chunks Git code by function. The pattern looks for the function signature starting with 'def'.
    """

    def __init__(self):
        super().__init__(r"^def\s+\w+\(.*\):\s*(?:#.*)?$")


class GitClassChunker(GitChunker):
    """
    Chunks Git code by class. The pattern looks for the class signature starting with 'class'.
    """

    def __init__(self):
        super().__init__(r"^class\s+\w+\(.*\):\s*(?:#.*)?$")


def load_documents(json_file_path):
    """
    Loads documents from JSON file.

    :param json_file_path: Path to the JSON file containing documents.
    :return: List of documents.
    """
    with open(json_file_path, encoding="utf-8") as file:
        return json.load(file)


def run(job_input: IJobInput):
    log.info(f"Starting job step {__name__}")

    data_job_dir = pathlib.Path(job_input.get_job_directory())
    input_json = data_job_dir / CLEANED_DOCUMENTS_JSON_FILE_LOCATION
    output_chunks = data_job_dir / CHUNKS_PKL_FILE_LOCATION
    chunk_size = CHUNK_SIZE
    chunk_overlap = CHUNK_OVERLAP
    chunking_strategy = job_input.get_property("chunking_strategy", "default")

    documents = load_documents(input_json)
    chunker = ChunkerFactory.get_chunker(
        chunking_strategy, chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    chunked_documents = chunker.chunk(documents)
    if chunked_documents:
        log.info(
            f"{len(chunked_documents)} documents chunks created using the {chunking_strategy} chunking strategy."
        )
        with open(output_chunks, "wb") as file:
            import pickle

            pickle.dump(chunked_documents, file)
        log.info(f"Chunks saved to {output_chunks}")
