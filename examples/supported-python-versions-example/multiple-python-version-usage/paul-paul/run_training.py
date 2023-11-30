from typing import Callable

import mlflow.pytorch
from mlflow import MlflowClient


def print_auto_logged_info(r):
    tags = {k: v for k, v in r.data.tags.items() if not k.startswith("mlflow.")}
    artifacts = [f.path for f in MlflowClient().list_artifacts(r.info.run_id, "model")]
    print(f"run_id: {r.info.run_id}")
    print(f"artifacts: {artifacts}")
    print(f"params: {r.data.params}")
    print(f"metrics: {r.data.metrics}")
    print(f"tags: {tags}")


def run_training(training_run: Callable):
    # Auto log all MLflow entities
    mlflow.pytorch.autolog()
    with mlflow.start_run() as run:
        training_run()
    print_auto_logged_info(mlflow.get_run(run_id=run.info.run_id))
