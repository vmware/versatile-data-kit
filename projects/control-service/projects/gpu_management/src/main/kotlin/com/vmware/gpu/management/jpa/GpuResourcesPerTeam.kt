package com.vmware.gpu.management.jpa

import com.vmware.gpu.management.api.DeviceType
import jakarta.persistence.*
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.data.jpa.repository.Query
import org.springframework.stereotype.Repository

@Entity
data class GpuResourcesPerTeam(
    val teamName: String,
    val deviceType: DeviceType,
    val resources: Float) {

    @Id
    @GeneratedValue
    var id: Long = 0
}

@Repository
interface GpuResourcesPerTeamRepo : JpaRepository<GpuResourcesPerTeam, Long> {
    @Query(
        "SELECT g " +
                "FROM GpuResourcesPerTeam g WHERE g.deviceType = :deviceType " +
                "GROUP BY g " +
                "HAVING (SELECT SUM(j.consumedResources) FROM GpuConsumingJob j " +
                "WHERE j.gpuResourcesPerTeam = g and j.nodeWithGPUs.deviceType = :deviceType) > g.resources"
    )
    fun findTeamsOverusingResources(deviceType: DeviceType): List<GpuResourcesPerTeam>


    fun findByTeamNameAndDeviceType(teamName: String,deviceType: DeviceType): GpuResourcesPerTeam?
}


fun GpuResourcesPerTeamRepo.find(teamName: String, deviceType: DeviceType) = this.findByTeamNameAndDeviceType(teamName, deviceType)?: GpuResourcesPerTeam(teamName, deviceType, 0f)
