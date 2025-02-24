/*
 * Copyright 2023-2025 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.exception;

import org.springframework.http.HttpStatus;

/** Exception thrown, when a secret storage has not been configured */
public class SecretStorageNotConfiguredException extends ExternalSystemError {

  public SecretStorageNotConfiguredException() {
    super(MainExternalSystem.SECRETS, "Not Configured");
  }

  @Override
  public HttpStatus getHttpStatus() {
    return HttpStatus.NOT_IMPLEMENTED;
  }
}
