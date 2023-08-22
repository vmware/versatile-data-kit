import nbformat
from nbconvert.preprocessors import ClearOutputPreprocessor


class NotebookOutputCleaner:
    def __init__(self, notebook_path: str):
        self.notebook_path = notebook_path

    def clear_outputs(self):
        with open(self.notebook_path, 'r', encoding='utf-8') as f:
            notebook = nbformat.read(f, as_version=4)
            clearer = ClearOutputPreprocessor()
            clearer.preprocess(notebook, {})

        with open(self.notebook_path, 'w', encoding='utf-8') as f:
            nbformat.write(notebook, f)
