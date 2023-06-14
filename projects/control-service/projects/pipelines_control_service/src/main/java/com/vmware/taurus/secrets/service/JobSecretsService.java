/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.secrets.service;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.vmware.taurus.base.FeatureFlags;
import lombok.extern.slf4j.Slf4j;
import org.json.JSONObject;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Service;
import org.springframework.vault.authentication.TokenAuthentication;
import org.springframework.vault.client.VaultEndpoint;
import org.springframework.vault.core.VaultOperations;
import org.springframework.vault.core.VaultTemplate;
import org.springframework.vault.support.Versioned;

import java.net.URI;
import java.net.URISyntaxException;
import java.util.Collections;
import java.util.Map;
import java.util.stream.Collectors;

@Slf4j
@Service
//@ConditionalOnProperty(value = "featureflag.vault.integration.enabled")
public class JobSecretsService {

  private static final String SECRET = "secret";

  private final ObjectMapper objectMapper = new ObjectMapper();
  private VaultOperations vaultOperations;

  public JobSecretsService(VaultOperations vaultOperations){
      this.vaultOperations = vaultOperations;
  }

  public void updateJobSecrets(String jobName, Map<String, Object> secrets) {
    Versioned<JobSecrets> readResponse =
        vaultOperations.opsForVersionedKeyValue(SECRET).get(jobName, JobSecrets.class);

    JobSecrets jobSecrets;

    if (readResponse != null && readResponse.hasData()) {
      jobSecrets = readResponse.getData();
    } else {
      jobSecrets = new JobSecrets(jobName, null);
    }

    var updatedSecrets =
        secrets.entrySet().stream()
            .collect(
                Collectors.toMap(
                    Map.Entry::getKey,
                    entry -> {
                      if (entry.getValue() == null) {
                        entry.setValue(JSONObject.NULL);
                      }
                      return entry.getValue();
                    }));

    jobSecrets.setSecretsJson(new JSONObject(updatedSecrets).toString());

    vaultOperations.opsForVersionedKeyValue(SECRET).put(jobName, jobSecrets);
  }

  public Map<String, Object> readJobSecrets(String jobName) throws JsonProcessingException {
    Versioned<JobSecrets> readResponse =
        vaultOperations.opsForVersionedKeyValue(SECRET).get(jobName, JobSecrets.class);

    JobSecrets jobSecrets;

    if (readResponse != null && readResponse.hasData()) {
      jobSecrets = readResponse.getData();
      return objectMapper.readValue(jobSecrets.getSecretsJson(), Map.class);
    } else {
      return Collections.emptyMap();
    }
  }
}
