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
import com.vmware.taurus.exception.AuthorizationError;
import java.util.Map;
import java.util.UUID;
import lombok.Getter;
import org.springframework.beans.factory.annotation.Value;
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
public class AWSCredentialsService {

  public static final String AWS_SERVICE_ACCOUNT_SECRET_ACCESS_KEY = "AWS_SERVICE_ACCOUNT_SECRET_ACCESS_KEY";
  public static final String AWS_SERVICE_ACCOUNT_ACCESS_KEY_ID = "AWS_SERVICE_ACCOUNT_ACCESS_KEY_ID";
  public static final String AWS_SERVICE_ACCOUNT_SESSION_TOKEN = "AWS_SERVICE_ACCOUNT_SESSION_TOKEN";

  @Getter
  private String awsRegion;

  @Getter
  private boolean assumeIAMRole;

  @Getter
  private String awsSecretAccessKey;

  @Getter
  private String awsAccessKeyId;

  private STSAssumeRoleSessionCredentialsProvider credentialsProvider;

  public AWSCredentialsService(
      @Value("${datajobs.aws.serviceAccountSecretAccessKey:}") String serviceAccountSecretKey,
      @Value("${datajobs.aws.serviceAccountAccessKeyId:}") String serviceAccountAcessKeyId,
      @Value("${datajobs.aws.RoleArn:}") String awsServiceAccountRoleArn,
      @Value("${datajobs.aws.defaultSessionDurationSeconds:}") int serviceAccountSessionDuration,
      @Value("${datajobs.aws.region:}") String awsRegion,
      @Value("${datajobs.aws.assumeIAMRole:false}") boolean assumeIAMRole,
      @Value("${datajobs.aws.secretAccessKey:}") String awsSecretAccessKey,
      @Value("${datajobs.aws.accessKeyId:}") String awsAccessKeyId) {

    this.awsRegion = awsRegion;
    this.assumeIAMRole = assumeIAMRole;
    this.awsSecretAccessKey = awsSecretAccessKey;
    this.awsAccessKeyId = awsAccessKeyId;

    if (assumeIAMRole) {
      AWSSecurityTokenService stsClient =
          AWSSecurityTokenServiceClientBuilder.standard()
              .withCredentials(
                  new AWSStaticCredentialsProvider(
                      new BasicAWSCredentials(serviceAccountAcessKeyId,
                          serviceAccountSecretKey)))
              .withRegion(awsRegion)
              .build();

      AssumeRoleRequest assumeRequest =
          new AssumeRoleRequest()
              .withRoleArn(awsServiceAccountRoleArn)
              .withRoleSessionName(
                  "control-service-session-" + UUID.randomUUID().toString().substring(0, 4))
              .withDurationSeconds(serviceAccountSessionDuration);

      this.credentialsProvider =
          new STSAssumeRoleSessionCredentialsProvider.Builder(
              assumeRequest.getRoleArn(), assumeRequest.getRoleSessionName())
              .withStsClient(stsClient)
              .build();

    }
  }

  /**
   * Returns a map containing AWS temporary credentials for authorization against AWS API's The keys
   * to the returned map are: AWS_SERVICE_ACCOUNT_SECRET_ACCESS_KEY AWS_SERVICE_ACCOUNT_ACCESS_KEY_ID
   * AWS_SERVICE_ACCOUNT_SESSION_TOKEN
   */
  public Map<String, String> createTemporaryCredentials() {
    if (!assumeIAMRole) {
      throw new AuthorizationError(
          "createTemporaryCredentials() method called when the datajobs.aws.assumeIAMRole flag is false.",
          "The call will fail, and no credentials will be returned.",
          "Please configure all appropriate properties for aws service account pattern in application.properties.",
          null);
    }
    AWSSessionCredentials serviceAccountCredentials = credentialsProvider.getCredentials();
    var accessKeyId = serviceAccountCredentials.getAWSAccessKeyId();
    var secretAccessKey = serviceAccountCredentials.getAWSSecretKey();
    var sessionToken = serviceAccountCredentials.getSessionToken();

    return Map.of(AWS_SERVICE_ACCOUNT_ACCESS_KEY_ID, accessKeyId,
        AWS_SERVICE_ACCOUNT_SECRET_ACCESS_KEY, secretAccessKey, AWS_SERVICE_ACCOUNT_SESSION_TOKEN,
        sessionToken);
  }
}
