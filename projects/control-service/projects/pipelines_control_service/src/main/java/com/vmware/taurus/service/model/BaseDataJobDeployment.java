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
@EqualsAndHashCode
@ToString
@MappedSuperclass
public abstract class BaseDataJobDeployment {

  @Id
  @Column(name = "data_job_name")
  private String dataJobName;

  @MapsId
  @OneToOne(cascade = CascadeType.MERGE)
  @JoinColumn(name = "data_job_name")
  @ToString.Exclude
  @EqualsAndHashCode.Exclude
  private DataJob dataJob;

  private String pythonVersion;

  private String gitCommitSha;

  private String schedule;

  private Float resourcesCpuRequestCores; // TODO embeded DataJobDeploymentResources

  private Float resourcesCpuLimitCores;

  private Integer resourcesMemoryRequestMi;

  private Integer resourcesMemoryLimitMi;

  private String lastDeployedBy;

  private Boolean enabled;

  public BaseDataJobDeployment() {
  }

  public BaseDataJobDeployment(String dataJobName, DataJob dataJob, String pythonVersion, String gitCommitSha, Float resourcesCpuRequestCores, Float resourcesCpuLimitCores, Integer resourcesMemoryRequestMi, Integer resourcesMemoryLimitMi, String lastDeployedBy, Boolean enabled) {
    this.dataJobName = dataJobName;
    this.dataJob = dataJob;
    this.pythonVersion = pythonVersion;
    this.gitCommitSha = gitCommitSha;
    this.resourcesCpuRequestCores = resourcesCpuRequestCores;
    this.resourcesCpuLimitCores = resourcesCpuLimitCores;
    this.resourcesMemoryRequestMi = resourcesMemoryRequestMi;
    this.resourcesMemoryLimitMi = resourcesMemoryLimitMi;
    this.lastDeployedBy = lastDeployedBy;
    this.enabled = enabled;
  }
}
