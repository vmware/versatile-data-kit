/*
 * Copyright 2023-2025 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.secrets.service.vault;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.datajobs.it.common.BaseIT;
import com.vmware.taurus.exception.DataJobSecretsSizeLimitException;
import com.vmware.taurus.exception.DataJobTeamSecretsException;
import org.apache.commons.lang3.RandomStringUtils;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.vault.core.VaultTemplate;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;
import org.testcontainers.vault.VaultContainer;

import java.io.IOException;
import java.net.URISyntaxException;
import java.util.Collections;
import java.util.HashMap;
import java.util.Map;

import static com.vmware.taurus.secrets.service.vault.VaultTestSetup.setupVaultTemplate;
import static org.junit.jupiter.api.Assertions.assertThrows;

@SpringBootTest(
    webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT,
    classes = ControlplaneApplication.class)
@Testcontainers
public class TestVaultJobSecretsServiceIT extends BaseIT {

  @Container
  private static final VaultContainer vaultContainer =
      new VaultContainer<>("vault:1.13.3").withVaultToken("root");

  private static VaultJobSecretsService vaultJobSecretService;

  @BeforeAll
  public static void init() throws URISyntaxException, IOException, InterruptedException {
    String vaultUri = vaultContainer.getHttpHostAddress();

    // Setup vault app roles authentication
    // https://developer.hashicorp.com/vault/tutorials/auth-methods/approle

    VaultTemplate vaultTemplate = setupVaultTemplate(vaultUri, vaultContainer);

    vaultJobSecretService = new VaultJobSecretsService(vaultTemplate);
  }

  @Test
  public void testGetEmptyDataJobSecrets() throws Exception {
    Map<String, Object> result = vaultJobSecretService.readJobSecrets("testTeam", "testJob");
    Assertions.assertEquals(Collections.emptyMap(), result);
  }

  @Test
  public void testSetDataJobSecrets() throws Exception {
    Map<String, Object> temp = new HashMap<>();
    temp.put("key1", "value1");

    Map<String, Object> secrets = Collections.unmodifiableMap(temp);

    vaultJobSecretService.updateJobSecrets("test !@#$%^&*() Team", "testJob2", secrets);

    Map<String, Object> readResult =
        vaultJobSecretService.readJobSecrets("test !@#$%^&*() Team", "testJob2");
    Assertions.assertEquals(secrets, readResult);
  }

  @Test
  public void testSetEmptyDataJobSecrets() throws Exception {
    Map<String, Object> temp = new HashMap<>();

    Map<String, Object> secrets = Collections.unmodifiableMap(temp);

    vaultJobSecretService.updateJobSecrets("testTeam", "testJob2", secrets);

    Map<String, Object> readResult = vaultJobSecretService.readJobSecrets("testTeam", "testJob2");
    Assertions.assertEquals(secrets, readResult);
  }

  @Test
  void testUpdateJobSecretsLimit() throws JsonProcessingException {
    Map<String, Object> temp = new HashMap<>();
    temp.put("key1", "value1");

    Map<String, Object> secrets = Collections.unmodifiableMap(temp);

    vaultJobSecretService.updateJobSecrets("test Team", "testJob2", secrets);

    Map<String, Object> largeSecrets = new HashMap<>();
    largeSecrets.put("key1", null);
    largeSecrets.put(
        "key2",
        RandomStringUtils.randomAlphabetic(VaultJobSecretsService.VAULT_SIZE_LIMIT_DEFAULT));

    assertThrows(
        DataJobSecretsSizeLimitException.class,
        () -> vaultJobSecretService.updateJobSecrets("test Team", "testJob2", largeSecrets));

    // check secrets were not updated
    Map<String, Object> readResult = vaultJobSecretService.readJobSecrets("test Team", "testJob2");
    Assertions.assertEquals(secrets, readResult);
  }

  @Test
  public void testGetEmptyTeamOauthToken() throws Exception {
    Assertions.assertNull(vaultJobSecretService.readTeamOauthCredentials("testTeam"));
  }

  @Test
  public void testSetTeamOauthToken() throws Exception {
    String teamName = "ala-bala chiki-riki 123 $&^#@$";
    String clientId = "clientId";
    String clientSecret = "clientSecret";

    vaultJobSecretService.updateTeamOauthCredentials(teamName, clientId, clientSecret);

    VaultTeamCredentials readResult = vaultJobSecretService.readTeamOauthCredentials(teamName);
    Assertions.assertEquals(teamName, readResult.getTeamName());
    Assertions.assertEquals(clientId, readResult.getClientId());
    Assertions.assertEquals(clientSecret, readResult.getClientSecret());
  }

  @Test
  public void testSetEmptyTeamOauthToken() throws Exception {
    Assertions.assertThrows(
        DataJobTeamSecretsException.class,
        () -> vaultJobSecretService.updateTeamOauthCredentials("", "ClientId", "clientSecret"));
    Assertions.assertThrows(
        DataJobTeamSecretsException.class,
        () -> vaultJobSecretService.updateTeamOauthCredentials("teamName", "", "clientSecret"));
    Assertions.assertThrows(
        DataJobTeamSecretsException.class,
        () -> vaultJobSecretService.updateTeamOauthCredentials("teamName", "ClientId", ""));
  }

  @Test
  public void testGetTeamsForClientIds() throws Exception {
    String team1Name = "ala-bala chiki-riki 123 $&^#@$";
    String client1Id = "clientId1";
    String client1Secret = "clientSecret3";

    vaultJobSecretService.updateTeamOauthCredentials(team1Name, client1Id, client1Secret);

    String team3Name = "normal team name";
    String client3Id = "clientId3";
    String client3Secret = "clientSecret3";

    vaultJobSecretService.updateTeamOauthCredentials(team3Name, client3Id, client3Secret);

    String team5Name = "some-team-name";
    String client5Id = "clientId5";
    String client5Secret = "clientSecret5";

    vaultJobSecretService.updateTeamOauthCredentials(team5Name, client5Id, client5Secret);

    String readResult = vaultJobSecretService.getTeamIdForClientId(client1Id);
    Assertions.assertEquals(team1Name, readResult);

    readResult = vaultJobSecretService.getTeamIdForClientId(client3Id);
    Assertions.assertEquals(team3Name, readResult);

    readResult = vaultJobSecretService.getTeamIdForClientId(client5Id);
    Assertions.assertEquals(team5Name, readResult);

    readResult = vaultJobSecretService.getTeamIdForClientId("some-other-team-name");
    Assertions.assertNull(readResult);
  }
}
