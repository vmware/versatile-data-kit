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

public class WebHookRequestError extends TaurusExceptionBase implements UserFacingError {
  private HttpStatus httpStatus;

  public WebHookRequestError(String operationName, String webHookMessage, HttpStatus httpStatus) {
    super(
        String.format(
            "Post %s Web Hook call associated with this request returns client error.",
            operationName),
        webHookMessage,
        String.format(
            "This API call fails with %s and the %s operation will not be completed.",
            httpStatus, operationName),
        "Inspect this message and fix the request to the Web Hook Server.",
        null);
    this.httpStatus = httpStatus;
  }

  @Override
  public HttpStatus getHttpStatus() {
    return httpStatus;
  }
}
