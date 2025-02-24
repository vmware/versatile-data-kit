/*
 * Copyright 2023-2025 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.credentials.webhook;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.Serializable;
import lombok.Data;
import lombok.SneakyThrows;

@Data
public class CreateOAuthAppResponse implements Serializable {
  @JsonProperty("client_id")
  private String clientId;

  @JsonProperty("client_secret")
  private String clientSecret;

  @SneakyThrows
  public String toString() {
    ObjectMapper mapper = new ObjectMapper();
    String jsonBody = mapper.writeValueAsString(this);
    return jsonBody;
  }
}
