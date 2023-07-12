/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.servers.Server;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Configuration;

import javax.annotation.PostConstruct;
import java.util.List;

/**
 * This class exists so that we can set the swagger URL explicitly if swagger is not able to infer
 * it correctly.
 */
@Configuration
public class SwaggerConfiguration {

  private final OpenAPI openAPI;

  @Value("${swagger-ui.hostname:}")
  private String serverUrl;

  @Autowired
  public SwaggerConfiguration(OpenAPI openAPI) {
    this.openAPI = openAPI;
  }

  @PostConstruct
  public void setupServerUrl() {
    if (!serverUrl.isEmpty()) {
      openAPI.servers(List.of(new Server().url(serverUrl)));
    }
  }
}
