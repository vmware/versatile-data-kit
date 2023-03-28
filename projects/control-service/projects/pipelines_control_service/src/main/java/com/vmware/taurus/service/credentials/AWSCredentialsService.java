/*
 * Copyright 2023-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.credentials;

import com.amazonaws.auth.AWSStaticCredentialsProvider;
import com.amazonaws.auth.BasicAWSCredentials;
import com.amazonaws.auth.BasicSessionCredentials;
import com.amazonaws.auth.STSAssumeRoleSessionCredentialsProvider;
import com.amazonaws.services.securitytoken.AWSSecurityTokenService;
import com.amazonaws.services.securitytoken.AWSSecurityTokenServiceClientBuilder;
import com.amazonaws.services.securitytoken.model.AssumeRoleRequest;
import java.util.UUID;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

@Service
public class AWSCredentialsService {

  @Value("${datajobs.aws.secretAccessKey:}")
  private String awsSecretAccessKey;

  @Value("${datajobs.aws.accessKeyId:}")
  private String awsAccessKeyId;

  @Value("${datajobs.aws.RoleArn:}")
  private String awsRoleArn;

  @Value("${datajobs.aws.defaultSessionDurationSeconds:}")
  private int sessionDuration;

  @Value("${datajobs.aws.region:}")
  private String awsRegion;

  public BasicSessionCredentials getTemporaryCredentials() {
    AWSSecurityTokenService stsClient =
        AWSSecurityTokenServiceClientBuilder.standard()
            .withCredentials(
                new AWSStaticCredentialsProvider(
                    new BasicAWSCredentials(awsSecretAccessKey, awsAccessKeyId)))
            .withRegion(awsRegion)
            .build();

    AssumeRoleRequest assumeRequest =
        new AssumeRoleRequest()
            .withRoleArn(awsRoleArn)
            .withRoleSessionName(
                "control-service-session-" + UUID.randomUUID().toString().substring(0, 4))
            .withDurationSeconds(sessionDuration);

    STSAssumeRoleSessionCredentialsProvider credentialsProvider =
        new STSAssumeRoleSessionCredentialsProvider.Builder(
                assumeRequest.getRoleArn(), assumeRequest.getRoleSessionName())
            .withStsClient(stsClient)
            .build();

    BasicSessionCredentials sessionCredentials =
        (BasicSessionCredentials) credentialsProvider.getCredentials();

    return sessionCredentials;
  }
}
