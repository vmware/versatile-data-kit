# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import nbformat
from nbconvert.preprocessors import ClearOutputPreprocessor


def clear_notebook_outputs(notebook_path: str):
    """
    Clear the outputs of a Jupyter notebook.
    :param notebook_path: Path to the Jupyter notebook.
    """
    with open(notebook_path, encoding="utf-8") as f:
        notebook = nbformat.read(f, as_version=4)
        clearer = ClearOutputPreprocessor()
        clearer.preprocess(notebook, {})

    with open(notebook_path, "w", encoding="utf-8") as f:
        nbformat.write(notebook, f)
