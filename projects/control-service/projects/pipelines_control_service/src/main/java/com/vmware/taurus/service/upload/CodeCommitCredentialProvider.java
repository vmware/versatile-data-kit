/*
 * Copyright 2023-2024 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.upload;

import com.vmware.taurus.service.credentials.AWSCredentialsService;
import org.eclipse.jgit.transport.CredentialsProvider;
import org.springframework.cloud.config.server.support.AwsCodeCommitCredentialProvider;
import org.springframework.stereotype.Component;

@Component
public class CodeCommitCredentialProvider {
    private final AWSCredentialsService awsCredentialsService;

    public CodeCommitCredentialProvider(AWSCredentialsService awsCredentialsService) {
        this.awsCredentialsService = awsCredentialsService;
    }

    public CredentialsProvider getProvider() {
        AwsCodeCommitCredentialProvider codeCommitCredentialProvider = new AwsCodeCommitCredentialProvider();
        codeCommitCredentialProvider.setAwsCredentialProvider(awsCredentialsService.getCredentialsProvider());
        return codeCommitCredentialProvider;
    }
}
