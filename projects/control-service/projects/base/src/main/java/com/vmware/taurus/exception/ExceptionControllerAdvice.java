/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.exception;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.web.bind.annotation.ControllerAdvice;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestController;

/** Adds exception handling to Taurus REST controllers */
@ControllerAdvice(annotations = RestController.class)
public class ExceptionControllerAdvice {
  private final Logger log = LoggerFactory.getLogger(this.getClass());

  @ExceptionHandler(TaurusExceptionBase.class)
  public ResponseEntity<ErrorMessage> handleException(TaurusExceptionBase e) {
    HttpStatus httpStatus = HttpStatus.INTERNAL_SERVER_ERROR;
    if (e instanceof UserFacingError) {
      httpStatus = ((UserFacingError) e).getHttpStatus();
    }
    log.error("REST call finished with error: " + e.getMessage(), e);

    return new ResponseEntity<>(e.getErrorMessage(), httpStatus);
  }

  @ExceptionHandler
  public ResponseEntity<ErrorMessage> handleException(Exception e) {
    if (e instanceof HttpMessageNotReadableException) {
      return new ResponseEntity<>(
          new ErrorMessage(
              "An issue with the JSON body of the request was found",
              e.getMessage(),
              "The API call will fail with 400 BAD REQUEST.",
              "Inspect your input and fix the problem."),
          HttpStatus.BAD_REQUEST);
    }
    // Yes, this is a bug. Only TaurusExceptionBase errors should go through the wire.
    return handleException(new Bug(e.getMessage(), e));
  }
}
