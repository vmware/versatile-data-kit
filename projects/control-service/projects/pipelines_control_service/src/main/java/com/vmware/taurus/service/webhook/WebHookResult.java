/*
 * Copyright 2023-2024 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.webhook;

import lombok.Builder;
import lombok.Getter;
import org.springframework.http.HttpStatus;

/**
 * WebHookResult class with sole responsibility to leave post operations actions to the client code
 * using webhook invocations.
 */
@Getter
@Builder
public class WebHookResult {
  private final HttpStatus status;
  private final String message;
  private final boolean success;
}
