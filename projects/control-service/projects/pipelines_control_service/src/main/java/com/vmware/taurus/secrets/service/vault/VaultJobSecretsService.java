/*
 * Copyright 2023-2024 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.secrets.service.vault;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.vmware.taurus.exception.DataJobSecretsException;
import com.vmware.taurus.exception.DataJobSecretsSizeLimitException;
import com.vmware.taurus.exception.DataJobTeamSecretsException;
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
  public static final String TEAM_OAUTH_CREDENTIALS = "team-oauth-credentials";

  @Value("${datajobs.vault.size.limit.bytes}")
  private int sizeLimitBytes = VAULT_SIZE_LIMIT_DEFAULT;

  private final ObjectMapper objectMapper = new ObjectMapper();
  private final VaultOperations vaultOperations;

  public VaultJobSecretsService(VaultOperations vaultOperations) {
    this.vaultOperations = vaultOperations;
  }

  @Override
  public void updateJobSecrets(String teamName, String jobName, Map<String, Object> secrets) {

    checkInputs(teamName, jobName);

    String secretKey = teamName + "/" + jobName;

    Versioned<VaultJobSecrets> readResponse =
        vaultOperations.opsForVersionedKeyValue(SECRET).get(secretKey, VaultJobSecrets.class);

    VaultJobSecrets vaultJobSecrets;

    if (readResponse != null && readResponse.hasData()) {
      vaultJobSecrets = readResponse.getData();
    } else {
      vaultJobSecrets = new VaultJobSecrets(secretKey, null);
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
              secretKey, "Secret size exceeds configured limit of:" + sizeLimitBytes);
    }

    vaultJobSecrets.setSecretsJson(updatedSecretsString);

    vaultOperations.opsForVersionedKeyValue(SECRET).put(secretKey, vaultJobSecrets);
  }

  @Override
  public Map<String, Object> readJobSecrets(String teamName, String jobName) throws JsonProcessingException {
    checkInputs(teamName, jobName);

    String secretKey = teamName + "/" + jobName;

    Versioned<VaultJobSecrets> readResponse =
        vaultOperations.opsForVersionedKeyValue(SECRET).get(secretKey, VaultJobSecrets.class);

    VaultJobSecrets vaultJobSecrets;

    if (readResponse != null && readResponse.hasData()) {
      vaultJobSecrets = readResponse.getData();
      return objectMapper.readValue(vaultJobSecrets.getSecretsJson(), Map.class);
    } else {
      return Collections.emptyMap();
    }
  }

  @Override
  public void updateTeamOauthCredentials(String teamName, String clientId, String clientSecret) {
    checkInputs(teamName, clientId, clientSecret);

    String secretKey = teamName + "/" + TEAM_OAUTH_CREDENTIALS;

    VaultTeamCredentials teamCredentials = new VaultTeamCredentials(teamName, clientId, clientSecret);

    vaultOperations.opsForVersionedKeyValue(SECRET).put(secretKey, teamCredentials);
  }

  @Override
  public VaultTeamCredentials readTeamOauthCredentials(String teamName) {
    checkInputs(teamName);

    String secretKey = teamName + "/" + TEAM_OAUTH_CREDENTIALS;

    Versioned<VaultTeamCredentials> readResponse =
            vaultOperations.opsForVersionedKeyValue(SECRET).get(secretKey, VaultTeamCredentials.class);

    if (readResponse != null && readResponse.hasData()) {
      return readResponse.getData();
    } else {
      throw new DataJobTeamSecretsException(teamName, "Cannot retrieve OAuth Credentials for team:" + teamName);
    }
  }

  private void checkInputs(String teamName) {
    if (teamName == null || teamName.isBlank()) {
      throw new DataJobTeamSecretsException(teamName, "Team Name cannot be blank");
    }
  }

  private void checkInputs(String teamName, String jobName) {
    if (teamName == null || teamName.isBlank()) {
      throw new DataJobSecretsException(teamName, "Team Name cannot be blank");
    }
    if (jobName == null || jobName.isBlank()) {
      throw new DataJobSecretsException(jobName, "Data Job Name cannot be blank");
    }
  }

  private void checkInputs(String teamName, String clientId, String clientSecret) {
    if (teamName == null || teamName.isBlank()) {
      throw new DataJobTeamSecretsException(teamName, "Team Name cannot be blank");
    }
    if (clientId == null || clientId.isBlank()) {
      throw new DataJobTeamSecretsException(clientId, "ClientId cannot be blank");
    }
    if (clientSecret == null || clientSecret.isBlank()) {
      throw new DataJobTeamSecretsException(clientSecret, "ClientSecret cannot be blank");
    }
  }
}
