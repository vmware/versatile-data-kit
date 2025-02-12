/*
 * Copyright 2023-2025 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.secrets.service.vault;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.vmware.taurus.exception.DataJobSecretsException;
import com.vmware.taurus.exception.DataJobSecretsSizeLimitException;
import com.vmware.taurus.exception.DataJobTeamSecretsException;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.jetbrains.annotations.NotNull;
import org.json.JSONObject;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Service;
import org.springframework.vault.core.VaultOperations;
import org.springframework.vault.support.Versioned;

import java.nio.charset.StandardCharsets;
import java.util.Collections;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

@Slf4j
@Service
@ConditionalOnProperty(value = "featureflag.vault.integration.enabled")
public class VaultJobSecretsService implements com.vmware.taurus.secrets.service.JobSecretsService {

  //  package private so it can be used in tests
  static final int VAULT_SIZE_LIMIT_DEFAULT = 1048576; // 1 MB

  // make the kv store configurable as some users might want to use something different than secrets
  @Value("${vdk.vault.kvstore:secret}")
  String kvStore;

  @Value("${vdk.vault.kvstoremeta:secret/metadata/}")
  String kvStoreMeta;

  public static final String TEAM_OAUTH_CREDENTIALS = "team-oauth-credentials";

  @Value("${datajobs.vault.size.limit.bytes}")
  private int sizeLimitBytes = VAULT_SIZE_LIMIT_DEFAULT;

  private final ObjectMapper objectMapper = new ObjectMapper();
  private final VaultOperations vaultOperations;

  private final ConcurrentHashMap<String, VaultTeamCredentials> teamIdToCredentialsCache;
  private final ConcurrentHashMap<String, String> clientIdToTeamIdCache;

  public VaultJobSecretsService(VaultOperations vaultOperations) {
    this.vaultOperations = vaultOperations;
    this.teamIdToCredentialsCache = new ConcurrentHashMap<>();
    this.clientIdToTeamIdCache = new ConcurrentHashMap<>();
  }

  @Override
  public void updateJobSecrets(String teamName, String jobName, Map<String, Object> secrets) {

    checkInputs(teamName, jobName);

    String secretKey = getJobSecretKey(teamName, jobName);

    Versioned<VaultJobSecrets> readResponse =
        vaultOperations.opsForVersionedKeyValue(kvStore).get(secretKey, VaultJobSecrets.class);

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

    vaultOperations.opsForVersionedKeyValue(kvStore).put(secretKey, vaultJobSecrets);
  }

  @Override
  public Map<String, Object> readJobSecrets(String teamName, String jobName)
      throws JsonProcessingException {
    checkInputs(teamName, jobName);

    String secretKey = getJobSecretKey(teamName, jobName);

    Versioned<VaultJobSecrets> readResponse =
        vaultOperations.opsForVersionedKeyValue(kvStore).get(secretKey, VaultJobSecrets.class);

    VaultJobSecrets vaultJobSecrets;

    if (readResponse != null && readResponse.hasData()) {
      vaultJobSecrets = readResponse.getData();
      return objectMapper.readValue(vaultJobSecrets.getSecretsJson(), Map.class);
    } else {
      return Collections.emptyMap();
    }
  }

  private static @NotNull String getJobSecretKey(String teamName, String jobName) {
    String secretKey = teamName + "/" + jobName;
    return secretKey;
  }

  @Override
  public void updateTeamOauthCredentials(String teamName, String clientId, String clientSecret) {
    checkInputs(teamName, clientId, clientSecret);

    String secretKey = getTeamSecretKey(teamName);

    VaultTeamCredentials teamCredentials =
        new VaultTeamCredentials(teamName, clientId, clientSecret);

    vaultOperations.opsForVersionedKeyValue(kvStore).put(secretKey, teamCredentials);
    clientIdToTeamIdCache.put(teamCredentials.getClientId(), teamName);
    teamIdToCredentialsCache.put(teamName, teamCredentials);
  }

  @Override
  public VaultTeamCredentials readTeamOauthCredentials(String teamName) {
    checkInputs(teamName);
    if (teamIdToCredentialsCache.containsKey(teamName)) {
      return teamIdToCredentialsCache.get(teamName);
    } else {
      String secretKey = getTeamSecretKey(teamName);

      Versioned<VaultTeamCredentials> readResponse =
          vaultOperations
              .opsForVersionedKeyValue(kvStore)
              .get(secretKey, VaultTeamCredentials.class);

      if (readResponse != null && readResponse.hasData()) {
        VaultTeamCredentials teamCredentials = readResponse.getData();
        clientIdToTeamIdCache.put(teamCredentials.getClientId(), teamName);
        teamIdToCredentialsCache.put(teamName, teamCredentials);
        return teamCredentials;
      } else {
        return null;
      }
    }
  }

  public String getTeamIdForClientId(String clientId) {
    // Check the cache
    if (clientIdToTeamIdCache.containsKey(clientId)) {
      return clientIdToTeamIdCache.get(clientId);
    } else {
      // Search through all team entries in Vault
      try {
        var response = vaultOperations.list(kvStoreMeta);
        if (response != null) {
          for (String teamId : response) {
            teamId = StringUtils.removeEnd(teamId, "/");
            VaultTeamCredentials credentials = readTeamOauthCredentials(teamId);
            if (credentials != null && credentials.getClientId().equals(clientId)) {
              clientIdToTeamIdCache.put(clientId, credentials.getTeamName());
              teamIdToCredentialsCache.put(credentials.getTeamName(), credentials);
              return teamId;
            }
          }
        }
      } catch (Exception e) {
        log.error("Error fetching team ID for client ID: " + clientId, e);
      }
      return null;
    }
  }

  private static @NotNull String getTeamSecretKey(String teamName) {
    String secretKey = teamName + "/" + TEAM_OAUTH_CREDENTIALS;
    return secretKey;
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
