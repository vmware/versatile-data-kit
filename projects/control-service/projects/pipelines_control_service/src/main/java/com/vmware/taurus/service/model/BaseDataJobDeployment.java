/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.model;

import lombok.EqualsAndHashCode;
import lombok.Getter;
import lombok.Setter;
import lombok.ToString;

import javax.persistence.*;

@Getter
@Setter
@EqualsAndHashCode
@ToString
@MappedSuperclass
public abstract class BaseDataJobDeployment {

  @Id
  @Column(name = "data_job_name")
  private String dataJobName;

  private String pythonVersion;

  private String gitCommitSha;

  private String schedule;

  @Embedded private DataJobDeploymentResources resources;

  private String lastDeployedBy;

  private Boolean enabled;
}
