# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import sys

import click
from vdk.internal.control.exception.vdk_exception import VDKException
from vdk.internal.control.utils import cli_utils
from vdk.internal.control.utils.cli_utils import extended_option
from vdk.plugin.control_api_auth.auth_exception import VDKAuthException
from vdk.plugin.control_api_auth.auth_exception import VDKInvalidAuthParamError
from vdk.plugin.control_api_auth.authentication import Authentication
from vdk.plugin.control_api_auth.login_types import LoginTypes


@click.command(
    help="Authenticate against the Control Service. The received request token will be cached so no "
    "further login is required. Use logout command to remove the credentials"
    """
Examples:

\b
# Login using interactive login - will open browser to redirect to corporate SSO to login
vdk login

\b
# Login using non-interactive login - in other words using api token (also called refresh token)
vdk login -t api-token -a 3ece313f612db1f03629313d847

\b
For example to setup Oauth2 provider as Google:

First, create a client using https://console.developers.google.com/apis/credentials/oauthclient
redirect_uri should be set to http://127.0.0.1  (without the port)

Execute: vdk login --oauth2-discovery-url https://accounts.google.com/o/oauth2/v2/auth\\?scope\\=profile --oauth2-exchange-url
https://oauth2.googleapis.com/token --client-id 1234-example.apps.googleusercontent.com
--client-secret 1234-example-secret

For the authentication against Control Service to be successful, Control Service must be configured to accept Google access tokens.
"""
)
@click.option(
    "-u",
    "--api-token-authorization-url",
    help="Location of the API Token OAuth2 provider. It is used to exchange api refresh token for access token. "
    "Response should match https://tools.ietf.org/html/rfc6749#section-5.1",
    cls=extended_option(hide_if_default=True),
)
@click.option(
    "-a",
    "--api-token",
    help="API Token for the OAuth2 provider used in exchange for Access Token. "
    "It acts as a 'refresh token' (https://datatracker.ietf.org/doc/html/rfc6749#section-1.5)"
    " - in other words it's used as the credentials used to obtain access tokens. "
    "This request is made against the URL specified by --api-token-authorization-url or the VDK_API_TOKEN_AUTHORIZATION_URL environment variable. "
    'Required when authentication type is "api-token", ignored otherwise. ',
    cls=extended_option(),
)
@click.option(
    "-t",
    "--auth-type",
    help="Type of the authentication (oauth2) api-token or credentials. "
    "credentials type is interactive login - it will redirect to your authentication "
    "provider to login and save access token (and if available a refresh token) locally "
    "and it will be used in future operations. "
    "api-token is non-interactive - you specify api refresh token generated from your authentication "
    "provider. ",
    default=LoginTypes.API_TOKEN.value,
    type=click.Choice(
        [LoginTypes.API_TOKEN.value, LoginTypes.CREDENTIALS.value], case_sensitive=False
    ),
    cls=extended_option(),
)
@click.option(
    "-i",
    "--client-id",
    help="Client ID granted when OAuth2 Application is created. Required for credentials login type."
    "See https://tools.ietf.org/html/rfc6749#section-2.2",
    cls=extended_option(hide_if_default=True),
)
@click.option(
    "-s",
    "--client-secret",
    help="Client Secret granted when OAuth2 Application is created. Required for credentials login type."
    "See https://tools.ietf.org/html/rfc6749#section-2.3.1",
    cls=extended_option(hide_if_default=True),
)
@click.option(
    "-d",
    "--oauth2-discovery-url",
    help="The endpoint which is opened by browser to start the redirection login process."
    "This is the starting point of the OAuth 2.0 flow to authenticate end users. "
    "This authorization endpoint is be used to authenticate users and obtain an authorization code. ",
    cls=extended_option(hide_if_default=True),
)
@click.option(
    "-e",
    "--oauth2-exchange-url",
    help="The point from which authorization code is exchanged for access and refresh tokens."
    "This is the Token endpoint as defined in RFC 6749."
    "Response should match https://tools.ietf.org/html/rfc6749#section-5.1",
    cls=extended_option(hide_if_default=True),
)
@click.pass_context
def login(
    ctx,
    api_token_authorization_url,
    api_token,
    auth_type,
    client_id,
    client_secret,
    oauth2_discovery_url,
    oauth2_exchange_url,
):
    if auth_type == LoginTypes.CREDENTIALS.value:
        try:
            auth = Authentication(
                client_id=client_id,
                client_secret=client_secret,
                auth_discovery_url=oauth2_discovery_url,
                authorization_url=oauth2_exchange_url,
                auth_type=auth_type,
                cache_locally=True,
            )
            auth.authenticate()
            click.echo("Login Successful")
        except VDKInvalidAuthParamError:
            click.echo(
                f"Login type: {auth_type} requires arguments:, --client-secret, --client-id, "
                "--oauth2-exchange-url, --oauth2-discovery-url"
            )
            sys.exit(1)
        except VDKAuthException as e:
            click.echo(f"Login failed. Error was: {e.message}")
            sys.exit(1)

    elif auth_type == LoginTypes.API_TOKEN.value:
        api_token = cli_utils.get_or_prompt("Oauth2 API token", api_token)
        if not api_token:
            raise VDKException(
                what="Login failed",
                why=f"Login type: {auth_type} requires API token",
                consequence=f"Previous login will be used if still valid, "
                f"otherwise operation that require authorization will fail.",
                countermeasure="Please login providing correct API Token. ",
            )
        else:
            apikey_auth = Authentication(
                authorization_url=api_token_authorization_url,
                token=api_token,
                auth_type=auth_type,
                cache_locally=True,
            )
            try:
                apikey_auth.authenticate()
            except VDKAuthException as e:
                click.echo(f"Login failed. Error was: {e.message}")
                sys.exit(1)
            click.echo("Login Successful")
    else:
        click.echo(f"Login type: {auth_type} not supported")
