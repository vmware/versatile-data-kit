/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.model;

import lombok.EqualsAndHashCode;
import lombok.Getter;
import lombok.Setter;
import lombok.ToString;

import javax.persistence.Entity;

@Getter
@Setter
@EqualsAndHashCode(callSuper = false)
@ToString
@Entity
public class DesiredDataJobDeployment extends BaseDataJobDeployment {

    private DeploymentStatus status;
}
