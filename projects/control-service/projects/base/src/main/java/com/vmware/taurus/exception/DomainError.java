/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.exception;

/** For user-facing exceptions ({@link UserFacingError}) the HTTP status is likely to be 4xx */
public class DomainError extends TaurusExceptionBase {
  public DomainError(
      String what, String why, String consequences, String countermeasures, Throwable cause) {
    super(what, why, consequences, countermeasures, null);
    validate();
  }

  private void validate() {
    if (this instanceof UserFacingError) {
      if (!((UserFacingError) this).getHttpStatus().is4xxClientError()) {
        throw new Bug("User-facing DomainErrors must be associated with a 4xx status code", this);
      }
    }
  }
}
