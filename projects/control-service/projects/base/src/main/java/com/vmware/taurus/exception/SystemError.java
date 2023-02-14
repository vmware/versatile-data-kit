/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.exception;

/** For user-facing exceptions ({@link UserFacingError}) the HTTP status is likely to be 5xx */
public abstract class SystemError extends TaurusExceptionBase {

  protected SystemError(
      String what, String why, String consequences, String countermeasures, Throwable cause) {
    super(what, why, consequences, countermeasures, cause);
    validate();
  }

  private void validate() {
    if (this instanceof UserFacingError) {
      if (!((UserFacingError) this).getHttpStatus().is5xxServerError()) {
        throw new Bug("User-facing SystemErrors must be associated with a 5xx status code", this);
      }
    }
  }
}
