/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.exception;

import org.springframework.http.HttpStatus;

public interface UserFacingError {
  /**
   * @return the HTTP status that user should see for this exception.
   */
  public abstract HttpStatus getHttpStatus();
}
