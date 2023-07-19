import os
import shutil
import glob


def validate_dir(dir_path):
    if not os.path.isdir(dir_path):
        raise ValueError(f"{dir_path} is not a valid directory.")
    return True


class DirectoryArchiver:
    """
    The DirectoryArchiver class provides functionality to create an archive of a specified directory.
    Attributes:
        _dir_path (str): The path to the directory that will be archived.
    Methods:
        get_parent_dir(): Returns the parent directory of _dir_path.
        get_archive_name(): Generates and returns the name of the archive file.
        archive_folder(): Creates a zip archive of the directory.
    """

    def __init__(self, dir_path):
        validate_dir(dir_path)
        self._dir_path = dir_path

    def get_parent_dir(self) -> str:
        return os.path.dirname(self._dir_path)

    def get_archive_name(self) -> str:
        dir_name = os.path.basename(self._dir_path)
        parent_dir = self.get_parent_dir()
        return os.path.join(parent_dir, f"{dir_name}_archive")

    def archive_folder(self):
        shutil.make_archive(self.get_archive_name(), 'zip', self._dir_path)


class ConvertJobDirectoryProcessor:
    """
    The TransformJobDirectoryProcessor class provides functionality to process a directory,
    archiving it, and storing specific file contents into a structured list.
    Attributes:
        _dir_path (str): The path to the directory that will be processed.
        _archiver (DirectoryArchiver): An instance of DirectoryArchiver to archive the directory.
        _code_structure (list): A list to store the processed content of specific files.
    Methods:
        process_files(): Processes files in the directory, saving and removing specific files' content.
        get_code_structure() -> list: Returns the structured list of processed file contents.
    """

    def __init__(self, dir_path):
        validate_dir(dir_path)
        self._dir_path = dir_path
        self._archiver = DirectoryArchiver(dir_path)
        self._code_structure = []

    def process_files(self):
        all_files = sorted(glob.glob(os.path.join(self._dir_path, '*')))
        self._archiver.archive_folder()

        for file in all_files:
            if file.endswith('.sql'):
                with open(file, 'r') as f:
                    content = f.read()
                self._code_structure.append(f'job_input.execute_query("""{content}""")')
                os.remove(file)
            elif file.endswith('.py'):
                with open(file, 'r') as f:
                    content = f.read()

                if 'def run(job_input: IJobInput)' in content:
                    self._code_structure.append(content)
                    os.remove(file)

    def get_code_structure(self):
        return self._code_structure
