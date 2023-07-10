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
 * This class exists so that when running quickstart vdk the swagger ui has the correct base url.
 *
 * <p>Without this in qucikstart vdk the swagger will think the url should be localhost:80/.
 *
 * <p>This is not actually correct! We are mapping port 80 from the cluster port 8092 on the local
 * machine. There is no way for the service to know this mapping is happening so we need to provide
 * it with the correct url.
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
  public void dd() {
    if (!serverUrl.isEmpty()) {
      openAPI.servers(List.of(new Server().url(serverUrl)));
    }
  }
}
