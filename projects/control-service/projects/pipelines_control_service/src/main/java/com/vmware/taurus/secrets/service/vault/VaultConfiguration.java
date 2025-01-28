/*
 * Copyright 2023-2024 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.secrets.service.vault;

import com.vmware.taurus.exception.SecretStorageNotConfiguredException;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.jetbrains.annotations.NotNull;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.vault.authentication.*;
import org.springframework.vault.client.VaultEndpoint;
import org.springframework.vault.config.AbstractVaultConfiguration;
import org.springframework.vault.core.VaultOperations;
import org.springframework.vault.core.VaultTemplate;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.util.DefaultUriBuilderFactory;

import java.net.URI;
import java.net.URISyntaxException;

@Slf4j
@Configuration
@ConditionalOnProperty(value = "featureflag.vault.integration.enabled")
public class VaultConfiguration extends AbstractVaultConfiguration {

  @Value("${vdk.vault.uri:}")
  String vaultUri;

  @Value("${vdk.vault.approle.roleid:}")
  String roleId;

  @Value("${vdk.vault.approle.secretid:}")
  String secretId;

  @Value("${vdk.vault.token:}")
  String vaultToken;

  @Bean
  public VaultOperations vaultOperations(
      VaultEndpoint vaultEndpoint, SessionManager sessionManager) {

    SimpleClientHttpRequestFactory clientHttpRequestFactory = new SimpleClientHttpRequestFactory();
    return new VaultTemplate(vaultEndpoint, clientHttpRequestFactory, sessionManager);
  }

  @NotNull
  @Override
  @Bean
  public VaultEndpoint vaultEndpoint() {
    try {
      return VaultEndpoint.from(new URI(this.vaultUri));
    } catch (URISyntaxException e) {
      throw new SecretStorageNotConfiguredException();
    }
  }

  @NotNull
  @Override
  @Bean
  public ClientAuthentication clientAuthentication() {
    if (StringUtils.isNotBlank(this.roleId) && StringUtils.isNotBlank(this.secretId)) {
      log.info("Initializing vault integration with AppRole Authentication.");
      AppRoleAuthenticationOptions.AppRoleAuthenticationOptionsBuilder builder =
          AppRoleAuthenticationOptions.builder()
              .roleId(AppRoleAuthenticationOptions.RoleId.provided(this.roleId))
              .secretId(AppRoleAuthenticationOptions.SecretId.provided(this.secretId));

      RestTemplate restTemplate = new RestTemplate();
      restTemplate.setUriTemplateHandler(new DefaultUriBuilderFactory(this.vaultUri));

      return new AppRoleAuthentication(builder.build(), restTemplate);
    }
    // Token authentication should only be used for development purposes. If the token expires, the
    // secrets functionality will stop working
    else {
      log.warn("Initializing vault integration with Token Authentication.");
      return new TokenAuthentication(this.vaultToken);
    }
  }
}
