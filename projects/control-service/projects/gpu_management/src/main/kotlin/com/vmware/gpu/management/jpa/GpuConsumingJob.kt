package com.vmware.gpu.management.jpa

import com.vmware.gpu.management.api.DeviceType
import com.vmware.gpu.management.api.JobUniqueIdentifier
import jakarta.persistence.*
import jakarta.transaction.Transactional
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.data.jpa.repository.Modifying
import org.springframework.data.jpa.repository.Query
import org.springframework.data.repository.query.Param
import org.springframework.stereotype.Repository
import java.lang.Exception
import java.time.LocalDateTime
import java.util.*


@Entity
class GpuConsumingJob(
    var jobName: String,
    val consumedResources: Float,
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "node_name")
    val nodeWithGPUs: NodeWithGPUs,
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "team_name")
    val gpuResourcesPerTeam: GpuResourcesPerTeam,
    @Column(nullable = false, updatable = false)
    private val createdAt: LocalDateTime = LocalDateTime.now(),
    @Id
    val id: String = gpuResourcesPerTeam.teamName + "____" + jobName,
    var priority: Boolean = false
) {


    override fun toString(): String {
        return "GpuConsumingJob{" +
                "jobName='" + jobName + '\'' +
                ", consumedResources=" + consumedResources +
                ", createdAt=" + createdAt +
                '}'
    }
}



@Repository
interface GpuConsumingJobRepo : JpaRepository<GpuConsumingJob, String> {

    @Query("SELECT COALESCE(SUM(g.consumedResources),0) FROM GpuConsumingJob g " +
            "WHERE g.gpuResourcesPerTeam.teamName = :teamName AND g.nodeWithGPUs.deviceType = :deviceType")
    fun sumConsumedResourcesByTeam(@Param("teamName") teamName: String, deviceType: DeviceType): Float


    fun findByNodeWithGPUsDeviceType(deviceType: DeviceType): List<GpuConsumingJob>

    @Transactional
    @Modifying
    @Query("DELETE FROM GpuConsumingJob g WHERE g.id = ?1")
    fun removeOptional(id: String): Int


    @Transactional
    @Modifying
    @Query("UPDATE GpuConsumingJob g SET g.nodeWithGPUs = :newNode WHERE g.jobName = :jobName " +
            "AND g.gpuResourcesPerTeam.teamName = :teamName")
    fun updateNodeForJobOptional(
        jobName: String,
        teamName: String,
        newNode: NodeWithGPUs
    ): Int

}


fun GpuConsumingJobRepo.remove(id: String){
    val removeOptional = removeOptional(id)
    if(removeOptional !=1)
        throw Exception("remove updated an unexpected number of rows which was $removeOptional")
}

fun GpuConsumingJobRepo.updateNodeForJob(
    jobUniqueIdentifier: JobUniqueIdentifier,
    newNode: NodeWithGPUs
) {
    val updateNodeForJobOptional = updateNodeForJobOptional(jobUniqueIdentifier.jobName,
        jobUniqueIdentifier.teamName, newNode)
    if(updateNodeForJobOptional !=1)
        throw Exception("updateNodeForJob updated an unexpected number of rows which was $updateNodeForJobOptional")
}
