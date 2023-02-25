/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.exception;

import org.springframework.http.HttpStatus;

public class DataJobDeploymentNotFoundException extends DomainError implements UserFacingError {

  public DataJobDeploymentNotFoundException(String jobName) {
    super(
        String.format("The Data Job '%s' is not deployed.", jobName),
        "The Data Job must be deployed.",
        "Operation cannot complete since it expects the data job to have a deployment.",
        "Deploy the Data Job and try again.",
        null);
  }

  @Override
  public HttpStatus getHttpStatus() {
    return HttpStatus.NOT_FOUND;
  }
}
