/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.secrets.service.vault;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.vault.authentication.TokenAuthentication;
import org.springframework.vault.client.VaultEndpoint;
import org.springframework.vault.core.VaultOperations;
import org.springframework.vault.core.VaultTemplate;

import java.net.URI;
import java.net.URISyntaxException;

@Configuration
public class VaultConfiguration {

    @Bean
    public VaultOperations vaultOperations(@Value("${vdk.vault.uri:}") String vaultUri,
                                           @Value("${vdk.vault.token:}") String vaultToken) throws URISyntaxException {
        VaultEndpoint vaultEndpoint = VaultEndpoint.from(new URI(vaultUri));
        TokenAuthentication clientAuthentication = new TokenAuthentication(vaultToken);

        return new VaultTemplate(vaultEndpoint, clientAuthentication);
    }
}
