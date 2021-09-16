# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from vdk.internal import test_utils
from vdk.internal.control.auth.redirect_auth import RedirectAuthentication


# TODO: extend unit tests
def test_verify_redirect_url():
    test_utils.allow_oauthlib_insecure_transport()
    auth = RedirectAuthentication(
        "client-id",
        "client-secret",
        "http://discovery-url",
        "http://exchange-url",
        "http://127.0.0.1",
        9999,
    )
    authorization_url = auth._create_authorization_redirect_url()
    assert (
        authorization_url[0]
        == "http://discovery-url?response_type=code&client_id=client-id&redirect_uri=http%3A%2F%2F127.0.0.1%3A9999&state=requested&prompt=login"
    )
    assert authorization_url[1] == "requested"
