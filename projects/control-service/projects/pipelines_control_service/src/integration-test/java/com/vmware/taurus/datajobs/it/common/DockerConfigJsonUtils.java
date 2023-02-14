/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs.it.common;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.util.Map;

/** Responsible for creating k8s formatted docker secret. Parameters are secret and the repo. */
public class DockerConfigJsonUtils {
  private static final ObjectMapper objectMapper = new ObjectMapper();

  public static Map<String, String> create(String repo, String secret)
      throws JsonProcessingException {
    return Map.of(
        ".dockerconfigjson",
        objectMapper.writeValueAsString(Map.of("auths", Map.of(repo, Map.of("auth", secret)))));
  }
}
