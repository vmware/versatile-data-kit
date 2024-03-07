/*
 * Copyright 2023-2024 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.gpu.jpa;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

@Repository
public interface GpuConsumingJobRepo extends JpaRepository<GpuConsumingJob, Long> {
    void deleteByJobNameAndGpuResourcesPerTeam_TeamName(String jobName, String teamName);

    @Query("SELECT COALESCE(SUM(g.consumedResources),0) FROM GpuConsumingJob g WHERE g.gpuResourcesPerTeam.teamName = :teamName")
    Float sumConsumedResourcesByTeam(@Param("teamName") String teamName);
}
