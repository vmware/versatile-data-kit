/*
 * Copyright 2023-2025 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.credentials.webhook;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.vmware.taurus.service.webhook.WebHookRequestBody;
import lombok.Data;
import lombok.EqualsAndHashCode;
import lombok.SneakyThrows;

/** CreateOAuthAppBody class which defines the request body for the create oAuth App webhook */
@Data
@EqualsAndHashCode(callSuper = true)
public class CreateOAuthAppBody extends WebHookRequestBody {

  @JsonProperty(OAUTH_APP_ID)
  private String oauthAppId;

  private static final String OAUTH_APP_ID = "oauth_app_id";

  @SneakyThrows
  public String toString() {
    ObjectMapper mapper = new ObjectMapper();
    String jsonBody = mapper.writeValueAsString(this);
    return jsonBody;
  }
}
