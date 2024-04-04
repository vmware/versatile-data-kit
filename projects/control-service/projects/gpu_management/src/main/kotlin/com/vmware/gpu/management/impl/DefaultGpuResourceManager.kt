package com.vmware.gpu.management.impl

import com.vmware.gpu.management.impl.solver.JobForSolver
import com.vmware.gpu.management.impl.solver.OptimalNodePacker
import com.google.ortools.Loader
import com.vmware.gpu.management.api.*
import com.vmware.gpu.management.jpa.*
import jakarta.transaction.Transactional
import org.springframework.stereotype.Component

@Component
class DefaultGpuResourceManager(
    val gpuResourcesPerTeamRepo: GpuResourcesPerTeamRepo,
    val gpuConsumingJobRepo: GpuConsumingJobRepo,
    val nodeWithGPURepo: NodeWithGPURepo,
    val optimalNodePacker: OptimalNodePacker
) : GpuResourceManager {

    companion object {
        init {
            Loader.loadNativeLibraries()
        }
    }

    override fun jobEnded(jobUniqueIdentifier: JobUniqueIdentifier) {
        gpuConsumingJobRepo.deleteById(jobUniqueIdentifier.uniqueID)
    }

    override fun markJobPriority(jobUniqueIdentifier: JobUniqueIdentifier, priority: Boolean) {
        val findById = gpuConsumingJobRepo.findById(jobUniqueIdentifier.uniqueID).get()
        findById.priority = priority
        gpuConsumingJobRepo.save(findById)
    }

    @Transactional
    override fun tryProvisionResources(jobUniqueIdentifier: JobUniqueIdentifier, amount: Float): List<JobAction> {
        return tryProvisionResourcesI(ProvisionResourceRequest(jobUniqueIdentifier, amount)).onEach {
            when (it) {
                is CreateJob -> gpuConsumingJobRepo.save(
                    GpuConsumingJob(
                        jobUniqueIdentifier.jobName, amount, nodeWithGPURepo.getReferenceById(it.nodeName),
                        gpuResourcesPerTeamRepo.getReferenceById(jobUniqueIdentifier.teamName)
                    )
                )
                is DeleteJob -> gpuConsumingJobRepo.remove(it.uId)
                is MoveJob -> gpuConsumingJobRepo.updateNodeForJob(
                    it.jobUniqueIdentifier, nodeWithGPURepo.findById(it.nodeName).get()
                )
            }
        }

    }

    fun tryProvisionResourcesI(provisionResourceRequest: ProvisionResourceRequest): List<JobAction> {

        // Rule 1: if there is free space put it there.
        val nodesWithAvailableGPUs = nodeWithGPURepo.findNodesWithAvailableGPUs(provisionResourceRequest.amount)
        return if (nodesWithAvailableGPUs.isNotEmpty()) {
            val nodeWithGPUs = nodesWithAvailableGPUs[0]
            listOf<JobAction>(CreateJob(nodeWithGPUs.name, provisionResourceRequest))
            // Rule 2: if no free space and not within budget. then its a no-op
        } else if (gpuConsumingJobRepo.sumConsumedResourcesByTeam(provisionResourceRequest.teamName) + provisionResourceRequest.amount > gpuResourcesPerTeamRepo.findById(
                provisionResourceRequest.teamName
            ).get().resources
        ) {
            mutableListOf()
        } else {
            // Rule 3: run linear optimization
            reshuffleToFit(provisionResourceRequest)
        }
    }

    private fun reshuffleToFit(provisionResourceRequest: ProvisionResourceRequest): List<JobAction> {
        val teamsOverBudget = gpuResourcesPerTeamRepo.findTeamsOverusingResources().map { it.teamName }.toSet()
        val allJobs = gpuConsumingJobRepo.findAll().map {
            JobForSolver(
                JobUniqueIdentifier(it.jobName, it.gpuResourcesPerTeam.teamName),
                it.consumedResources,
                teamsOverBudget.contains(it.gpuResourcesPerTeam.teamName) && !it.priority, it.nodeWithGPUs.name
            )
        } + JobForSolver(
            provisionResourceRequest.jobUniqueIdentifier,
            provisionResourceRequest.amount, false
        )
        val nodes = nodeWithGPURepo.findAll()
        return optimalNodePacker.reshuffleToFit(allJobs, nodes)
    }

}
