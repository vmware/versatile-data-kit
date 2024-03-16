/*
 * Copyright 2023-2024 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.gpu;

import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.gpu.jpa.*;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import java.util.HashSet;

import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest(
        webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT,
        classes = ControlplaneApplication.class)
class GpuResourceManagerTest {


    @Autowired
    private GpuConsumingJobRepo gpuConsumingJobRepo;

    @Autowired
    private GpuResourcesPerTeamRepo gpuResourcesPerTeamRepo;


    @Autowired
    private NodeWithGPURepo nodeWithGPURepo;


    @Autowired
    private  GpuResourceManager  gpuResourceManager;

    @Test
    public void saveFirstJob(){
        GpuResourcesPerTeam teamA = gpuResourcesPerTeamRepo.save(new GpuResourcesPerTeam("Team A", 10f, new HashSet<>()));
        NodeWithGPUs node1 = nodeWithGPURepo.save(new NodeWithGPUs("machine 1", 4, new HashSet<>()));


        gpuResourceManager.tryProvisionResources(teamA.getTeamName(), "my first job", 3.0f);
    }

    @Test
    public void saveJobWhenOtherTeamIsOverProvisioned(){
        GpuResourcesPerTeam teamA = gpuResourcesPerTeamRepo.save(new GpuResourcesPerTeam("Team A", 10f, new HashSet<>()));
        GpuResourcesPerTeam teamb = gpuResourcesPerTeamRepo.save(new GpuResourcesPerTeam("Team B", 4f, new HashSet<>()));
        NodeWithGPUs node1 = nodeWithGPURepo.save(new NodeWithGPUs("machine 1", 10, new HashSet<>()));


        gpuResourceManager.tryProvisionResources(teamb.getTeamName(), "Job 1", 3.0f);
        gpuResourceManager.tryProvisionResources(teamb.getTeamName(), "Job 2", 3.0f);
        gpuResourceManager.tryProvisionResources(teamb.getTeamName(), "Job 3", 3.0f);
        gpuResourceManager.tryProvisionResources(teamA.getTeamName(), "my first job", 3.0f);
    }
}
