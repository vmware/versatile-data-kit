# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import _io
import json
import logging
from enum import Enum
from enum import unique
from typing import Any
from typing import Dict
from typing import Tuple
from typing import Type

import click
from vdk.internal.control.configuration.defaults_config import load_default_team_name
from vdk.internal.control.exception.vdk_exception import VDKException
from vdk.internal.control.rest_lib.factory import ApiClientFactory
from vdk.internal.control.rest_lib.rest_client_errors import ApiClientErrorDecorator
from vdk.internal.control.utils import cli_utils
from vdk.internal.control.utils import output_printer
from vdk.internal.control.utils.output_printer import OutputFormat

log = logging.getLogger(__name__)


@unique
class SecretOperation(Enum):
    """
    An enum used to store the types of secrets operations
    """

    SET = "set"
    GET = "get"


class JobSecrets:
    def __init__(
        self,
        rest_api_url: str,
        job_name: str,
        team: str,
        output_format: OutputFormat,
    ):
        self.__secrets_api = ApiClientFactory(rest_api_url).get_secrets_api()
        self.__output = output_format
        self.__printer = output_printer.create_printer(output_format)
        self.__job_name = job_name
        self.__team = team
        self.__deployment_id = "TODO"

    def __get_all_remote_secrets(self) -> Dict[str, Any]:
        return self.__secrets_api.data_job_secrets_read(
            team_name=self.__team,
            job_name=self.__job_name,
            deployment_id=self.__deployment_id,
        )

    def __list_secrets(self, remote_secrets: Dict[str, Any]) -> None:
        self.__printer.print_dict(remote_secrets)

    @staticmethod
    def _to_bool(value: str) -> bool:
        if value.lower() == "true":
            return True
        if value.lower() == "false":
            return False
        raise ValueError("bool cast accept only True/true/False/false values.")

    @staticmethod
    def __cast(key: str, new_value: str, value_type: Type) -> Any:
        try:
            log.debug(f"Cast {key} to type {value_type}")
            if value_type == bool:
                return JobSecrets._to_bool(new_value)
            if value_type == list or value_type == dict:
                raise ValueError(
                    "Updating Secrets which are set to list or dict is not supported through CLI."
                )
            else:
                return value_type(new_value)
        except Exception as e:
            raise VDKException(
                f"The value of the passed secret with key {key} is not an expected type",
                f"We detect existing value for secret with key '{key}' has type {value_type}. "
                f"But we could not convert the value '{new_value}' to that type. Error is {e}",
                "In order to ensure that we do not overwrite with bad value the secrets, "
                "the operation aborts and no secret will be updated.",
                "If the key value is correct, you can first delete the key (with --delete)"
                " and then use the cli to set it again. "
                "Or you can use VDK job_input.set_all_secrets to overwrite them.",
            )

    def __merge_secrets(
        self, new_secrets: Dict[str, str], remote_secrets: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Merge secrets between those already persisted (remote_secrets) and new key value pairs passed by user.
        Merge algorithm attempts to preserve original type if possible and if not detects type from the passed value.

        :param new_secrets: the passed key value pairs
        :param remote_secrets: the secrets that are persisted on the remote server
        :return: the new merged secrets
        """
        merged = remote_secrets
        for new_key, new_value in new_secrets.items():
            if new_key in remote_secrets:
                remote_value_type = type(remote_secrets[new_key])
                merged[new_key] = self.__cast(new_key, new_value, remote_value_type)
            else:
                merged[new_key] = new_value

        return merged

    @ApiClientErrorDecorator()
    def get(self, key: str) -> None:
        remote_secrets = self.__get_all_remote_secrets()
        if key in remote_secrets:
            self.__list_secrets({key: remote_secrets[key]})
        else:
            self.__list_secrets({})

    @ApiClientErrorDecorator()
    def list(self) -> None:
        remote_secrets = self.__get_all_remote_secrets()
        self.__list_secrets(remote_secrets)

    @ApiClientErrorDecorator()
    def update_secrets(self, new_secrets: Dict[str, str]) -> None:
        remote_secrets = self.__get_all_remote_secrets()
        merged_secrets = self.__merge_secrets(new_secrets, remote_secrets)
        self.__secrets_api.data_job_secrets_update(
            team_name=self.__team,
            job_name=self.__job_name,
            deployment_id=self.__deployment_id,
            request_body=merged_secrets,
        )

    @ApiClientErrorDecorator()
    def overwrite_secrets(self, new_secrets: Dict[str, str]) -> None:
        self.__secrets_api.data_job_secrets_update(
            team_name=self.__team,
            job_name=self.__job_name,
            deployment_id=self.__deployment_id,
            request_body=new_secrets,
        )

    @ApiClientErrorDecorator()
    def delete_keys(self, delete_keys: Tuple[str]) -> None:
        secrets = self.__get_all_remote_secrets()
        for key in delete_keys:
            secrets.pop(key)
        self.__secrets_api.data_job_secrets_update(
            team_name=self.__team,
            job_name=self.__job_name,
            deployment_id=self.__deployment_id,
            request_body=secrets,
        )

    @ApiClientErrorDecorator()
    def delete_all_job_secrets(self) -> None:
        self.__secrets_api.data_job_secrets_update(
            team_name=self.__team,
            job_name=self.__job_name,
            deployment_id=self.__deployment_id,
            request_body={},
        )


# Below is the definition of the CLI API/UX users will be interacting
# Above is the actual implementation of the operations


@click.command(
    name="secrets",
    help="Secrets are key value pairs that can be set per data job. "
    """
         Job secrets are used to store credentials/tokens/sensitive data securely.

     Examples:

     \b
     # Set single secret with key "my-key" and value "my-value". If no value is passed
     you'll get prompted so it's not printed on the screen.
     vdk secrets --set my-key "my-value"

     \b
     # Update multiple secrets at once.
     vdk secrets --set "key1" "value1" --set "key2" "value2" --set "secret1" --set "secret2"

     \b
     # Use backslash \\ to set them on multiple lines
     vdk secrets \\
        --set "key1" "value1" \\
        --set "key2" "value2"

     \b
     # Return the value associated with the given key "my-key"
     vdk secrets --get "my-key"

     \b
     # Delete a secrets with key "my-key"
     vdk secrets --delete "my-key"

     \b
     # List all secrets
     vdk secrets --list

                    """,
)
@click.option(
    "-n", "--name", prompt="Job Name", type=click.STRING, help="The job name."
)
@click.option(
    "-t",
    "--team",
    type=click.STRING,
    default=load_default_team_name(),
    required=True,
    prompt="Job Team",
    help="The team name to which the job belongs to.",
)
@click.option(
    "--set",
    nargs=2,
    type=click.STRING,
    multiple=True,
    help="Set key value secret. "
    "If secret with same key exists we will override it but we will try to preserve the type."
    "Entirely new secrets will be set with string type"
    "You can set multiple secrets by using --set multiple times",
)
@click.option(
    "--delete",
    nargs=1,
    type=click.STRING,
    multiple=True,
    help="Delete a secret with the given key. "
    "You can delete multiple secrets by using --delete multiple times",
)
@click.option(
    "--delete-all-job-secrets",
    is_flag=True,
    default=False,
    help="Delete all secrets for the given data job. ",
)
@click.option(
    "--overwrite-all-job-secrets",
    type=click.File("rb"),
    help="Pass JSON file that will overwrite all secrets for the passed data job. "
    "No sanity checks are performed. It will completely overwrite all secrets."
    "Use with care - with great power comes great responsibility."
    "The option accepts '-' which will read the file input from the standard input (stdin)",
)
@click.option("--get", type=click.STRING, help="Get secret with a given key. ")
@click.option("--list", is_flag=True, help="List all secrets for the data job ")
@cli_utils.rest_api_url_option()
@cli_utils.output_option()
@cli_utils.check_required_parameters
def secrets_command(
    name: str,
    team: str,
    set: Tuple[str, str],  # pylint: disable=redefined-builtin
    delete: Tuple[str],
    delete_all_job_secrets: bool,
    overwrite_all_job_secrets: _io.BufferedReader,
    get: str,
    list: bool,  # pylint: disable=redefined-builtin
    rest_api_url: str,
    output: OutputFormat,
):
    if (set or delete) and (get or list):
        raise VDKException(
            what="Invalid arguments",
            why="Wrong input. Cannot pass --get or --list at the same time as --set and --delete.",
            consequence="Command will abort with error.",
            countermeasure="Fix passed arguments such that get/list are not passed in the same time as set/delete.",
        )
    if get and list:
        raise VDKException(
            what="Invalid arguments",
            why="Wrong input. Cannot pass --get at the same time as --list. Choose one of the two.",
            consequence="Command will abort with error",
            countermeasure="Fix passed arguments such that only --list or only --get are used.",
        )
    log.debug(
        f"secrets passed options: name: {name}, team: {team}, "
        f"set: {set}, get: {get}, list: {list}, delete: {delete} "
        f"rest_api_url: {rest_api_url}, output: {output}"
    )
    key_value_pairs = _get_key_value_pairs(set)
    cmd = JobSecrets(rest_api_url, name, team, output)
    if key_value_pairs:
        cmd.update_secrets(key_value_pairs)
    if delete:
        cmd.delete_keys(delete)
    if delete_all_job_secrets:
        cmd.delete_all_job_secrets()
    if get:
        cmd.get(get)
    if list:
        cmd.list()
    if overwrite_all_job_secrets:
        json_secrets_string = overwrite_all_job_secrets.read().decode("utf-8")
        try:
            json_secrets = json.loads(json_secrets_string)
            cmd.overwrite_secrets(json_secrets)
        except Exception as e:
            raise VDKException(
                "Expected valid json for secrets overwrite.",
                "JSON was not valid; error is " + str(e),
                "Operation is aborted. Nothing has been changed.",
                "Fix the file to be a valid json and re-try again.",
            )


def _get_key_value_pairs(set):  # pylint: disable=redefined-builtin
    key_value_pairs = {}
    if set:
        for key, value in set:
            if value:
                key_value_pairs[key] = value
            else:
                value = click.prompt(f"{key}", hide_input=True)
                key_value_pairs[key] = value
    return key_value_pairs
