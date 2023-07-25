# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import glob
import os
import re
import shutil


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
        _get_archive_name(): Generates and returns the name of the archive file.
        archive_folder(): Creates a zip archive of the directory.
    """

    def __init__(self, dir_path):
        validate_dir(dir_path)
        self._dir_path = dir_path

    def get_parent_dir(self) -> str:
        return os.path.dirname(self._dir_path)

    def _get_archive_name(self) -> str:
        dir_name = os.path.basename(self._dir_path)
        parent_dir = self.get_parent_dir()
        return os.path.join(parent_dir, f"{dir_name}_archive")

    def archive_folder(self):
        shutil.make_archive(self._get_archive_name(), "zip", self._dir_path)


class ConvertJobDirectoryProcessor:
    """
    The ConvertJobDirectoryProcessor class provides functionality to process a directory,
    archiving it, and storing specific file contents into a structured list.
    Attributes:
        _dir_path (str): The path to the directory that will be processed.
        _code_structure (list): A list to store the processed content of specific files.
        _removed_files (list): A list to store the names of files that have been removed.
    Methods:
        process_files(): Processes files in the directory, saving and removing specific files' content.
        cleanup(): Removes any remaining files that were supposed to be removed.
        get_code_structure() -> list: Returns the structured list of processed file contents.
        get_removed_files() -> list: Returns the list of removed file names.
    """

    def __init__(self, dir_path):
        validate_dir(dir_path)
        self._dir_path = dir_path
        self._code_structure = []
        self._removed_files = []

    def process_files(self):
        all_files = sorted(glob.glob(os.path.join(self._dir_path, "*")))

        for file in all_files:
            if file.endswith(".sql"):
                with open(file) as f:
                    content = f.read()
                self._code_structure.append(f'job_input.execute_query("""{content}""")')
                self._removed_files.append(os.path.basename(file))
                os.remove(file)
            elif file.endswith(".py"):
                with open(file) as f:
                    content = f.read()

                if re.search(r"def run\(job_input", content):
                    self._code_structure.append(content)
                    self._removed_files.append(os.path.basename(file))
                    os.remove(file)

    def cleanup(self):
        for file_name in self._removed_files:
            file_path = os.path.join(self._dir_path, file_name)
            if os.path.exists(file_path):
                os.remove(file_path)

    def get_code_structure(self):
        return self._code_structure

    def get_removed_files(self):
        return self._removed_files
