/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.authorization.webhook;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.vmware.taurus.service.webhook.WebHookRequestBody;
import lombok.Data;
import lombok.EqualsAndHashCode;
import lombok.SneakyThrows;

/** AuthorizationBody class which defines the request body for the authorization webhook */
@Data
@EqualsAndHashCode(callSuper = true)
public class AuthorizationBody extends WebHookRequestBody {

  @JsonProperty(REQUESTED_PERMISSION)
  private String requestedPermission;

  private static final String REQUESTED_PERMISSION = "requested_permission";

  @SneakyThrows
  public String toString() {
    ObjectMapper mapper = new ObjectMapper();
    String jsonBody = mapper.writeValueAsString(this);
    return jsonBody;
  }
}
