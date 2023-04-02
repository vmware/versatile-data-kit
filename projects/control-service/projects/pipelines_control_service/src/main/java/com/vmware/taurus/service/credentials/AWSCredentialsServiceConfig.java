/*
 * Copyright 2023-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.credentials;

import lombok.Getter;
import lombok.Setter;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;

@Configuration
@ConfigurationProperties(prefix = "datajobs.aws")
@Getter
@Setter
public class AWSCredentialsServiceConfig {

  private String region;
  private String serviceAccountSecretAccessKey;
  private String serviceAccountAccessKeyId;
  private String roleArn;
  private int defaultSessionDurationSeconds;
  private boolean assumeIAMRole;
  private String secretAccessKey;
  private String accessKeyId;
}
