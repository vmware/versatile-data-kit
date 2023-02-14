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

public class JsonDissectException extends DomainError implements UserFacingError {
  public JsonDissectException(Throwable cause) {
    super(
        "Control service failed to parse provided arguments to a valid JSON string.",
        String.format("The internal parser threw an exception because: %s", cause.getMessage()),
        "The requested system call will not complete.",
        "Inspect the cause and re-try the call with arguments that can be parsed to JSON.",
        cause);
  }

  @Override
  public HttpStatus getHttpStatus() {
    return HttpStatus.BAD_REQUEST;
  }
}
