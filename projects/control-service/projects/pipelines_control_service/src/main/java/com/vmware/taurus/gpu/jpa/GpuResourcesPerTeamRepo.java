package com.vmware.taurus.gpu.jpa;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;

import java.util.List;
import java.util.Optional;

public interface GpuResourcesPerTeamRepo extends JpaRepository<GpuResourcesPerTeam, String> {

    @Query("SELECT g, (SELECT SUM(j.consumedResources) FROM GpuConsumingJob j WHERE j.gpuResourcesPerTeam = g) AS totalConsumed " +
            "FROM GpuResourcesPerTeam g " +
            "GROUP BY g " +
            "HAVING totalConsumed > g.resources " +
            "ORDER BY totalConsumed - g.resources DESC")
    List<GpuResourcesPerTeam> findTeamsOverusingResources();
}
