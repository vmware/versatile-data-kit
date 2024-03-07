package com.vmware.taurus.gpu.jpa;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

public interface GpuConsumingJobRepo extends JpaRepository<GpuConsumingJob, Long> {
    void deleteByJobNameAndGpTeamName(String jobName, String teamName);

    @Query("SELECT SUM(g.consumedResources) FROM GpuConsumingJob g WHERE g.gpuResourcesPerTeam.teamName = :teamName")
    Float sumConsumedResourcesByTeam(@Param("teamName") String teamName);
}
