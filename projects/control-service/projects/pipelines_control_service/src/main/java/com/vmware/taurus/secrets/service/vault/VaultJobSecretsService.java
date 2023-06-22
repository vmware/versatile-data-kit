/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.secrets.service.vault;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.vmware.taurus.exception.DataJobSecretsException;
import com.vmware.taurus.exception.DataJobSecretsSizeLimitException;
import lombok.extern.slf4j.Slf4j;
import org.json.JSONObject;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Service;
import org.springframework.vault.core.VaultOperations;
import org.springframework.vault.support.Versioned;

import java.nio.charset.StandardCharsets;
import java.util.Collections;
import java.util.Map;
import java.util.stream.Collectors;

@Slf4j
@Service
@ConditionalOnProperty(value = "featureflag.vault.integration.enabled")
public class VaultJobSecretsService implements com.vmware.taurus.secrets.service.JobSecretsService {

  //  package private so it can be used in tests
  static final int VAULT_SIZE_LIMIT_DEFAULT = 1048576; // 1 MB
  private static final String SECRET = "secret";

  @Value("${datajobs.vault.size.limit.bytes}")
  private int sizeLimitBytes = VAULT_SIZE_LIMIT_DEFAULT;

  private final ObjectMapper objectMapper = new ObjectMapper();
  private final VaultOperations vaultOperations;

  public VaultJobSecretsService(VaultOperations vaultOperations) {
    this.vaultOperations = vaultOperations;
  }

  @Override
  public void updateJobSecrets(String jobName, Map<String, Object> secrets) {

    checkJobName(jobName);
    checkJobSecretsMap(jobName, secrets);

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

    String updatedSecretsString = new JSONObject(updatedSecrets).toString();
    if (updatedSecretsString.getBytes(StandardCharsets.UTF_8).length > sizeLimitBytes) {
      throw new DataJobSecretsSizeLimitException(
          jobName, "Secret size exceeds configured limit of:" + sizeLimitBytes);
    }

    vaultJobSecrets.setSecretsJson(updatedSecretsString);

    vaultOperations.opsForVersionedKeyValue(SECRET).put(jobName, vaultJobSecrets);
  }

  @Override
  public Map<String, Object> readJobSecrets(String jobName) throws JsonProcessingException {
    checkJobName(jobName);
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

  private void checkJobName(String jobName) {
    if (jobName == null || jobName.isBlank()) {
      throw new DataJobSecretsException(jobName, "Data Job Name cannot be blank");
    }
  }

  private void checkJobSecretsMap(String jobName, Map<String, Object> secrets) {
    if (secrets == null || secrets.isEmpty()) {
      throw new DataJobSecretsException(jobName, "Secrets parameter cannot be null or empty");
    }
  }
}
