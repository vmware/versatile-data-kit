/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.webhook;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.Data;
import lombok.SneakyThrows;

import java.io.Serializable;

/**
 * WebHookRequestBody class which defines the request body for the various post operation webhooks
 */
@Data
public class WebHookRequestBody implements Serializable {

  @JsonProperty(REQUESTER_USER_ID)
  private String requesterUserId;

  @JsonProperty(REQUESTED_RESOURCE_TEAM)
  private String requestedResourceTeam;

  @JsonProperty(REQUESTED_RESOURCE_NAME)
  private String requestedResourceName;

  @JsonProperty(REQUESTED_RESOURCE_ID)
  private String requestedResourceId;

  @JsonProperty(REQUESTED_HTTP_PATH)
  private String requestedHttpPath;

  @JsonProperty(REQUESTED_HTTP_VERB)
  private String requestedHttpVerb;

  @JsonProperty(REQUESTED_RESOURCE_NEW_TEAM)
  private String requestedResourceNewTeam;

  private static final String REQUESTER_USER_ID = "requester_user_id";
  private static final String REQUESTED_RESOURCE_TEAM = "requested_resource_team";
  private static final String REQUESTED_RESOURCE_NAME = "requested_resource_name";
  private static final String REQUESTED_RESOURCE_ID = "requested_resource_id";
  private static final String REQUESTED_HTTP_PATH = "requested_http_path";
  private static final String REQUESTED_HTTP_VERB = "requested_http_verb";
  private static final String REQUESTED_RESOURCE_NEW_TEAM = "requested_resource_new_team";

  @SneakyThrows
  public String toString() {
    ObjectMapper mapper = new ObjectMapper();
    String jsonBody = mapper.writeValueAsString(this);
    return jsonBody;
  }
}
