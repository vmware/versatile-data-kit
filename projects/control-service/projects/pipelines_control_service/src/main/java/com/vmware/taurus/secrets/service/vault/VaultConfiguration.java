/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.secrets.service.vault;

import com.vmware.taurus.exception.SecretStorageNotConfiguredException;
import org.jetbrains.annotations.NotNull;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.vault.authentication.AppRoleAuthentication;
import org.springframework.vault.authentication.AppRoleAuthenticationOptions;
import org.springframework.vault.authentication.ClientAuthentication;
import org.springframework.vault.authentication.SessionManager;
import org.springframework.vault.client.VaultEndpoint;
import org.springframework.vault.config.AbstractVaultConfiguration;
import org.springframework.vault.core.VaultOperations;
import org.springframework.vault.core.VaultTemplate;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.util.DefaultUriBuilderFactory;

import java.net.URI;
import java.net.URISyntaxException;

@Configuration
public class VaultConfiguration extends AbstractVaultConfiguration {

    @Value("${vdk.vault.uri:}")
    String vaultUri;
    @Value("${vdk.vault.approle.roleid:}")
    String roleId;
    @Value("${vdk.vault.approle.secretid:}")
    String secretId;

    @Bean
    public VaultOperations vaultOperations(VaultEndpoint vaultEndpoint, SessionManager sessionManager) {

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
        AppRoleAuthenticationOptions.AppRoleAuthenticationOptionsBuilder builder = AppRoleAuthenticationOptions
                .builder()
                .roleId(AppRoleAuthenticationOptions.RoleId.provided(this.roleId))
                .secretId(AppRoleAuthenticationOptions.SecretId.provided(this.secretId));

        RestTemplate restTemplate = new RestTemplate();
        restTemplate.setUriTemplateHandler(new DefaultUriBuilderFactory(vaultUri));


        return new AppRoleAuthentication(builder.build(), restTemplate);
    }
}
