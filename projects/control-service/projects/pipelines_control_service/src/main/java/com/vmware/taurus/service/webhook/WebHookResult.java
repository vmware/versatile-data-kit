/*
 * Copyright 2021-2023 VMware, Inc.
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
