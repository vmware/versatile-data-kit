/*
 * Copyright 2023-2025 Broadcom
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
