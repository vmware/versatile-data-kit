# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging

from vdk.api.job_input import IJobInput

from datasets import load_dataset
from torch import torch

log = logging.getLogger(__name__)


def run(job_input: IJobInput):
    log.info(f"Starting job step {__name__}")
    dataset = load_dataset("yelp_review_full")
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained("bert-base-cased")

    def tokenize_function(examples):
        return tokenizer(examples["text"], padding="max_length", truncation=True)

    tokenized_datasets = dataset.map(tokenize_function, batched=True)
    from transformers import AutoModelForSequenceClassification

    model = AutoModelForSequenceClassification.from_pretrained("bert-base-cased", num_labels=5)
    from transformers import TrainingArguments
    training_args = TrainingArguments(output_dir="test_trainer", use_mps_device=False)

    import numpy as np
    import evaluate

    metric = evaluate.load("accuracy")

    def compute_metrics(eval_pred):
        logits, labels = eval_pred
        predictions = np.argmax(logits, axis=-1)
        return metric.compute(predictions=predictions, references=labels)

    from transformers import Trainer

    small_train_dataset = tokenized_datasets["train"].shuffle(seed=42).select(range(1000))
    small_eval_dataset = tokenized_datasets["test"].shuffle(seed=42).select(range(1000))
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=small_train_dataset,
        eval_dataset=small_eval_dataset,
        compute_metrics=compute_metrics,
    )
    trainer.train()


if __name__ == '__main__':
    run(None)
