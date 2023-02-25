/*
 * Copyright 2021-2023 VMware, Inc.
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
