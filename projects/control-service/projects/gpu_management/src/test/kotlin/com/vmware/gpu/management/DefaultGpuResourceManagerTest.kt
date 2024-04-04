package com.vmware.gpu.management

import com.vmware.gpu.management.api.*
import com.vmware.gpu.management.jpa.*
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Test
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.test.context.SpringBootTest
import org.springframework.test.annotation.DirtiesContext


@SpringBootTest(classes = [DemoApplication::class])
@DirtiesContext(classMode = DirtiesContext.ClassMode.AFTER_EACH_TEST_METHOD)
internal class GpuResourceManagerTest @Autowired constructor(
    val gpuConsumingJobRepo: GpuConsumingJobRepo,
    val gpuResourcesPerTeamRepo: GpuResourcesPerTeamRepo,
    val nodeWithGPURepo: NodeWithGPURepo,
    val gpuResourceManager: GpuResourceManager
) {


    @Test
    fun `when the cluster is empty I can deploy a job`() {
        val teamA = gpuResourcesPerTeamRepo.save(GpuResourcesPerTeam("Team A", 10f))
        val node1 = nodeWithGPURepo.save(NodeWithGPUs("machine 1", 10))


        val result = gpuResourceManager.tryProvisionResources(JobUniqueIdentifier("my first job", teamA.teamName), 3.0f)

        assert(result == listOf(CreateJob(node1.name, JobUniqueIdentifier("my first job", teamA.teamName),3.0f)))
        assert(nodeWithGPURepo.findAll().size == 1)
    }

    @Test
    fun `save job when other team is over provisioned`() {
        val teamA = gpuResourcesPerTeamRepo.save(GpuResourcesPerTeam("Team A", 10f))
        val teamb = gpuResourcesPerTeamRepo.save(GpuResourcesPerTeam("Team B", 4f))
        val node1 = nodeWithGPURepo.save(NodeWithGPUs("machine 1", 10))


        gpuResourceManager.tryProvisionResources(JobUniqueIdentifier("Job 1",teamb.teamName), 3.0f)
        gpuResourceManager.tryProvisionResources(JobUniqueIdentifier("Job 2",teamb.teamName), 3.0f)
        gpuResourceManager.tryProvisionResources(JobUniqueIdentifier("Job 3", teamb.teamName), 3.0f)
        val result = gpuResourceManager.tryProvisionResources(JobUniqueIdentifier("my first job",teamA.teamName), 3.0f)

        assert(result[0] is DeleteJob)
        assert(result[1] is CreateJob)

        assertEquals(gpuConsumingJobRepo.findAll().size, 3)
        val numberOfJobsPerTeam = gpuConsumingJobRepo.findAll().map { it.gpuResourcesPerTeam.teamName }.groupBy { it }.mapValues { it.value.size }
        assertEquals(numberOfJobsPerTeam["Team B"], 2)
        assertEquals(numberOfJobsPerTeam["Team A"], 1)
    }


    @Test
    fun `move jobs around to schedule big job`() {
        val teamA = gpuResourcesPerTeamRepo.save(GpuResourcesPerTeam("Team A", 10f))
        val teamB = gpuResourcesPerTeamRepo.save(GpuResourcesPerTeam("Team B", 10f))
        val node1 = nodeWithGPURepo.save(NodeWithGPUs("machine 1", 10))
        val node2 = nodeWithGPURepo.save(NodeWithGPUs("machine 2", 10))

        gpuConsumingJobRepo.save(GpuConsumingJob("Job 1",3.0f, node1, teamB))
        gpuConsumingJobRepo.save(GpuConsumingJob("Job 2",3.0f, node1, teamB))
        gpuConsumingJobRepo.save(GpuConsumingJob("Job 3",3.0f, node2, teamB))


        val result =gpuResourceManager.tryProvisionResources( JobUniqueIdentifier("My first job",teamA.teamName), 9.0f)

        assert(result[0] is MoveJob)
        assert(result[1] is CreateJob)

        assertEquals(gpuConsumingJobRepo.findAll().size, 4)
        val numberOfJobsPerTeam = gpuConsumingJobRepo.findAll().map { it.gpuResourcesPerTeam.teamName }.groupBy { it }.mapValues { it.value.size }
        assertEquals(numberOfJobsPerTeam["Team B"], 3)
        assertEquals(numberOfJobsPerTeam["Team A"], 1)
    }
    @Test
    fun `If there is no where to put my job it won't get placed even if I have budget`() {
        val teamA = gpuResourcesPerTeamRepo.save(GpuResourcesPerTeam("Team A", 10f))
        val teamB = gpuResourcesPerTeamRepo.save(GpuResourcesPerTeam("Team B", 13f))
        val node1 = nodeWithGPURepo.save(NodeWithGPUs("machine 1", 10))
        val node2 = nodeWithGPURepo.save(NodeWithGPUs("machine 2", 10))

        gpuConsumingJobRepo.save(GpuConsumingJob("Job 1",3.0f, node1, teamB))
        gpuConsumingJobRepo.save(GpuConsumingJob("Job 2",3.0f, node1, teamB))
        gpuConsumingJobRepo.save(GpuConsumingJob("Job 3",3.0f, node2, teamB))
        gpuConsumingJobRepo.save(GpuConsumingJob("Job 4",3.0f, node2, teamB))

        assertThrows(
            Exception::class.java,
        ) { gpuResourceManager.tryProvisionResources( JobUniqueIdentifier("My first job",teamA.teamName), 9.0f) }
    }

}
