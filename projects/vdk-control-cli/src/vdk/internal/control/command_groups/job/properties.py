# Copyright 2021 VMware, Inc.
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
from tabulate import tabulate
from vdk.internal.control.configuration.defaults_config import load_default_team_name
from vdk.internal.control.exception.vdk_exception import VDKException
from vdk.internal.control.rest_lib.factory import ApiClientFactory
from vdk.internal.control.rest_lib.rest_client_errors import ApiClientErrorDecorator
from vdk.internal.control.utils import cli_utils
from vdk.internal.control.utils.cli_utils import OutputFormat

log = logging.getLogger(__name__)


@unique
class PropertyOperation(Enum):
    """
    An enum used to store the types of deploy operations
    """

    SET = "set"
    SET_SECRET = "set_secret"  # nosec
    GET = "get"


class JobProperties:
    def __init__(
        self,
        rest_api_url: str,
        job_name: str,
        team: str,
        output: OutputFormat,
    ):
        self.properties_api = ApiClientFactory(rest_api_url).get_properties_api()
        self.output = output
        self.job_name = job_name
        self.team = team
        self.deployment_id = "TODO"

    def __get_all_remote_properties(self) -> Dict[str, Any]:
        return self.properties_api.data_job_properties_read(
            team_name=self.team,
            job_name=self.job_name,
            deployment_id=self.deployment_id,
        )

    def __list_properties(self, remote_props: Dict[str, Any]) -> None:
        if self.output == OutputFormat.TEXT.value:
            if len(remote_props) > 0:
                click.echo(
                    tabulate(
                        [[k, v] for k, v in remote_props.items()],
                        headers=("key", "value"),
                    )
                )
            else:
                click.echo("No properties.")
        else:
            click.echo(json.dumps(remote_props))

    @staticmethod
    def _to_bool(value: str) -> bool:
        if value == "true" or value == "True":
            return True
        if value == "false" or value == "False":
            return False
        raise ValueError("bool cast accept only True/true/False/false values.")

    @staticmethod
    def __cast(key: str, new_value: str, value_type: Type) -> Any:
        try:
            log.debug(f"Cast {key} to type {value_type}")
            if value_type == bool:
                return JobProperties._to_bool(new_value)
            if value_type == list or value_type == dict:
                raise ValueError(
                    "Updating Properties which are set to list or dict is not supported through CLI."
                )
            else:
                return value_type(new_value)
        except Exception as e:
            raise VDKException(
                f"The value of the passed property with key {key} is not expected type",
                f"We detect existing value for property with key '{key}' has type {value_type}. "
                f"But we could not convert the value '{new_value}' to that type. Error is {e}",
                f"In order to ensure that we do not overwrite with bad value the properties, "
                f"the operation aborts and no property will be updated.",
                f"If the key value is correct, you can first delete the key (with --delete)"
                f" and then use the cli to set it again. "
                f"Or you can use VDK job_input.set_all_properties to overwrite them.",
            )

    def __merge_props(
        self, new_properties: Dict[str, str], remote_properties: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Merge properties between those already persisted (remote_props) and new key value pairs passed by user.
        Merge algorithm attempts to preserve original type if possible and if not detects type from the passed value.

        :param new_properties: the passed key values pairs
        :param remote_properties: the properties that are persisted on the remote server
        :return: the new merged properties
        """
        merged = remote_properties
        for new_key, new_value in new_properties.items():
            if new_key in remote_properties:
                remote_value_type = type(remote_properties[new_key])
                merged[new_key] = self.__cast(new_key, new_value, remote_value_type)
            else:
                merged[new_key] = new_value

        return merged

    @ApiClientErrorDecorator()
    def get(self, key: str) -> None:
        remote_props = self.__get_all_remote_properties()
        if key in remote_props:
            self.__list_properties({key: remote_props[key]})
        else:
            self.__list_properties({})

    @ApiClientErrorDecorator()
    def list(self) -> None:
        remote_props = self.__get_all_remote_properties()
        self.__list_properties(remote_props)

    @ApiClientErrorDecorator()
    def update_properties(self, new_properties: Dict[str, str]) -> None:
        remote_props = self.__get_all_remote_properties()
        merged_props = self.__merge_props(new_properties, remote_props)
        self.properties_api.data_job_properties_update(
            team_name=self.team,
            job_name=self.job_name,
            deployment_id=self.deployment_id,
            request_body=merged_props,
        )

    @ApiClientErrorDecorator()
    def overwrite_properties(self, new_properties: Dict[str, str]) -> None:
        self.properties_api.data_job_properties_update(
            team_name=self.team,
            job_name=self.job_name,
            deployment_id=self.deployment_id,
            request_body=new_properties,
        )

    @ApiClientErrorDecorator()
    def delete_keys(self, delete_keys: Tuple[str]) -> None:
        props = self.__get_all_remote_properties()
        for key in delete_keys:
            props.pop(key)
        self.properties_api.data_job_properties_update(
            team_name=self.team,
            job_name=self.job_name,
            deployment_id=self.deployment_id,
            request_body=props,
        )

    @ApiClientErrorDecorator()
    def delete_all_job_properties(self) -> None:
        self.properties_api.data_job_properties_update(
            team_name=self.team,
            job_name=self.job_name,
            deployment_id=self.deployment_id,
            request_body={},
        )


# Below is the definition of the CLI API/UX users will be interacting
# Above is the actual implementation of the operations


@click.command(
    name="properties",
    help="Properties are key value pairs that can be set per data job. "
    """
         Job properties are most commonly used to:

         * store credentials securely
         * store data job state

     Examples:

     \b
     # Set single property with key "my-key" and value "my-value".
     vdk properties --set my-key "my-value"

     \b
     # Will prompt for the value so it's not printed on the screen.
     vdk properties --set-secret "my-secret"

     \b
     # Update multiple properties at once.
     vdk properties --set "key1" "value1" --set "key2" "value2" --set-secret "secret1" --set-secret "secret2"

     \b
     # Use backslash \\ to set them on multiple lines
     vdk properties \\
        --set "key1" "value1" \\
        --set "key2" "value2"

     \b
     # Return the value associated with the given key "my-key"
     vdk properties --get "my-key"

     \b
     # Delete a property with key "my-key"
     vdk properties --delete "my-key"

     \b
     # List all properties
     vdk properties --list

                    """,
    hidden=True,
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
    help="The team name to which the job belong to.",
)
@click.option(
    "--set",
    nargs=2,
    type=click.STRING,
    multiple=True,
    help="Set key value property. "
    "If property with same key exists we will override it but we will try to preserve the type."
    "Entirely new properties will be set with string type"
    "You can set multiple properties by using --set multiple times",
)
@click.option(
    "--set-secret",
    multiple=True,
    type=click.STRING,
    help="Set key value property which is a secret. It behaves almost the same way as --set."
    "The difference from --set is that it will be prompted and input would be masked. ",
)
@click.option(
    "--delete",
    nargs=1,
    type=click.STRING,
    multiple=True,
    help="Delete property with a given key. "
    "You can delete multiple properties by using --delete multiple times",
)
@click.option(
    "--delete-all-job-properties",
    is_flag=True,
    default=False,
    help="Delete all properties for the given data job. ",
)
@click.option(
    "--overwrite-all-job-properties",
    type=click.File("rb"),
    help="Pass JSON file that will overwrite all properties for the passed data job. "
    "No sanity checks are performed. It will completely overwrite all properties."
    "Use with care - with great power comes great responsibility."
    "The option accepts '-' which will read the file input from the standard input (stdin)",
)
@click.option("--get", type=click.STRING, help="Get property with a given key. ")
@click.option("--list", is_flag=True, help="List all properties for the data job ")
@cli_utils.rest_api_url_option()
@cli_utils.output_option()
@cli_utils.check_required_parameters
def properties_command(
    name: str,
    team: str,
    set: Tuple[str, str],
    set_secret: Tuple[str, str],
    delete: Tuple[str],
    delete_all_job_properties: bool,
    overwrite_all_job_properties: _io.BufferedReader,
    get: str,
    list: bool,
    rest_api_url: str,
    output: OutputFormat,
):
    if (set or set_secret or delete) and (get or list):
        raise VDKException(
            what="Invalid arguments",
            why="Wrong input. Cannot pass --get or --list at the same time as --set or --set-secret.",
            consequence="Command will abort with error.",
            countermeasure="Fix passed arguments such that get/list are not passed in the same time as set/set-secret.",
        )
    if get and list:
        raise VDKException(
            what="Invalid arguments",
            why="Wrong input. Cannot pass --get at the same time as --list. Choose one of the two.",
            consequence="Command will abort with error",
            countermeasure="Fix passed arguments such that only --list or only --get are used.",
        )
    log.debug(
        f"properties passed options: name: {name}, team: {team}, "
        f"set: {set}, set_secret: {set_secret}, get: {get}, list: {list}, delete: {delete} "
        f"rest_api_url: {rest_api_url}, output: {output}"
    )
    key_value_pairs = _get_key_value_pairs(set, set_secret)
    cmd = JobProperties(rest_api_url, name, team, output)
    if key_value_pairs:
        cmd.update_properties(key_value_pairs)
    if delete:
        cmd.delete_keys(delete)
    if delete_all_job_properties:
        cmd.delete_all_job_properties()
    if get:
        cmd.get(get)
    if list:
        cmd.list()
    if overwrite_all_job_properties:
        json_props_string = overwrite_all_job_properties.read().decode("utf-8")
        try:
            json_props = json.loads(json_props_string)
            cmd.overwrite_properties(json_props)
        except Exception as e:
            raise VDKException(
                "Expected valid json for properties overwrite.",
                "JSON was not valid; error is " + str(e),
                "Operation is aborted. Nothing has been changed.",
                "Fix the file to be a valid json and re-try again.",
            )


def _get_key_value_pairs(set, set_secret):
    key_value_pairs = {}
    if set:
        for key, value in set:
            key_value_pairs[key] = value
    if set_secret:
        for key in set_secret:
            value = click.prompt(f"{key}", hide_input=True)
            key_value_pairs[key] = value
    return key_value_pairs
