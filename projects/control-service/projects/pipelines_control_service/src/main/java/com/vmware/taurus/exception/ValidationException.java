/*
 * Copyright 2023-2025 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.exception;

import org.springframework.http.HttpStatus;

public class ValidationException extends DomainError implements UserFacingError {
  public ValidationException(String what, String why, String consequences, String countermeasures) {
    super(what, why, consequences, countermeasures, null);
  }

  @Override
  public HttpStatus getHttpStatus() {
    return HttpStatus.BAD_REQUEST;
  }
}
