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
@NoArgsConstructor
@AllArgsConstructor
@EqualsAndHashCode
@ToString
@Entity
public class DataJobDeployment {

    @Id
    @Column(name = "data_job_name")
    private String dataJobName;

    @OneToOne(mappedBy = "dataJobDeployment")
    @ToString.Exclude
    @EqualsAndHashCode.Exclude
    private DataJob dataJob;

    private String deploymentVersionSha;

    private String pythonVersion;

    private String gitCommitSha;

    private Float resourcesCpuRequest;

    private Float resourcesCpuLimit;

    private Integer resourcesMemoryRequest;

    private Integer resourcesMemoryLimit;

    private OffsetDateTime lastDeployedDate;

    private String lastDeployedBy;

    private Boolean enabled;
}
