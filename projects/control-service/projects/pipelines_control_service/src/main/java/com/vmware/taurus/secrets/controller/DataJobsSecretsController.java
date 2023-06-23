/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.secrets.controller;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.vmware.taurus.controlplane.model.api.DataJobsSecretsApi;
import com.vmware.taurus.exception.DataJobSecretsException;
import com.vmware.taurus.secrets.service.JobSecretsService;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.context.annotation.ComponentScan;
import org.springframework.http.ResponseEntity;
import org.springframework.lang.Nullable;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
@ComponentScan(basePackages = "com.vmware.taurus.secrets")
@Tag(name = "Data Jobs Secrets")
@ConditionalOnProperty(value = "featureflag.vault.integration.enabled")
public class DataJobsSecretsController implements DataJobsSecretsApi {
  static Logger log = LoggerFactory.getLogger(DataJobsSecretsController.class);

  private final JobSecretsService secretsService;

  @Autowired
  public DataJobsSecretsController(@Nullable JobSecretsService secretsService) {
    this.secretsService = secretsService;
  }

  @Override
  public ResponseEntity<Void> dataJobSecretsUpdate(
      String teamName, String jobName, String deploymentId, Map<String, Object> requestBody) {
    log.debug("Updating secrets for job: {}", jobName);

    secretsService.updateJobSecrets(jobName, requestBody);
    return ResponseEntity.noContent().build();
  }

  @Override
  public ResponseEntity<Map<String, Object>> dataJobSecretsRead(
      String teamName, String jobName, String deploymentId) {
    log.debug("Reading secrets for job: {}", jobName);

    try {
      return ResponseEntity.ok(secretsService.readJobSecrets(jobName));
    } catch (JsonProcessingException e) {
      log.error("Error while parsing secrets for job: " + jobName, e);
      throw new DataJobSecretsException(jobName, "Error while parsing secrets for job");
    }
  }
}
