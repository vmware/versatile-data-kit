/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.model;

import com.vmware.taurus.controlplane.model.data.DataJobResources;
import lombok.Data;

/** Object used for providing users with information about data job deployments. */
@Data
public class JobDeploymentStatus {

  private String dataJobName;

  private String gitCommitSha;

  private String vdkImageName;

  private String vdkVersion;

  private String imageName;

  private String cronJobName;

  private Boolean enabled;

  private String mode;

  private DataJobResources resources;

  private String lastDeployedBy;

  private String lastDeployedDate;
}
