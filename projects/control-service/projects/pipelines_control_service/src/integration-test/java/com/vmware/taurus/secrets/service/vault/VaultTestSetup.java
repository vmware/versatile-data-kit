/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.secrets.service.vault;

import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.entity.StringEntity;
import org.apache.http.impl.client.HttpClients;
import org.jetbrains.annotations.NotNull;
import org.springframework.vault.authentication.AppRoleAuthentication;
import org.springframework.vault.authentication.AppRoleAuthenticationOptions;
import org.springframework.vault.client.VaultEndpoint;
import org.springframework.vault.core.VaultTemplate;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.util.DefaultUriBuilderFactory;
import org.testcontainers.containers.ContainerState;
import org.testcontainers.vault.VaultContainer;

import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;

public class VaultTestSetup {

  @NotNull
  static VaultTemplate setupVaultTemplate(String vaultUri, VaultContainer vaultContainer)
      throws IOException, InterruptedException, URISyntaxException {
    setupAppRole(vaultUri, vaultContainer);
    String roleId = getRoleId(vaultContainer);
    String secretId = getSecretId(vaultContainer);
    // create the authentication
    AppRoleAuthentication clientAuthentication =
        getAppRoleAuthentication(vaultUri, roleId, secretId);
    VaultEndpoint vaultEndpoint = VaultEndpoint.from(new URI(vaultUri + "/v1/"));
    VaultTemplate vaultTemplate = new VaultTemplate(vaultEndpoint, clientAuthentication);
    return vaultTemplate;
  }

  private static void setupAppRole(String vaultUri, ContainerState vaultContainer)
      throws IOException, InterruptedException {
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
  }

  @NotNull
  private static String getRoleId(ContainerState vaultContainer)
      throws IOException, InterruptedException {
    org.testcontainers.containers.Container.ExecResult execResult =
        vaultContainer.execInContainer(
            "vault", "read", "auth/approle/role/test/role-id"); // read the role-id
    String output = execResult.getStdout();
    String roleId = output.substring(output.lastIndexOf(" ")).trim();
    return roleId;
  }

  @NotNull
  private static String getSecretId(ContainerState vaultContainer)
      throws IOException, InterruptedException {
    org.testcontainers.containers.Container.ExecResult execResult =
        vaultContainer.execInContainer(
            "vault", "write", "-force", "auth/approle/role/test/secret-id"); // read the secret-id
    String output = execResult.getStdout();
    String secretId =
        output
            .substring(output.indexOf("secret_id") + 9, output.indexOf("secret_id_accessor"))
            .trim();
    return secretId;
  }

  @NotNull
  private static AppRoleAuthentication getAppRoleAuthentication(
      String vaultUri, String roleId, String secretId) {
    AppRoleAuthenticationOptions.AppRoleAuthenticationOptionsBuilder builder =
        AppRoleAuthenticationOptions.builder()
            .roleId(AppRoleAuthenticationOptions.RoleId.provided(roleId))
            .secretId(AppRoleAuthenticationOptions.SecretId.provided(secretId));

    RestTemplate restTemplate = new RestTemplate();
    restTemplate.setUriTemplateHandler(new DefaultUriBuilderFactory(vaultUri + "/v1/"));

    AppRoleAuthentication clientAuthentication =
        new AppRoleAuthentication(builder.build(), restTemplate);
    return clientAuthentication;
  }
}
