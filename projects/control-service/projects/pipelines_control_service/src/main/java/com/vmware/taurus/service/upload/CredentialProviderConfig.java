/*
 * Copyright 2023-2024 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.upload;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class CredentialProviderConfig {


    private final VCSCredentialsProvider credentialsProvider;

    @Autowired
    public CredentialProviderConfig(
            @Value("${datajobs.git.assumeIAMRole}") boolean assumeCodeCommitIAMRole,
            GitCredentialsProvider gitCredentialsProvider,
            CodeCommitCredentialProvider codeCommitProvider) {
        if (assumeCodeCommitIAMRole) {
            this.credentialsProvider = codeCommitProvider;
        } else {
            this.credentialsProvider = gitCredentialsProvider;
        }
    }

    @Bean
    public VCSCredentialsProvider credentialsProvider() {
        return credentialsProvider;
    }
}
