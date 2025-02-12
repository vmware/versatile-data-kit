/*
 * Copyright 2023-2025 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.credentials.webhook;

import com.vmware.taurus.service.webhook.WebHookResult;
import lombok.Getter;
import lombok.Setter;
import org.springframework.http.HttpStatus;

@Getter
@Setter
public class CreateOAuthAppWebHookResult extends WebHookResult {

  private String clientId;
  private String clientSecret;

  public CreateOAuthAppWebHookResult(
      HttpStatus status, String message, boolean success, String clientId, String clientSecret) {
    super(status, message, success);
    this.clientId = clientId;
    this.clientSecret = clientSecret;
  }
}
