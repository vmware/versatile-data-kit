# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import json
import logging
import pathlib
import subprocess
from contextlib import contextmanager
from tempfile import NamedTemporaryFile
from typing import Iterator
from typing import Optional

from vdk.plugin.singer.adapter import Catalog
from vdk.plugin.singer.adapter import Message
from vdk.plugin.singer.adapter import parse_message
from vdk.plugin.singer.adapter import SchemaMessage
from vdk.plugin.singer.message_utils import message_to_catalog_entry

log = logging.getLogger(__name__)


class TapCommandRunner:
    def __init__(self):
        self._process: Optional[subprocess.Popen] = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def stop(self):
        if self._process is not None:
            self._process.terminate()
            self._process = None

    @contextmanager
    def _temp_file(self, data: dict) -> pathlib.Path:
        with NamedTemporaryFile() as file:
            if data:
                file.write(json.dumps(data).encode())
                file.flush()
            yield pathlib.Path(file.name)

    def _run_discover_catalog(self, config, tap) -> Catalog:
        with self._temp_file(config) as temp_file:
            cmd_args = [tap, "--config", str(temp_file), "--discover"]
            with subprocess.Popen(
                cmd_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            ) as process:
                stdout_data, stderr_data = process.communicate()
                if stderr_data:
                    log.debug(f"Command {cmd_args} logs: {stderr_data}")
                return Catalog.from_dict(json.loads(stdout_data))

    def _run_command(self, cmd_args) -> Iterator[Message]:
        if not self._process:
            self._process = subprocess.Popen(
                cmd_args, stdout=subprocess.PIPE, text=True
            )
        for line in iter(self._process.stdout.readline, ""):
            stderr_line = self._process.stderr
            if stderr_line:
                log.debug(stderr_line)

            # log.info(f"tap command line: {line}")
            yield parse_message(line.strip())

    def _run_discover_command(self, tap: str, config: dict) -> Iterator[Message]:
        with self._temp_file(config) as temp_file:
            cmd_args = [tap, "--config", str(temp_file), "--discover"]
            yield from self._run_command(cmd_args)

    def discover(self, tap: str, config: dict) -> Catalog:
        try:
            return self._discover_from_schema_messages(config, tap)
        except Exception as e:
            log.debug(
                f"Could not discover schema using schema messages from the tap. Message: {e}"
            )
        try:
            return self._run_discover_catalog(config, tap)
        except Exception as e:
            log.debug(f"Could not discover schema catalog from the tap. Message: {e}")
        return Catalog([])

    def _discover_from_schema_messages(self, config, tap):
        try:
            entries = []
            for message in self._run_discover_command(tap, config):
                if isinstance(message, SchemaMessage):
                    entries.append(message_to_catalog_entry(message))
                else:
                    break
            return Catalog(entries)
        finally:
            self.stop()

    def sync(
        self, tap: str, config: dict, state: dict = None, catalog: dict = None
    ) -> Iterator[Message]:
        with self._temp_file(config) as config_file, self._temp_file(
            state
        ) as state_file, self._temp_file(catalog) as catalog_file:
            cmd_args = [tap, "--config", str(config_file)]

            if state:
                cmd_args.extend(["--state", str(state_file)])

            if catalog:
                cmd_args.extend(["--catalog", str(catalog_file)])

            yield from self._run_command(cmd_args)
