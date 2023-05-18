/*
 * Copyright 2023-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.credentials;

import com.amazonaws.auth.AWSSessionCredentials;
import com.amazonaws.auth.AWSStaticCredentialsProvider;
import com.amazonaws.auth.BasicAWSCredentials;
import com.amazonaws.auth.STSAssumeRoleSessionCredentialsProvider;
import com.amazonaws.services.securitytoken.AWSSecurityTokenService;
import com.amazonaws.services.securitytoken.AWSSecurityTokenServiceClientBuilder;
import com.amazonaws.services.securitytoken.model.AssumeRoleRequest;
import java.util.UUID;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

/**
 * This Spring Service Component provides a convenient way to manage AWS SDK credentials within
 * control-service. It simplifies the process of setting up and configuring AWS SDK credentials,
 * allowing you to quickly get up and running with AWS temporary session credentials for service
 * accounts with the aws credentials found in the application.properties file. More information
 * about the properties and service user patterns can be found in the application.properties file's
 * comments or https://docs.aws.amazon.com/eks/latest/userguide/iam-roles-for-service-accounts.html
 */
@Service
@Slf4j
public class AWSCredentialsService {

  public record AWSCredentialsDTO(
      String awsSecretAccessKey, String awsAccessKeyId, String awsSessionToken, String region) {}

  private STSAssumeRoleSessionCredentialsProvider credentialsProvider;
  private AWSCredentialsServiceConfig awsCredentialsServiceConfig;

  public AWSCredentialsService(AWSCredentialsServiceConfig awsCredentialsServiceConfig) {
    this.awsCredentialsServiceConfig = awsCredentialsServiceConfig;

    if (awsCredentialsServiceConfig.isAssumeIAMRole()) {
      AWSSecurityTokenService stsClient =
          AWSSecurityTokenServiceClientBuilder.standard()
              .withCredentials(
                  new AWSStaticCredentialsProvider(
                      new BasicAWSCredentials(
                          awsCredentialsServiceConfig.getServiceAccountAccessKeyId(),
                          awsCredentialsServiceConfig.getServiceAccountSecretAccessKey())))
              .withRegion(awsCredentialsServiceConfig.getRegion())
              .build();

      AssumeRoleRequest assumeRequest =
          new AssumeRoleRequest()
              .withRoleArn(awsCredentialsServiceConfig.getRoleArn())
              .withRoleSessionName(
                  "control-service-session-" + UUID.randomUUID().toString().substring(0, 4))
              .withDurationSeconds(awsCredentialsServiceConfig.getDefaultSessionDurationSeconds());

      this.credentialsProvider =
          new STSAssumeRoleSessionCredentialsProvider.Builder(
                  assumeRequest.getRoleArn(), assumeRequest.getRoleSessionName())
              .withStsClient(stsClient)
              .build();
    }
  }

  /**
   * DTO object containing the secret access key, access key id and the session token. Return an
   * empty session token if we are using long term credentials. Values can be accessed through
   * getters.
   *
   * @return
   */
  public AWSCredentialsDTO createTemporaryCredentials() {

    if (!awsCredentialsServiceConfig.isAssumeIAMRole()) {
      return new AWSCredentialsDTO(
          awsCredentialsServiceConfig.getSecretAccessKey(),
          awsCredentialsServiceConfig.getAccessKeyId(),
          "",
          awsCredentialsServiceConfig.getRegion());
    }
    AWSSessionCredentials serviceAccountCredentials = credentialsProvider.getCredentials();
    var accessKeyId = serviceAccountCredentials.getAWSAccessKeyId();
    var secretAccessKey = serviceAccountCredentials.getAWSSecretKey();
    var sessionToken = serviceAccountCredentials.getSessionToken();

    return new AWSCredentialsDTO(
        secretAccessKey, accessKeyId, sessionToken, awsCredentialsServiceConfig.getRegion());
  }
}
