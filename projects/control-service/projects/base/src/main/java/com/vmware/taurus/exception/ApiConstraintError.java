/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.exception;

import org.springframework.http.HttpStatus;

/** Exception thrown when parameter validation fails */
public class ApiConstraintError extends DomainError implements UserFacingError {

  /**
   * Describes a new error of this type
   *
   * @param paramName the parameter name that failed validation; must match the name in the API
   *     definition
   * @param paramConstraint human-readable description of required value
   * @param actualValue actual value, can be null
   */
  public ApiConstraintError(String paramName, String paramConstraint, Object actualValue) {
    this(
        paramName,
        paramConstraint,
        actualValue,
        String.format("Provide value that is %s.", paramConstraint));
  }

  public ApiConstraintError(
      String paramName, String paramConstraint, Object actualValue, String countermeasures) {
    super(
        String.format("Parameter %s is not valid.", paramName),
        String.format("It must be %s, but was %s.", paramConstraint, actualValue),
        "API call fails with 400 BAD REQUEST.",
        countermeasures,
        null);
  }

  @Override
  public HttpStatus getHttpStatus() {
    return HttpStatus.BAD_REQUEST;
  }
}
