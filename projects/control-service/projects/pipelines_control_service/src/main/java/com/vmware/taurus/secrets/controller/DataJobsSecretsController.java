/*
 * Copyright 2023-2025 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.secrets.controller;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.vmware.taurus.controlplane.model.api.DataJobsSecretsApi;
import com.vmware.taurus.controlplane.model.data.OauthCredentials;
import com.vmware.taurus.controlplane.model.data.OauthTeamClientId;
import com.vmware.taurus.controlplane.model.data.OauthTeamCredentials;
import com.vmware.taurus.exception.DataJobSecretsException;
import com.vmware.taurus.secrets.service.JobSecretsService;
import com.vmware.taurus.secrets.service.vault.VaultTeamCredentials;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.context.annotation.ComponentScan;
import org.springframework.http.ResponseEntity;
import org.springframework.lang.Nullable;
import org.springframework.web.bind.annotation.RestController;

import java.util.ArrayList;
import java.util.List;
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
    log.debug("Updating secrets for job: {} - {}", teamName, jobName);

    secretsService.updateJobSecrets(teamName, jobName, requestBody);
    return ResponseEntity.accepted().build();
  }

  @Override
  public ResponseEntity<Map<String, Object>> dataJobSecretsRead(
      String teamName, String jobName, String deploymentId) {
    log.debug("Reading secrets for job: {} - {}", teamName, jobName);

    try {
      return ResponseEntity.ok(secretsService.readJobSecrets(teamName, jobName));
    } catch (JsonProcessingException e) {
      log.error("Error while parsing secrets for job: " + jobName, e);
      throw new DataJobSecretsException(jobName, "Error while parsing secrets for job");
    }
  }

  @Override
  public ResponseEntity<OauthTeamClientId> clientIdGet(String teamName) {
    log.debug("Getting oauth ClientID for team: {}", teamName);
    VaultTeamCredentials teamCredentials = secretsService.readTeamOauthCredentials(teamName);
    if (teamCredentials != null) {
      OauthTeamClientId response = new OauthTeamClientId(teamName, teamCredentials.getClientId());
      return ResponseEntity.ok(response);
    }
    return ResponseEntity.notFound().build();
  }

  @Override
  public ResponseEntity<OauthTeamCredentials> oauthCredentialsGet(String teamName) {
    log.debug("Getting oauth credentials for team: {}", teamName);
    VaultTeamCredentials teamCredentials = secretsService.readTeamOauthCredentials(teamName);
    if (teamCredentials != null) {
      OauthTeamCredentials response =
          new OauthTeamCredentials(
              teamName, teamCredentials.getClientId(), teamCredentials.getClientSecret());
      return ResponseEntity.ok(response);
    }
    return ResponseEntity.notFound().build();
  }

  @Override
  public ResponseEntity<Void> oauthCredentialsPut(
      String teamName, OauthCredentials oauthCredentials) {
    secretsService.updateTeamOauthCredentials(
        teamName, oauthCredentials.getClientId(), oauthCredentials.getClientSecret());
    return ResponseEntity.accepted().build();
  }

  @Override
  public ResponseEntity<List<OauthTeamClientId>> getTeamIdsForClientIds(List<String> requestBody) {
    List<OauthTeamClientId> response = new ArrayList<>();
    for (String clientId : requestBody) {
      String teamName = secretsService.getTeamIdForClientId(clientId);
      if (teamName != null) {
        response.add(new OauthTeamClientId(teamName, clientId));
      }
    }
    return ResponseEntity.ok(response);
  }
}
