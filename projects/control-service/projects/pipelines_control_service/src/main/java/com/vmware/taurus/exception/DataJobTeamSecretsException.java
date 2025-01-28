/*
 * Copyright 2023-2025 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.exception;

import org.springframework.http.HttpStatus;

public class DataJobTeamSecretsException extends DomainError implements UserFacingError {

  public DataJobTeamSecretsException(String jobName, String why) {
    super(
        String.format("Exception processing secrets for team '%s'.", jobName),
        why,
        "Unable to process team secrets.",
        "Contact the service operator",
        null);
  }

  @Override
  public HttpStatus getHttpStatus() {
    return HttpStatus.BAD_REQUEST;
  }
}
