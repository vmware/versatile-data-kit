/*
 * Copyright 2023-2024 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.gpu.jpa;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;
@Repository
public interface GpuResourcesPerTeamRepo extends JpaRepository<GpuResourcesPerTeam, String> {

    @Query("SELECT g " +
            "FROM GpuResourcesPerTeam g " +
            "GROUP BY g " +
            "HAVING (SELECT SUM(j.consumedResources) FROM GpuConsumingJob j WHERE j.gpuResourcesPerTeam = g) > g.resources")
    List<GpuResourcesPerTeam> findTeamsOverusingResources();
}
