# Copyright 2023-2025 Broadcom
# SPDX-License-Identifier: Apache-2.0
# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import configparser

import psycopg2
from clean_embed_text import get_question_embedding
from fastapi import FastAPI
from openai import OpenAI
from pgvector.psycopg2 import register_vector
from pydantic import BaseModel

# TODO: figure out how to make the parts configurable, i.e. embedding model could be configured here
# but it would also need to be the same at the document ingestion step so that the similarity search
# can work


class QuestionModel(BaseModel):
    question: str


app = FastAPI()


@app.post("/question/")
async def answer_question(question: QuestionModel):
    config = configparser.ConfigParser()
    config.read("api_config.ini")

    embedding = get_question_embedding(question.question)

    cur = get_db_cursor(config)

    docs = get_similar_documents(embedding, cur, config, 3)
    docs = truncate(docs, 2000)

    prompt = build_prompt(docs, question.question)

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


def truncate(s, wordcount):
    return " ".join(s.split()[:wordcount])


def get_db_cursor(config):
    db_conn = psycopg2.connect(
        dsn=config["db"]["postgres_dsn"],
        dbname=config["db"]["postgres_dbname"],
        user=config["db"]["postgres_user"],
        password=config["db"]["postgres_password"],
        host=config["db"]["postgres_host"],
    )
    register_vector(db_conn)
    cur = db_conn.cursor()

    return cur


def build_prompt(context, question):
    prompt = f"""Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer. Use three sentences maximum. Keep the answer as concise as possible. Always say "thanks for asking!" at the end of the answer.
    Context: {context}
    Question: {question}
    Helpful Answer:"""

    # Standard formatting for LLaMa 2
    return f"<s>[INST] <<SYS>>\nBelow is an instruction that describes a task. Write a response that appropriately completes the request.\n<</SYS>>\n\n{prompt} [/INST] "


def get_similar_documents(question_embedding, db_cursor, config, doc_count):
    db_cursor.execute(
        f"""
        SELECT {config["tables"]["metadata_table"]}.data
        FROM {config["tables"]["metadata_table"]}
        JOIN {config["tables"]["embeddings_table"]}
        ON {config["tables"]["metadata_table"]}.id = {config["tables"]["embeddings_table"]}.id
        ORDER BY {config["tables"]["embeddings_table"]}.embedding <-> %s LIMIT {doc_count}
        """,
        (question_embedding,),
    )
    res = db_cursor.fetchall()

    return "\n".join([doc[0] for doc in res])
