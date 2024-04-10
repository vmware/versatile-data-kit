package com.vmware.gpu.management.jpa

import com.vmware.gpu.management.api.DeviceRequirements
import com.vmware.gpu.management.api.DeviceType
import jakarta.persistence.CascadeType
import jakarta.persistence.Entity
import jakarta.persistence.FetchType
import jakarta.persistence.Id
import jakarta.persistence.OneToMany
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.data.jpa.repository.Query
import org.springframework.data.repository.query.Param
import org.springframework.stereotype.Repository
import java.util.*




@Entity
class NodeWithGPUs(@Id val name: String,
                   val deviceCount: Int,
                   val deviceType: DeviceType) {
    @OneToMany(mappedBy = "nodeWithGPUs", cascade = [CascadeType.ALL], fetch = FetchType.EAGER)
    val gpuConsumingJobs: Set<GpuConsumingJob> = HashSet()
}
@Repository
interface NodeWithGPURepo : JpaRepository<NodeWithGPUs, String> {
    @Query(
        "SELECT n FROM NodeWithGPUs n LEFT JOIN n.gpuConsumingJobs g " +
                "WHERE n.deviceType = :deviceType " +
                "GROUP BY n HAVING n.deviceCount >=  :additionalResources+COALESCE(SUM(g.consumedResources), 0) " +
                "ORDER BY n.deviceCount - :additionalResources+COALESCE(SUM(g.consumedResources), 0) "
    )
    fun findNodesWithAvailableGPUs(additionalResources: Float,
                                   deviceType: DeviceType): List<NodeWithGPUs>
}


fun NodeWithGPURepo.findNodesWithAvailableGPUs(deviceRequirements: DeviceRequirements): List<NodeWithGPUs> = this.findNodesWithAvailableGPUs(
    deviceRequirements.amount ,  deviceRequirements.deviceType)
