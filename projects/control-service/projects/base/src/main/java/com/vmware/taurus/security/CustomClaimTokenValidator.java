/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.security;

import org.springframework.security.oauth2.core.OAuth2Error;
import org.springframework.security.oauth2.core.OAuth2ErrorCodes;
import org.springframework.security.oauth2.core.OAuth2TokenValidator;
import org.springframework.security.oauth2.core.OAuth2TokenValidatorResult;
import org.springframework.security.oauth2.jwt.Jwt;

import java.util.Set;

/**
 * A JWT Token Validator that checks if the caller is allowed to access a
 * resource based on a claim in the token. The name of the claim and the
 * allowed values are configurable.
 */
public class CustomClaimTokenValidator implements OAuth2TokenValidator<Jwt> {

    private final String customClaimName;
    private final Set<String> authorizedCustomClaimValues;

    public CustomClaimTokenValidator(String customClaimName, Set<String> authorizedCustomClaimValues) {
        this.customClaimName = customClaimName;
        this.authorizedCustomClaimValues = authorizedCustomClaimValues;
    }

    @Override
    public OAuth2TokenValidatorResult validate(Jwt jwt) {
        if (customClaimName.isEmpty() || authorizedCustomClaimValues.isEmpty()) {
            return OAuth2TokenValidatorResult.success();
        }

        String customClaimValue = jwt.getClaim(customClaimName);
        if (authorizedCustomClaimValues.contains(customClaimValue)) {
            return OAuth2TokenValidatorResult.success();
        }

        OAuth2Error err = new OAuth2Error(
                OAuth2ErrorCodes.INSUFFICIENT_SCOPE,
                "The request requires higher privileges than provided by the access token.",
                null);

        return OAuth2TokenValidatorResult.failure(err);
    }
}
