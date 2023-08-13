# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os

from traitlets import Unicode
from traitlets.config import Configurable


class VdkJupyterConfig(Configurable):
    oauth2_authorization_url = Unicode(
        os.environ.get("OAUTH2_AUTHORIZATION_URL", ""),
        config=True,
        help="The Oauth2 authorization URL. "
        "This is the URL used to start the authentication process."
        "Used to redirect to the authorization provider for user to login.",
    )
    oauth2_token_url = Unicode(
        os.environ.get("OAUTH2_TOKEN_URL", ""),
        config=True,
        help="The Oauth2 token URL. "
        "Used in the second phase of authentication process. "
        "Used to exchange authorization code with access token.",
    )
    oauth2_client_id = Unicode(
        os.environ.get("OAUTH2_CLIENT_ID", ""),
        config=True,
        help="The Oauth2 client ID. Note that client secret is not specified "
        "since we only support native app workflow with PKCE (RFC 7636)",
    )
    oauth2_redirect_url = Unicode(
        "http://127.0.0.1:8787/vdk-jupyterlab-extension/login2",
        config=True,
        help="The Oauth2 Redirect URL (or callback URL)."
        " This is the URL that authorization provider will redirect back the user to with the authorization code."
        " If empty automatically the request URL will be used.",
    )
    rest_api_url = Unicode(
        os.environ.get("REST_API_URL", ""),
        config=True,
        help="The VDK Control Service REST API URL",
    )
