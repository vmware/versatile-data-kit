package com.vmware.taurus.gpu.jpa;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import javax.persistence.*;
import java.time.LocalDateTime;
import java.util.HashSet;
import java.util.Set;

@Data
@NoArgsConstructor
@Entity
public class GpuConsumingJob {
    @Id
    private Long id;

    private String jobName;
    private boolean lowPriority;
    private float consumedResources;


    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "node_name") // This column is added to the GpuConsumingJob table as a foreign key.
    private NodeWithGPUs nodeWithGPUs;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "team_name") // This column is added to the GpuConsumingJob table as a foreign key.
    private GpuResourcesPerTeam gpuResourcesPerTeam;


    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt;


    public GpuConsumingJob(GpuResourcesPerTeam gpuResourcesPerTeam,String jobName, float consumedResources, NodeWithGPUs nodeWithGPUs){
        this.gpuResourcesPerTeam = gpuResourcesPerTeam;
        this.jobName = jobName;
        this.consumedResources = consumedResources;
        this.nodeWithGPUs = nodeWithGPUs;
        this.createdAt = LocalDateTime.now();
    }

}
