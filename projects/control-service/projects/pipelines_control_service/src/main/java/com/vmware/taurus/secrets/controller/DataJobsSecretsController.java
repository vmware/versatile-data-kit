/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.secrets.controller;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.vmware.taurus.controlplane.model.api.DataJobsPropertiesApi;
import com.vmware.taurus.controlplane.model.api.DataJobsSecretsApi;
import com.vmware.taurus.properties.service.PropertiesService;
import com.vmware.taurus.secrets.service.SecretsService;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.context.annotation.ComponentScan;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

import java.util.Map;

@RestController
@ComponentScan(basePackages = "com.vmware.taurus.secrets")
@Tag(name = "Data Jobs Secrets")
public class DataJobsSecretsController implements DataJobsSecretsApi {
  static Logger log = LoggerFactory.getLogger(DataJobsSecretsController.class);

  @Override
  public ResponseEntity<Void> dataJobSecretsUpdate(
      String teamName, String jobName, String deploymentId, Map<String, Object> requestBody) {
    log.debug("Updating secrets for job: {}", jobName);
    throw new ResponseStatusException(
            HttpStatus.NOT_IMPLEMENTED, "Secrets service is not implemented");
  }

  @Override
  public ResponseEntity<Map<String, Object>> dataJobSecretsRead(
      String teamName, String jobName, String deploymentId) {
    log.debug("Reading secrets for job: {}", jobName);
    throw new ResponseStatusException(
            HttpStatus.NOT_IMPLEMENTED, "Secrets service is not implemented");
  }
}
