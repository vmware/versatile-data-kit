/*
 * Copyright 2023-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.credentials;

import lombok.Getter;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

@ConfigurationProperties(prefix = "datajobs.aws")
@Component
public class AWSCredentialsServiceConfig {
  @Getter
  private String region;
  @Getter
  private String serviceAccountSecretAccessKey;
  @Getter
  private String serviceAccountAccessKeyId;
  @Getter
  private String RoleArn;
  @Getter
  private int defaultSessionDurationSeconds;
  @Getter
  private boolean assumeIAMRole;
  @Getter
  private String secretAccessKey;
  @Getter
  private String accessKeyId;
}
