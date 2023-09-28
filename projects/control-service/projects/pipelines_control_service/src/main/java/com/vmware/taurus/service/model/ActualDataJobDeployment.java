/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.model;

import lombok.*;

import javax.persistence.*;
import java.time.OffsetDateTime;

@Getter
@Setter
@EqualsAndHashCode(callSuper = true)
@ToString
@Entity
public class ActualDataJobDeployment extends BaseDataJobDeployment {

  private String deploymentVersionSha;

  private OffsetDateTime lastDeployedDate;

  public ActualDataJobDeployment() {
    super();
  }

  public ActualDataJobDeployment(String dataJobName, DataJob dataJob, String pythonVersion, String gitCommitSha, Float resourcesCpuRequest, Float resourcesCpuLimit, Integer resourcesMemoryRequest, Integer resourcesMemoryLimit, OffsetDateTime lastDeployedDate, String lastDeployedBy, Boolean enabled, String deploymentVersionSha) {
    super(dataJobName, dataJob, pythonVersion, gitCommitSha, resourcesCpuRequest, resourcesCpuLimit, resourcesMemoryRequest, resourcesMemoryLimit, lastDeployedBy, enabled);
    this.deploymentVersionSha = deploymentVersionSha;
    this.lastDeployedDate = lastDeployedDate;
  }
}
