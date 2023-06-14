/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.secrets.service.vault;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.extern.slf4j.Slf4j;
import org.json.JSONObject;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Service;
import org.springframework.vault.core.VaultOperations;
import org.springframework.vault.support.Versioned;

import java.util.Collections;
import java.util.Map;
import java.util.stream.Collectors;

@Slf4j
@Service
@ConditionalOnProperty(value = "featureflag.vault.integration.enabled")
public class VaultJobSecretsService implements com.vmware.taurus.secrets.service.JobSecretsService {

  private static final String SECRET = "secret";

  private final ObjectMapper objectMapper = new ObjectMapper();
  private VaultOperations vaultOperations;

  public VaultJobSecretsService(VaultOperations vaultOperations) {
    this.vaultOperations = vaultOperations;
  }

  @Override
  public void updateJobSecrets(String jobName, Map<String, Object> secrets) {
    Versioned<VaultJobSecrets> readResponse =
        vaultOperations.opsForVersionedKeyValue(SECRET).get(jobName, VaultJobSecrets.class);

    VaultJobSecrets vaultJobSecrets;

    if (readResponse != null && readResponse.hasData()) {
      vaultJobSecrets = readResponse.getData();
    } else {
      vaultJobSecrets = new VaultJobSecrets(jobName, null);
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

    vaultJobSecrets.setSecretsJson(new JSONObject(updatedSecrets).toString());

    vaultOperations.opsForVersionedKeyValue(SECRET).put(jobName, vaultJobSecrets);
  }

  @Override
  public Map<String, Object> readJobSecrets(String jobName) throws JsonProcessingException {
    Versioned<VaultJobSecrets> readResponse =
        vaultOperations.opsForVersionedKeyValue(SECRET).get(jobName, VaultJobSecrets.class);

    VaultJobSecrets vaultJobSecrets;

    if (readResponse != null && readResponse.hasData()) {
      vaultJobSecrets = readResponse.getData();
      return objectMapper.readValue(vaultJobSecrets.getSecretsJson(), Map.class);
    } else {
      return Collections.emptyMap();
    }
  }
}
