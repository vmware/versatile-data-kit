/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.exception;

import org.springframework.http.HttpStatus;

public class DataJobAlreadyRunningException extends DomainError implements UserFacingError {

  public DataJobAlreadyRunningException(String jobName) {
    super(
        String.format("The Data Job '%s' is currently being executed.", jobName),
        "Simultaneous execution of the same Data Job are not allowed.",
        "The Data Job will not be started. The ongoing Data Job execution will continue to run.",
        "Wait for the current Data Job execution to complete or cancel it and try again.",
        null);
  }

  @Override
  public HttpStatus getHttpStatus() {
    return HttpStatus.CONFLICT;
  }
}
