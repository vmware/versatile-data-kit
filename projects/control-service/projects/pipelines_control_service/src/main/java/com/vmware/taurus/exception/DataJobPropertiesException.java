/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.exception;

import org.springframework.http.HttpStatus;

public class DataJobPropertiesException extends DomainError implements UserFacingError {

  public DataJobPropertiesException(String jobName, String why) {
    super(
        String.format("Error processing properties for '%s' data job.", jobName),
        why,
        "Unable to process data job properties.",
        "Try re-creating the data job properties or contract the service operator",
        null);
  }

  @Override
  public HttpStatus getHttpStatus() {
    return HttpStatus.BAD_REQUEST;
  }
}
