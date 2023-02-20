/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.exception;

import org.springframework.http.HttpStatus;

public class DataJobExecutionNotFoundException extends DomainError implements UserFacingError {

  public DataJobExecutionNotFoundException(String executionId) {
    super(
        String.format("The Data Job execution '%s' does not exist.", executionId),
        "Likely the Data Job execution have not started or it has expired.",
        "The Data Job execution will not be returned.",
        "Provide a Data Job execution that already exists or trigger one and try again.",
        null);
  }

  @Override
  public HttpStatus getHttpStatus() {
    return HttpStatus.NOT_FOUND;
  }
}
