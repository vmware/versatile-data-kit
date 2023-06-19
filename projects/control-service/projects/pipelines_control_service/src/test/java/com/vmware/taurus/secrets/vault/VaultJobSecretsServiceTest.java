/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.secrets.vault;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.exception.DataJobSecretsException;
import com.vmware.taurus.exception.DataJobSecretsSizeLimitException;
import com.vmware.taurus.secrets.service.vault.VaultJobSecrets;
import com.vmware.taurus.secrets.service.vault.VaultJobSecretsService;
import org.apache.commons.lang3.RandomStringUtils;
import org.hamcrest.CoreMatchers;
import org.junit.Assert;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.TestPropertySource;
import org.springframework.test.context.junit.jupiter.SpringExtension;
import org.springframework.vault.core.VaultTemplate;
import org.springframework.vault.core.VaultVersionedKeyValueOperations;
import org.springframework.vault.support.Versioned;

import java.util.HashMap;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.when;

@ExtendWith(SpringExtension.class)
@SpringBootTest(classes = ControlplaneApplication.class)
@TestPropertySource(
    properties = {
      "datajobs.vault.size.limit.bytes=1048576",
    })
class VaultJobSecretsServiceTest {

  private static final String SECRET = "secret";

  @Mock private VaultTemplate vaultTemplate;
  @Mock private VaultVersionedKeyValueOperations vaultOperations;

  @InjectMocks private VaultJobSecretsService secretsService;

  @Test
  void testUpdateJobSecrets() throws JsonProcessingException {
    String jobName = "testJob";
    Map<String, Object> secrets = new HashMap<>();
    secrets.put("key1", "value1");
    secrets.put("key2", 123);
    secrets.put("key3", true);
    secrets.put("key4", null);

    when(vaultTemplate.opsForVersionedKeyValue(SECRET)).thenReturn(vaultOperations);
    when(vaultOperations.get(jobName, VaultJobSecrets.class)).thenReturn(null);

    Map<String, Object> initial = secretsService.readJobSecrets(jobName);
    assertNotEquals(secrets, initial);

    VaultJobSecrets vaultJobSecrets =
        new VaultJobSecrets(jobName, "{\"key1\":\"ala-bala\",\"key3\":null}");
    Versioned<VaultJobSecrets> readResponse = Versioned.create(vaultJobSecrets);

    when(vaultOperations.get(jobName, VaultJobSecrets.class)).thenReturn(readResponse);
    secretsService.updateJobSecrets(jobName, secrets);

    vaultJobSecrets =
        new VaultJobSecrets(
            jobName, "{\"key1\":\"value1\",\"key2\":123,\"key3\":true,\"key4\":null}");
    readResponse = Versioned.create(vaultJobSecrets);

    when(vaultOperations.get(jobName, VaultJobSecrets.class)).thenReturn(readResponse);

    Map<String, Object> result = secretsService.readJobSecrets(jobName);
    assertEquals(secrets, result);
  }

  @Test
  void testUpdateJobSecretsLimit() throws JsonProcessingException {
    String jobName = "testJob";
    Map<String, Object> secrets = new HashMap<>();
    secrets.put("key1", "value1");
    secrets.put("key2", RandomStringUtils.randomAlphabetic(1025 * 1025));

    when(vaultTemplate.opsForVersionedKeyValue(SECRET)).thenReturn(vaultOperations);

    VaultJobSecrets vaultJobSecrets =
        new VaultJobSecrets(jobName, "{\"key1\":\"ala-bala\",\"key3\":null}");
    Versioned<VaultJobSecrets> readResponse = Versioned.create(vaultJobSecrets);

    when(vaultOperations.get(jobName, VaultJobSecrets.class)).thenReturn(readResponse);

    Assertions.assertThrows(
        DataJobSecretsSizeLimitException.class,
        () -> secretsService.updateJobSecrets(jobName, secrets));
  }

  @Test
  void testUpdateJobSecretsNulls() throws JsonProcessingException {
    String jobName = "testJob";
    String blankJobName = " ";
    String nullJobName = null;
    Map<String, Object> secrets = new HashMap<>();
    Map<String, Object> nullSecrets = new HashMap<>();

    Throwable t =
        Assertions.assertThrows(
            DataJobSecretsException.class,
            () -> secretsService.updateJobSecrets(blankJobName, secrets));

    Assert.assertThat(t.getMessage(), CoreMatchers.containsString("Data Job Name cannot be blank"));

    t =
        Assertions.assertThrowsExactly(
            DataJobSecretsException.class,
            () -> secretsService.updateJobSecrets(nullJobName, secrets));

    Assert.assertThat(t.getMessage(), CoreMatchers.containsString("Data Job Name cannot be blank"));

    t =
        Assertions.assertThrowsExactly(
            DataJobSecretsException.class, () -> secretsService.updateJobSecrets(jobName, secrets));

    Assert.assertThat(
        t.getMessage(), CoreMatchers.containsString("Secrets parameter cannot be null or empty"));

    t =
        Assertions.assertThrowsExactly(
            DataJobSecretsException.class,
            () -> secretsService.updateJobSecrets(jobName, nullSecrets));

    Assert.assertThat(
        t.getMessage(), CoreMatchers.containsString("Secrets parameter cannot be null or empty"));
  }
}
