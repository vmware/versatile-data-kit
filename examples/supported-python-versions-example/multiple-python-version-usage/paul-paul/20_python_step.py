# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os

import pytorch_lightning as L
import torch
from run_training import run_training
from torch.nn import functional as F
from torch.utils.data import DataLoader
from torch.utils.data import Subset
from torchmetrics import Accuracy
from torchvision import transforms
from torchvision.datasets import MNIST
from vdk.api.job_input import IJobInput


class MNISTModel(L.LightningModule):
    def __init__(self):
        super().__init__()
        self.l1 = torch.nn.Linear(28 * 28, 10)
        self.accuracy = Accuracy("multiclass", num_classes=10)

    def forward(self, x):
        return torch.relu(self.l1(x.view(x.size(0), -1)))

    def training_step(self, batch, batch_nb):
        x, y = batch
        logits = self(x)
        loss = F.cross_entropy(logits, y)
        pred = logits.argmax(dim=1)
        acc = self.accuracy(pred, y)

        # PyTorch `self.log` will be automatically captured by MLflow.
        self.log("train_loss", loss, on_epoch=True)
        self.log("acc", acc, on_epoch=True)
        return loss

    def configure_optimizers(self):
        return torch.optim.Adam(self.parameters(), lr=0.02)


# Initialize our model.
mnist_model = MNISTModel()

# Load MNIST dataset.
train_ds = MNIST(
    os.getcwd(), train=True, download=True, transform=transforms.ToTensor()
)
# Only take a subset of the data for faster training.
indices = torch.arange(32)
train_ds = Subset(train_ds, indices)
train_loader = DataLoader(train_ds, batch_size=8)

# Initialize a trainer.
trainer = L.Trainer(max_epochs=3)


def run(job_input: IJobInput):
    # job_input.run_training()
    run_training(lambda: trainer.fit(mnist_model, train_loader))
