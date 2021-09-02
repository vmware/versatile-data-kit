# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import base64
import hashlib
import os
import re


class AuthPkce:
    @staticmethod
    def generate_pkce_codes():
        """
        Generate PKCE code challenge and code verifier necessary during Authorization Code Workflow
        as described in RFC 7636 (see  https://tools.ietf.org/html/rfc7636)
        :return: code_verifier, code_challenge, code_challenge_method
        """
        code_verifier = base64.urlsafe_b64encode(os.urandom(40)).decode("utf-8")
        code_verifier = re.sub("[^a-zA-Z0-9]+", "", code_verifier)
        code_challenge = hashlib.sha256(code_verifier.encode("utf-8")).digest()
        code_challenge = base64.urlsafe_b64encode(code_challenge).decode("utf-8")
        code_challenge = code_challenge.replace("=", "")
        return code_verifier, code_challenge, "S256"
