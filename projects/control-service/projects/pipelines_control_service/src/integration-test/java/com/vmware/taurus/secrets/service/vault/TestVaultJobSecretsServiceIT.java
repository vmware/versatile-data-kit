/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.secrets.service.vault;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.datajobs.it.common.BaseIT;
import com.vmware.taurus.exception.DataJobSecretsSizeLimitException;
import org.apache.commons.lang3.RandomStringUtils;
import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.entity.StringEntity;
import org.apache.http.impl.client.HttpClients;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.vault.authentication.AppRoleAuthentication;
import org.springframework.vault.authentication.AppRoleAuthenticationOptions;
import org.springframework.vault.client.VaultEndpoint;
import org.springframework.vault.core.VaultTemplate;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.util.DefaultUriBuilderFactory;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;
import org.testcontainers.vault.VaultContainer;

import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;
import java.util.Collections;
import java.util.HashMap;
import java.util.Map;

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
    // enable AppRoles
    vaultContainer.execInContainer("vault", "auth", "enable", "approle");

    // Create a new test policy via rest as there's no good way to do it via the command mechanism
    HttpClient httpClient = HttpClients.createDefault();
    HttpPost httpPost = new HttpPost(vaultUri + "/v1/sys/policies/acl/testpolicy");
    httpPost.setHeader("X-Vault-Token", "root");
    StringEntity requestBody =
        new StringEntity(
            "{\n"
                + "  \"policy\": \"path \\\"secret/*\\\" {\\n"
                + "  capabilities = [ \\\"create\\\", \\\"read\\\",\\\"update\\\", \\\"patch\\\","
                + " \\\"delete\\\",\\\"list\\\" ]\\n"
                + "}\"\n"
                + "}");
    httpPost.setEntity(requestBody);
    httpClient.execute(httpPost);

    // create "test" role with the policy
    vaultContainer.execInContainer(
        "vault",
        "write",
        "auth/approle/role/test",
        "token_policies=testpolicy",
        "token_ttl=1h",
        "token_max_ttl=4h");
    // get the role id
    org.testcontainers.containers.Container.ExecResult execResult =
        vaultContainer.execInContainer(
            "vault", "read", "auth/approle/role/test/role-id"); // read the role-id
    String output = execResult.getStdout();
    String roleId = output.substring(output.lastIndexOf(" ")).trim();

    // get the role secret id
    execResult =
        vaultContainer.execInContainer(
            "vault", "write", "-force", "auth/approle/role/test/secret-id"); // read the secret-id
    output = execResult.getStdout();
    String secretId =
        output
            .substring(output.indexOf("secret_id") + 9, output.indexOf("secret_id_accessor"))
            .trim();
    VaultEndpoint vaultEndpoint = VaultEndpoint.from(new URI(vaultUri + "/v1/"));

    // create the authentication
    AppRoleAuthenticationOptions.AppRoleAuthenticationOptionsBuilder builder =
        AppRoleAuthenticationOptions.builder()
            .roleId(AppRoleAuthenticationOptions.RoleId.provided(roleId))
            .secretId(AppRoleAuthenticationOptions.SecretId.provided(secretId));

    RestTemplate restTemplate = new RestTemplate();
    restTemplate.setUriTemplateHandler(new DefaultUriBuilderFactory(vaultUri + "/v1/"));

    AppRoleAuthentication clientAuthentication =
        new AppRoleAuthentication(builder.build(), restTemplate);

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
    Map<String, Object> temp = new HashMap<>();
    temp.put("key1", "value1");

    Map<String, Object> secrets = Collections.unmodifiableMap(temp);

    vaultJobSecretService.updateJobSecrets("testJob2", secrets);

    Map<String, Object> readResult = vaultJobSecretService.readJobSecrets("testJob2");
    Assertions.assertEquals(secrets, readResult);
  }

  @Test
  void testUpdateJobSecretsLimit() throws JsonProcessingException {
    Map<String, Object> temp = new HashMap<>();
    temp.put("key1", "value1");

    Map<String, Object> secrets = Collections.unmodifiableMap(temp);

    vaultJobSecretService.updateJobSecrets("testJob2", secrets);

    Map<String, Object> largeSecrets = new HashMap<>();
    largeSecrets.put("key1", null);
    largeSecrets.put(
        "key2",
        RandomStringUtils.randomAlphabetic(VaultJobSecretsService.VAULT_SIZE_LIMIT_DEFAULT));

    assertThrows(
        DataJobSecretsSizeLimitException.class,
        () -> vaultJobSecretService.updateJobSecrets("testJob2", largeSecrets));

    // check secrets were not updated
    Map<String, Object> readResult = vaultJobSecretService.readJobSecrets("testJob2");
    Assertions.assertEquals(secrets, readResult);
  }
}
