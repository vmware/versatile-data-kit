/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.deploy;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.Setter;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;

@Configuration
@ConfigurationProperties(prefix = "datajobs.deployment.configuration.persistence")
@Setter
@Getter
public class DataJobDeploymentPropertiesConfig {

  @AllArgsConstructor
  public enum PropertyPersistence {
    DB,
    K8S
  }

  private boolean writeToK8S;
  private boolean writeToDB;
  private PropertyPersistence readDataSource;
}
