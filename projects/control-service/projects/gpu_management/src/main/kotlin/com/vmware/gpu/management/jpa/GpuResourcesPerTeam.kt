package com.vmware.gpu.management.jpa

import jakarta.persistence.*
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.data.jpa.repository.Query
import org.springframework.stereotype.Repository
import java.util.*

@Entity
data class GpuResourcesPerTeam(@Id val teamName: String,
                               val resources: Float)

@Repository
interface GpuResourcesPerTeamRepo : JpaRepository<GpuResourcesPerTeam, String> {
    @Query(
        "SELECT g " +
                "FROM GpuResourcesPerTeam g " +
                "GROUP BY g " +
                "HAVING (SELECT SUM(j.consumedResources) FROM GpuConsumingJob j WHERE j.gpuResourcesPerTeam = g) > g.resources"
    )
    fun findTeamsOverusingResources(): List<GpuResourcesPerTeam>
}
