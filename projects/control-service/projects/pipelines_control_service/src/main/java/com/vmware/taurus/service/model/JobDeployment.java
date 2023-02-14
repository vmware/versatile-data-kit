/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.model;

import com.vmware.taurus.controlplane.model.data.DataJobResources;
import lombok.Data;

/**
 * Store this in the database if the data job configuration could not or should not be retrieved
 * from the kubernetes manifest of the data job deployment like Airflow DAG locations.
 */
@Data
public class JobDeployment {

  private String dataJobTeam;

  private String dataJobName;

  private String gitCommitSha;

  private String vdkVersion;

  private String imageName;

  private String cronJobName;

  /**
   * When disabled, the DataJob will still be deployed but it will never be executed. When enabled,
   * the DataJob will be executed according to its {@link JobConfig#getSchedule()}
   */
  private Boolean enabled;

  private String mode;

  private DataJobResources resources;
}
