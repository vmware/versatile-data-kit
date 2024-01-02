/*
 * Copyright 2021-2024 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.secrets.controller;

import com.vmware.taurus.controlplane.model.api.DataJobsSecretsApi;
import com.vmware.taurus.exception.SecretStorageNotConfiguredException;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.context.annotation.ComponentScan;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

/**
 * This class is used to provide the secrets endpoint in swagger and rest even when secrets support
 * is disabled.
 */
@RestController
@ComponentScan(basePackages = "com.vmware.taurus.secrets")
@Tag(name = "Data Jobs Secrets")
@ConditionalOnProperty(value = "featureflag.vault.integration.enabled", havingValue = "false")
public class NoOpDataJobsSecretsController implements DataJobsSecretsApi {
  @Override
  public ResponseEntity<Void> dataJobSecretsUpdate(
      String teamName, String jobName, String deploymentId, Map<String, Object> requestBody) {
    throw new SecretStorageNotConfiguredException();
  }

  @Override
  public ResponseEntity<Map<String, Object>> dataJobSecretsRead(
      String teamName, String jobName, String deploymentId) {
    throw new SecretStorageNotConfiguredException();
  }
}
