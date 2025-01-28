/*
 * Copyright 2023-2024 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.exception;

/**
 * AuthorizationError class which extends the {@link SystemError} class to follow the exception
 * handling in a proper manner
 */
public class AuthorizationError extends SystemError {
  public AuthorizationError(
      String why, String consequences, String countermeasures, Throwable cause) {
    super("Authorization failed", why, consequences, countermeasures, cause);
  }
}
