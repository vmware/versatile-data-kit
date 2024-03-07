/*
 * Copyright 2023-2024 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.gpu.jpa;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import javax.persistence.*;
import java.util.HashSet;
import java.util.Set;

@Data
@AllArgsConstructor
@NoArgsConstructor
@Entity
public class GpuResourcesPerTeam {
    @Id
    private String teamName;
    private float resources;

    @OneToMany(mappedBy = "nodeWithGPUs", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    private Set<GpuConsumingJob> gpuConsumingJobs = new HashSet<>();
}
