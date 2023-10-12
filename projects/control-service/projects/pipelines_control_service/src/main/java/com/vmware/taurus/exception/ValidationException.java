/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.exception;

import org.springframework.http.HttpStatus;

import java.util.Set;

public class ValidationException extends DomainError implements UserFacingError {
    public ValidationException(String what, String why, String consequences, String countermeasures) {
        super(what, why, consequences, countermeasures, null);
    }

    @Override
    public HttpStatus getHttpStatus() {
        return HttpStatus.BAD_REQUEST;
    }
}
