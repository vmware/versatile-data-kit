/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.exception;

import org.springframework.http.HttpStatus;

public class DataJobSecretsException extends DomainError implements UserFacingError {

  public DataJobSecretsException(String jobName, String why) {
    super(
        String.format("Exception processing secrets for '%s' data job.", jobName),
        why,
        "Unable to process data job secrets.",
        "Try re-creating the data job secrets or contract the service operator",
        null);
  }

  @Override
  public HttpStatus getHttpStatus() {
    return HttpStatus.BAD_REQUEST;
  }
}
