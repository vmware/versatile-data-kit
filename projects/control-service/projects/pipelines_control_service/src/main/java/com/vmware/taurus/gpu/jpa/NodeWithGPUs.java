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
public class NodeWithGPUs {

    @Id
    private String name;

    private int deviceCount;

    @OneToMany(mappedBy = "nodeWithGPUs", cascade = CascadeType.ALL, fetch = FetchType.EAGER)
    private Set<GpuConsumingJob> gpuConsumingJobs = new HashSet<>();


    @Override
    public boolean equals(Object obj) {
        if (this == obj) {
            return true;
        }
        if (!(obj instanceof NodeWithGPUs other)) {
            return false;
        }
        return java.util.Objects.equals(name, other.name);
    }

    @Override
    public int hashCode() {
        return java.util.Objects.hash(name);
    }

}
