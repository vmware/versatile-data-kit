/*
 * Copyright 2023-2025 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.secrets.vault;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.exception.DataJobSecretsException;
import com.vmware.taurus.exception.DataJobSecretsSizeLimitException;
import com.vmware.taurus.exception.DataJobTeamSecretsException;
import com.vmware.taurus.secrets.service.vault.VaultJobSecrets;
import com.vmware.taurus.secrets.service.vault.VaultJobSecretsService;
import com.vmware.taurus.secrets.service.vault.VaultTeamCredentials;
import org.apache.commons.lang3.RandomStringUtils;
import org.hamcrest.CoreMatchers;
import org.junit.Assert;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.TestPropertySource;
import org.springframework.test.context.junit.jupiter.SpringExtension;
import org.springframework.test.util.ReflectionTestUtils;
import org.springframework.vault.core.VaultTemplate;
import org.springframework.vault.core.VaultVersionedKeyValueOperations;
import org.springframework.vault.support.Versioned;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static com.vmware.taurus.secrets.service.vault.VaultJobSecretsService.TEAM_OAUTH_CREDENTIALS;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertThrowsExactly;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@ExtendWith(SpringExtension.class)
@SpringBootTest(classes = ControlplaneApplication.class)
@TestPropertySource(
    properties = {
      "datajobs.vault.size.limit.bytes=1048576",
      "vdk.vault.kvstore=secret",
      "vdk.vault.kvstoremeta=secret/metadata/",
    })
class VaultJobSecretsServiceTest {

  private static final String SECRET = "secret";
  private static final String SECRET_META = "secret/metadata/";

  @Mock private VaultTemplate vaultTemplate;
  @Mock private VaultVersionedKeyValueOperations vaultOperations;

  @InjectMocks private VaultJobSecretsService secretsService;

  @BeforeEach
  public void setUp() {
    ReflectionTestUtils.setField(secretsService, "kvStore", "secret");
    ReflectionTestUtils.setField(secretsService, "kvStoreMeta", "secret/metadata/");
  }

  @Test
  void testUpdateJobSecrets() throws JsonProcessingException {
    String jobName = "testJob";
    String teamName = "testTeam";
    String secretKey = teamName + "/" + jobName;
    Map<String, Object> secrets = new HashMap<>();
    secrets.put("key1", "value1");
    secrets.put("key2", 123);
    secrets.put("key3", true);
    secrets.put("key4", null);

    when(vaultTemplate.opsForVersionedKeyValue(SECRET)).thenReturn(vaultOperations);
    when(vaultOperations.get(secretKey, VaultJobSecrets.class)).thenReturn(null);

    Map<String, Object> initial = secretsService.readJobSecrets(teamName, jobName);
    assertNotEquals(secrets, initial);

    VaultJobSecrets vaultJobSecrets =
        new VaultJobSecrets(jobName, "{\"key1\":\"ala-bala\",\"key3\":null}");
    Versioned<VaultJobSecrets> readResponse = Versioned.create(vaultJobSecrets);

    when(vaultOperations.get(secretKey, VaultJobSecrets.class)).thenReturn(readResponse);
    secretsService.updateJobSecrets(teamName, jobName, secrets);

    vaultJobSecrets =
        new VaultJobSecrets(
            jobName, "{\"key1\":\"value1\",\"key2\":123,\"key3\":true,\"key4\":null}");
    readResponse = Versioned.create(vaultJobSecrets);

    when(vaultOperations.get(secretKey, VaultJobSecrets.class)).thenReturn(readResponse);

    Map<String, Object> result = secretsService.readJobSecrets(teamName, jobName);
    assertEquals(secrets, result);
  }

  @Test
  void testUpdateJobSecretsLimit() throws JsonProcessingException {
    String jobName = "testJob";
    String teamName = "testTeam";
    String secretKey = teamName + "/" + jobName;
    Map<String, Object> secrets = new HashMap<>();
    secrets.put("key1", "value1");
    secrets.put("key2", RandomStringUtils.randomAlphabetic(1025 * 1025));

    when(vaultTemplate.opsForVersionedKeyValue(SECRET)).thenReturn(vaultOperations);

    VaultJobSecrets vaultJobSecrets =
        new VaultJobSecrets(jobName, "{\"key1\":\"ala-bala\",\"key3\":null}");
    Versioned<VaultJobSecrets> readResponse = Versioned.create(vaultJobSecrets);

    when(vaultOperations.get(secretKey, VaultJobSecrets.class)).thenReturn(readResponse);

    assertThrows(
        DataJobSecretsSizeLimitException.class,
        () -> secretsService.updateJobSecrets(teamName, jobName, secrets));
  }

  @Test
  void testUpdateJobSecretsNulls() throws JsonProcessingException {
    String jobName = "testJob";
    String teamName = "testTeam";
    String blankJobName = " ";
    String nullJobName = null;
    Map<String, Object> secrets = new HashMap<>();

    Throwable t =
        assertThrows(
            DataJobSecretsException.class,
            () -> secretsService.updateJobSecrets(teamName, blankJobName, secrets));

    Assert.assertThat(t.getMessage(), CoreMatchers.containsString("Data Job Name cannot be blank"));

    t =
        assertThrowsExactly(
            DataJobSecretsException.class,
            () -> secretsService.updateJobSecrets(teamName, nullJobName, secrets));

    Assert.assertThat(t.getMessage(), CoreMatchers.containsString("Data Job Name cannot be blank"));
  }

  @Test
  void updateTeamOauthCredentials_validInputs_shouldUpdateCredentials() {
    String teamName = "testTeam";
    String clientId = "testClientId";
    String clientSecret = "testClientSecret";

    when(vaultTemplate.opsForVersionedKeyValue(SECRET)).thenReturn(vaultOperations);

    secretsService.updateTeamOauthCredentials(teamName, clientId, clientSecret);

    String expectedSecretKey = teamName + "/" + TEAM_OAUTH_CREDENTIALS;
    VaultTeamCredentials expectedCredentials =
        new VaultTeamCredentials(teamName, clientId, clientSecret);
    verify(vaultOperations).put(expectedSecretKey, expectedCredentials);
  }

  @Test
  void updateTeamOauthCredentials_nullTeamName_shouldThrowException() {
    assertThrows(
        DataJobTeamSecretsException.class,
        () -> secretsService.updateTeamOauthCredentials(null, "clientId", "clientSecret"));
  }

  @Test
  void updateTeamOauthCredentials_emptyClientId_shouldThrowException() {
    assertThrows(
        DataJobTeamSecretsException.class,
        () -> secretsService.updateTeamOauthCredentials("teamName", "", "clientSecret"));
  }

  @Test
  void updateTeamOauthCredentials_nullClientSecret_shouldThrowException() {
    assertThrows(
        DataJobTeamSecretsException.class,
        () -> secretsService.updateTeamOauthCredentials("teamName", "clientId", null));
  }

  @Test
  void testReadTeamOauthCredentials_Success() {
    String teamName = "testTeam";
    String secretKey = teamName + "/" + TEAM_OAUTH_CREDENTIALS;
    VaultTeamCredentials expectedCredentials = new VaultTeamCredentials();
    expectedCredentials.setTeamName(teamName);
    expectedCredentials.setClientSecret("secret");
    expectedCredentials.setClientId("id");
    Versioned<VaultTeamCredentials> versionedCredentials = Versioned.create(expectedCredentials);

    when(vaultTemplate.opsForVersionedKeyValue(SECRET)).thenReturn(vaultOperations);
    when(vaultOperations.get(secretKey, VaultTeamCredentials.class))
        .thenReturn(versionedCredentials);

    VaultTeamCredentials result = secretsService.readTeamOauthCredentials(teamName);

    assertEquals(expectedCredentials, result);
    verify(vaultTemplate).opsForVersionedKeyValue(SECRET);
    verify(vaultOperations).get(secretKey, VaultTeamCredentials.class);
  }

  @Test
  void testReadTeamOauthCredentials_NullResponse() {
    String teamName = "testTeam";
    String secretKey = teamName + "/" + TEAM_OAUTH_CREDENTIALS;

    when(vaultTemplate.opsForVersionedKeyValue(SECRET)).thenReturn(vaultOperations);
    when(vaultOperations.get(secretKey, VaultTeamCredentials.class)).thenReturn(null);

    assertNull(secretsService.readTeamOauthCredentials(teamName));
    verify(vaultTemplate).opsForVersionedKeyValue(SECRET);
    verify(vaultOperations).get(secretKey, VaultTeamCredentials.class);
  }

  @Test
  void testReadTeamOauthCredentials_EmptyResponse() {
    String teamName = "testTeam";
    String secretKey = teamName + "/" + TEAM_OAUTH_CREDENTIALS;
    //    Versioned<VaultTeamCredentials> emptyVersionedCredentials = Versioned.empty();

    when(vaultTemplate.opsForVersionedKeyValue(SECRET)).thenReturn(vaultOperations);
    when(vaultOperations.get(secretKey, VaultTeamCredentials.class)).thenReturn(null);

    assertNull(secretsService.readTeamOauthCredentials(teamName));
    verify(vaultTemplate).opsForVersionedKeyValue(SECRET);
    verify(vaultOperations).get(secretKey, VaultTeamCredentials.class);
  }

  @Test
  void testReadTeamOauthCredentials_NullTeamName() {
    assertThrows(
        DataJobTeamSecretsException.class, () -> secretsService.readTeamOauthCredentials(null));
  }

  @Test
  void testReadTeamOauthCredentials_EmptyTeamName() {
    assertThrows(
        DataJobTeamSecretsException.class, () -> secretsService.readTeamOauthCredentials(""));
  }

  @Test
  void testGetCredentialsForTeamId() {
    String teamName = "testTeam";
    String clientId = "client1";
    String clientSecret = "secret1";

    VaultTeamCredentials expectedCredentials =
        new VaultTeamCredentials(teamName, clientId, clientSecret);

    String secretKey = teamName + "/" + TEAM_OAUTH_CREDENTIALS;
    Versioned<VaultTeamCredentials> readResponse = Versioned.create(expectedCredentials);

    when(vaultTemplate.opsForVersionedKeyValue(SECRET)).thenReturn(vaultOperations);
    when(vaultOperations.get(secretKey, VaultTeamCredentials.class)).thenReturn(readResponse);

    VaultTeamCredentials credentialsForTeamId = secretsService.readTeamOauthCredentials(teamName);

    assertNotNull(credentialsForTeamId);
    assertEquals(clientId, credentialsForTeamId.getClientId());
    assertEquals(clientSecret, credentialsForTeamId.getClientSecret());
  }

  @Test
  void testGetTeamIdForClientId() {
    String teamName = "testTeam";
    String clientId = "client1";
    String clientSecret = "secret1";

    VaultTeamCredentials expectedCredentials =
        new VaultTeamCredentials(teamName, clientId, clientSecret);

    String secretKey = teamName + "/" + TEAM_OAUTH_CREDENTIALS;
    Versioned<VaultTeamCredentials> readResponse = Versioned.create(expectedCredentials);

    when(vaultTemplate.list(SECRET_META)).thenReturn(List.of(teamName));
    when(vaultTemplate.opsForVersionedKeyValue(SECRET)).thenReturn(vaultOperations);
    when(vaultOperations.get(secretKey, VaultTeamCredentials.class)).thenReturn(readResponse);

    String result = secretsService.getTeamIdForClientId(clientId);

    assertNotNull(result);
    assertEquals(teamName, result);
  }

  @Test
  void testGetCredentialsForNonExistentTeamId() {
    String nonExistentTeamId = "nonExistentTeam";

    String secretKey = nonExistentTeamId + "/" + TEAM_OAUTH_CREDENTIALS;
    when(vaultTemplate.opsForVersionedKeyValue(SECRET)).thenReturn(vaultOperations);
    when(vaultOperations.get(secretKey)).thenReturn(null);

    assertNull(secretsService.readTeamOauthCredentials(nonExistentTeamId));
  }

  @Test
  void testGetTeamIdForNonExistentClientId() {
    String nonExistentClientId = "nonExistentClient";

    when(vaultTemplate.opsForVersionedKeyValue(SECRET)).thenReturn(vaultOperations);
    when(vaultOperations.list(SECRET_META)).thenReturn(List.of("team1"));
    when(vaultOperations.get("secret/oauth/team1")).thenReturn(null);

    String result = secretsService.getTeamIdForClientId(nonExistentClientId);

    assertNull(result);
  }
}
