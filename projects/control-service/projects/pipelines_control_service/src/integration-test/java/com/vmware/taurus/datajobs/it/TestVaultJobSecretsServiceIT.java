/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs.it;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.datajobs.it.common.BaseIT;
import com.vmware.taurus.exception.DataJobSecretsSizeLimitException;
import com.vmware.taurus.secrets.service.vault.VaultJobSecretsService;
import org.apache.commons.lang3.RandomStringUtils;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.vault.authentication.TokenAuthentication;
import org.springframework.vault.client.VaultEndpoint;
import org.springframework.vault.core.VaultTemplate;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;
import org.testcontainers.vault.VaultContainer;

import java.net.URI;
import java.net.URISyntaxException;
import java.util.Collections;
import java.util.HashMap;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertThrows;

@SpringBootTest(
<<<<<<< HEAD
<<<<<<< HEAD
    webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT,
    classes = ControlplaneApplication.class)
@Testcontainers
public class VaultJobSecretsServiceIT extends BaseIT {

  @Container
  private static final VaultContainer vaultContainer =
      new VaultContainer<>("vault:1.0.2").withVaultToken("root");

  private static VaultJobSecretsService vaultJobSecretService;

  @BeforeAll
  public static void init() throws URISyntaxException {
    String vaultUri = vaultContainer.getHttpHostAddress();

    VaultEndpoint vaultEndpoint = VaultEndpoint.from(new URI(vaultUri));
    TokenAuthentication clientAuthentication = new TokenAuthentication("root");

    VaultTemplate vaultTemplate = new VaultTemplate(vaultEndpoint, clientAuthentication);

    vaultJobSecretService = new VaultJobSecretsService(vaultTemplate);
  }

  @Test
  public void testGetEmptyDataJobSecrets() throws Exception {
    Map<String, Object> result = vaultJobSecretService.readJobSecrets("testJob");
    Assertions.assertEquals(Collections.emptyMap(), result);
  }

  @Test
  public void testSetDataJobSecrets() throws Exception {
    Map<String, Object> secrets = new HashMap<>();
    secrets.put("key1", "value1");

    vaultJobSecretService.updateJobSecrets("testJob2", secrets);

    Map<String, Object> readResult = vaultJobSecretService.readJobSecrets("testJob2");
    Assertions.assertEquals(secrets, readResult);
  }

  @Test
  void testUpdateJobSecretsLimit() throws JsonProcessingException {
    Map<String, Object> secrets = new HashMap<>();
    secrets.put("key1", "value1");

    vaultJobSecretService.updateJobSecrets("testJob2", secrets);

    Map<String, Object> largeSecrets = new HashMap<>();
    largeSecrets.put("key1", null);
    largeSecrets.put("key2", RandomStringUtils.randomAlphabetic(1025 * 1025));

    assertThrows(
        DataJobSecretsSizeLimitException.class,
        () -> vaultJobSecretService.updateJobSecrets("testJob2", largeSecrets));

    // check secrets were not updated
    Map<String, Object> readResult = vaultJobSecretService.readJobSecrets("testJob2");
    Assertions.assertEquals(secrets, readResult);
  }
}
// vaultContainer.execInContainer("vault","kv","list", "secret")
// vaultContainer.execInContainer("vault","kv","list", "secret")
// vaultContainer.execInContainer("vault", "kv", "put", "secret/test", "db_name=postgres")
=======
        webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT,
        classes = ControlplaneApplication.class)
=======
    webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT,
    classes = ControlplaneApplication.class)
>>>>>>> 74e375dd (Google Java Format)
@Testcontainers
public class VaultJobSecretsServiceIT extends BaseIT {

  @Container
  private static final VaultContainer vaultContainer =
      new VaultContainer<>("vault:1.0.2").withVaultToken("root");

  private static VaultJobSecretsService vaultJobSecretService;

  @BeforeAll
  public static void init() throws URISyntaxException {
    String vaultUri = vaultContainer.getHttpHostAddress();

    VaultEndpoint vaultEndpoint = VaultEndpoint.from(new URI(vaultUri));
    TokenAuthentication clientAuthentication = new TokenAuthentication("root");

    VaultTemplate vaultTemplate = new VaultTemplate(vaultEndpoint, clientAuthentication);

    vaultJobSecretService = new VaultJobSecretsService(vaultTemplate);
  }

  @Test
  public void testGetEmptyDataJobSecrets() throws Exception {
    Map<String, Object> result = vaultJobSecretService.readJobSecrets("testJob");
    Assertions.assertEquals(Collections.emptyMap(), result);
  }

  @Test
  public void testSetDataJobSecrets() throws Exception {
    Map<String, Object> secrets = new HashMap<>();
    secrets.put("key1", "value1");

    vaultJobSecretService.updateJobSecrets("testJob2", secrets);

    Map<String, Object> readResult = vaultJobSecretService.readJobSecrets("testJob2");
    Assertions.assertEquals(secrets, readResult);
  }

  @Test
  void testUpdateJobSecretsLimit() throws JsonProcessingException {
    Map<String, Object> secrets = new HashMap<>();
    secrets.put("key1", "value1");

    vaultJobSecretService.updateJobSecrets("testJob2", secrets);

    Map<String, Object> largeSecrets = new HashMap<>();
    largeSecrets.put("key1", null);
    largeSecrets.put("key2", RandomStringUtils.randomAlphabetic(1025 * 1025));

    assertThrows(
        DataJobSecretsSizeLimitException.class,
        () -> vaultJobSecretService.updateJobSecrets("testJob2", largeSecrets));

    // check secrets were not updated
    Map<String, Object> readResult = vaultJobSecretService.readJobSecrets("testJob2");
    Assertions.assertEquals(secrets, readResult);
  }
}
<<<<<<< HEAD
//vaultContainer.execInContainer("vault","kv","list", "secret")
//vaultContainer.execInContainer("vault","kv","list", "secret")
//vaultContainer.execInContainer("vault", "kv", "put", "secret/test", "db_name=postgres")
>>>>>>> aa20f0b2 (control-service: secrets service integration test)
=======
// vaultContainer.execInContainer("vault","kv","list", "secret")
// vaultContainer.execInContainer("vault","kv","list", "secret")
// vaultContainer.execInContainer("vault", "kv", "put", "secret/test", "db_name=postgres")
>>>>>>> 74e375dd (Google Java Format)
