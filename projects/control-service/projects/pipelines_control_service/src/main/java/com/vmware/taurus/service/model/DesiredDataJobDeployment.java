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
@EqualsAndHashCode(callSuper = false)
@ToString
@Entity
public class DesiredDataJobDeployment extends BaseDataJobDeployment {

  @MapsId
  @OneToOne(cascade = CascadeType.MERGE)
  @JoinColumn(name = "data_job_name")
  @ToString.Exclude
  @EqualsAndHashCode.Exclude
  private DataJob dataJob;

  private DeploymentStatus status;

  @Column(name = "is_user_initiated")
  private Boolean userInitiated;
}
