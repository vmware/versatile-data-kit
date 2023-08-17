import json
from pathlib import Path


def remove_outputs_from_notebook(notebook_path):
    with notebook_path.open('r') as f:
        content = json.load(f)

    for cell in content["cells"]:
        if cell["cell_type"] == "code":
            cell['outputs'] = []
            cell['execution_count'] = None

    with notebook_path.open('w') as f:
        json.dump(content, f, indent=4)


class NotebookJobDirectory:
    def __init__(self, directory_path):
        self.directory_path = Path(directory_path)
        self.notebook_paths = list(self.directory_path.glob('*.ipynb'))

    def remove_outputs_from_all(self):
        for notebook_path in self.notebook_paths:
            remove_outputs_from_notebook(notebook_path)
