# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

import configparser
import json
import os
import re

import nltk
import psycopg2
import requests
from fastapi import FastAPI
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from openai import OpenAI
from pgvector.psycopg2 import register_vector
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

# TODO: figure out how to make the parts configurable, i.e. embedding model could be configured here
# but it would also need to be the same at the document ingestion step so that the similarity search
# can work


def clean_text(text):
    """
    TODO: Copied from the embed-ingest-job-example. Needs to be replaced by a more robust approach, something
    off the shelf ideally.
    """
    text = text.lower()
    # remove punctuation and special characters
    text = re.sub(r"[^\w\s]", "", text)
    # remove stopwords and lemmatize
    stop_words = set(stopwords.words("english"))
    lemmatizer = WordNetLemmatizer()
    text = " ".join(
        [lemmatizer.lemmatize(word) for word in text.split() if word not in stop_words]
    )
    return text


def setup_nltk(temp_dir):
    """
    Set up NLTK by creating a temporary directory for NLTK data and downloading required resources.
    """
    from pathlib import Path

    nltk_data_path = Path(temp_dir) / "nltk_data"

    nltk_data_path.mkdir(exist_ok=True)
    nltk.data.path.append(str(nltk_data_path))
    if os.path.isdir(nltk_data_path):
        return

    nltk.download("stopwords", download_dir=str(nltk_data_path))
    nltk.download("wordnet", download_dir=str(nltk_data_path))


class QuestionModel(BaseModel):
    question: str


app = FastAPI()


@app.post("/question/")
async def answer_question(question: QuestionModel):
    setup_nltk(".")

    config = configparser.ConfigParser()
    config.read("api_config.ini")

    # Embed the question
    model = SentenceTransformer("all-mpnet-base-v2")
    embedding = model.encode(clean_text(question.question), show_progress_bar=True)

    # DB connection
    db_conn = psycopg2.connect(
        dsn=config["db"]["postgres_dsn"],
        dbname=config["db"]["postgres_dbname"],
        user=config["db"]["postgres_user"],
        password=config["db"]["postgres_password"],
        host=config["db"]["postgres_host"],
    )
    register_vector(db_conn)
    cur = db_conn.cursor()

    # Similarity search
    cur.execute(
        "SELECT vdk_confluence_doc_metadata_example_2.data FROM vdk_confluence_doc_metadata_example_2 JOIN vdk_confluence_doc_embeddings_example_2 ON vdk_confluence_doc_metadata_example_2.id = vdk_confluence_doc_embeddings_example_2.id ORDER BY vdk_confluence_doc_embeddings_example_2.embedding <-> %s LIMIT 3",
        (embedding,),
    )
    res = cur.fetchall()

    docs = "\n".join([doc[0] for doc in res])

    # Build prompt
    prompt = f"""Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer. Use three sentences maximum. Keep the answer as concise as possible. Always say "thanks for asking!" at the end of the answer.
    Context: {docs}
    Question: {question.question}
    Helpful Answer:"""

    # Standard formatting for LLaMa 2
    prompt = f"<s>[INST] <<SYS>>\nBelow is an instruction that describes a task. Write a response that appropriately completes the request.\n<</SYS>>\n\n{prompt} [/INST] "

    client = OpenAI(
        api_key=config["llm"]["auth_token"], base_url=config["llm"]["llm_host"]
    )

    completion = client.completions.create(
        model=config["llm"]["llm_model"],
        prompt=prompt,
        max_tokens=512,
        temperature=0,
        stream=True,
    )

    model_output = ""
    for c in completion:
        model_output += c.choices[0].text

    return model_output
