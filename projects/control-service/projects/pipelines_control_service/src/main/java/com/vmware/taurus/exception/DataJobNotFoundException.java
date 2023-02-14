/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.exception;

import org.springframework.http.HttpStatus;

public class DataJobNotFoundException extends DomainError implements UserFacingError {

  public DataJobNotFoundException(String jobName) {
    super(
        String.format("The Data Job '%s' does not exist.", jobName),
        "The Data Job must be existing.",
        "The Data Job will not be started.",
        "Provide a Data Job that already exists or create a new one and try again.",
        null);
  }

  @Override
  public HttpStatus getHttpStatus() {
    return HttpStatus.NOT_FOUND;
  }
}
