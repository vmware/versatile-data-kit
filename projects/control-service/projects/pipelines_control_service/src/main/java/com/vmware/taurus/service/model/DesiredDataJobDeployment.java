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
@EqualsAndHashCode(callSuper = true)
@ToString
@Entity
public class DesiredDataJobDeployment extends BaseDataJobDeployment {
    public DesiredDataJobDeployment() {
        super();
    }

    public DesiredDataJobDeployment(String dataJobName, DataJob dataJob, String pythonVersion, String gitCommitSha, Float resourcesCpuRequestCores, Float resourcesCpuLimitCores, Integer resourcesMemoryRequestMi, Integer resourcesMemoryLimitMi, String lastDeployedBy, Boolean enabled) {
        super(dataJobName, dataJob, pythonVersion, gitCommitSha, resourcesCpuRequestCores, resourcesCpuLimitCores, resourcesMemoryRequestMi, resourcesMemoryLimitMi, lastDeployedBy, enabled);
    }
}
