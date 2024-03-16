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
import java.util.Objects;
import java.util.Set;

@Data
@AllArgsConstructor
@NoArgsConstructor
@Entity
public class GpuResourcesPerTeam {
    @Id
    private String teamName;
    private float resources;

    @OneToMany(mappedBy = "gpuResourcesPerTeam", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    private Set<GpuConsumingJob> gpuConsumingJobs = new HashSet<>();

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        GpuResourcesPerTeam that = (GpuResourcesPerTeam) o;
        return Float.compare(resources, that.resources) == 0 && Objects.equals(teamName, that.teamName);
    }

    @Override
    public int hashCode() {
        return Objects.hash(teamName, resources);
    }
}
