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

    @OneToMany(mappedBy = "gpuResourcesPerTeam", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
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
