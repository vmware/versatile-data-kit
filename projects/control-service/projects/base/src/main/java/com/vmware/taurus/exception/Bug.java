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

/** Exception used in cases which are not expected to happen - would mean there is a bug. */
public class Bug extends SystemError implements UserFacingError {
  public Bug(String why, Throwable cause) {
    super(
        "A coding error (bug) was found.",
        why,
        "This call with the current OpId will most likely fail.",
        "Inspect stack trace and either fix the problem or open a GitHub issue for it.",
        cause);
  }

  public static ErrorMessage errorMessage(String why, Throwable cause) {
    return new ErrorMessage(
        "A coding error (bug) was found.",
        why,
        "This call with the current OpId will most likely fail.",
        "Inspect stack trace and either fix the problem or open a GitHub issue for it.");
  }

  @Override
  public HttpStatus getHttpStatus() {
    return HttpStatus.INTERNAL_SERVER_ERROR;
  }
}
