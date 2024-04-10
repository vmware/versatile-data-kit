package com.vmware.gpu.management.impl

import com.vmware.gpu.management.impl.solver.JobForSolver
import com.vmware.gpu.management.impl.solver.OptimalNodePacker
import com.google.ortools.Loader
import com.vmware.gpu.management.api.*
import com.vmware.gpu.management.jpa.*
import jakarta.transaction.Transactional
import org.slf4j.Logger
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Component

@Component
class DefaultGpuResourceManager(
    val gpuResourcesPerTeamRepo: GpuResourcesPerTeamRepo,
    val gpuConsumingJobRepo: GpuConsumingJobRepo,
    val nodeWithGPURepo: NodeWithGPURepo,
    val optimalNodePacker: OptimalNodePacker
) : GpuResourceManager {
    private val log: Logger = LoggerFactory.getLogger(this.javaClass)

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
    override fun tryProvisionResources(
        jobUniqueIdentifier: JobUniqueIdentifier,
        deviceRequirements: DeviceRequirements
    ): List<JobAction> {
        return tryProvisionResourcesI(
            ProvisionResourceRequest(
                jobUniqueIdentifier,
                listOf(deviceRequirements)
            )
        ).onEach {
            when (it) {
                is CreateJob -> {
                    val nodeWithGPUs = nodeWithGPURepo.getReferenceById(it.nodeName)
                    gpuConsumingJobRepo.save(
                        GpuConsumingJob(
                            jobUniqueIdentifier.jobName, deviceRequirements.amount,
                            nodeWithGPUs,
                            gpuResourcesPerTeamRepo.find(jobUniqueIdentifier.teamName, nodeWithGPUs.deviceType)
                        )
                    )
                }

                is DeleteJob -> gpuConsumingJobRepo.remove(it.uId)
                is MoveJob -> gpuConsumingJobRepo.updateNodeForJob(
                    it.jobUniqueIdentifier, nodeWithGPURepo.findById(it.nodeName).get()
                )
            }
        }

    }

    fun tryProvisionResourcesI(provisionResourceRequest: ProvisionResourceRequest): List<JobAction> {

        // Rule 1: if there is free space put it there.
        val nodeWithGPUs = provisionResourceRequest.allDevicePossibilities
            .map { it.amount to nodeWithGPURepo.findNodesWithAvailableGPUs(it) }
            .firstOrNull { it.second.isNotEmpty() }?.let { it.first to it.second.first() }?.let {
                listOf<JobAction>(CreateJob(it.second.name, provisionResourceRequest.jobUniqueIdentifier, it.first))
            }

        if (nodeWithGPUs != null) {
            return nodeWithGPUs
        }

        // Rule 2: if no free space and not within budget. then its a no-op
        if (provisionResourceRequest.allDevicePossibilities.all {
                gpuConsumingJobRepo.sumConsumedResourcesByTeam(
                    provisionResourceRequest.teamName,
                    it.deviceType
                ) + it.amount > gpuResourcesPerTeamRepo.find(
                    provisionResourceRequest.teamName, it.deviceType
                ).resources
            }) {
            throw NoAvailableBudgetException()
        } else {
            // Rule 3: run linear optimization
            return reshuffleToFit(provisionResourceRequest)
        }
    }

    private fun reshuffleToFit(provisionResourceRequest: ProvisionResourceRequest): List<JobAction> {
        return provisionResourceRequest.allDevicePossibilities.firstNotNullOfOrNull {
            methodToRename(it, provisionResourceRequest)
        } ?: throw IllegalStateException(
            "Unable to place job even though the team has budget." +
                    " This is most likely a result of the total sum of all team budgets exceeding the total capacity or bad fragmentation"
        )
    }

    private fun methodToRename(
        it: DeviceRequirements,
        provisionResourceRequest: ProvisionResourceRequest
    ): List<JobAction>? {
        val teamsOverBudget =
            gpuResourcesPerTeamRepo.findTeamsOverusingResources(it.deviceType).map { it.teamName }.toSet()
        val allJobs = gpuConsumingJobRepo.findByNodeWithGPUsDeviceType(it.deviceType).map {
            JobForSolver(
                JobUniqueIdentifier(it.jobName, it.gpuResourcesPerTeam.teamName),
                it.consumedResources,
                teamsOverBudget.contains(it.gpuResourcesPerTeam.teamName) && !it.priority, it.nodeWithGPUs.name
            )
        } + JobForSolver(
            provisionResourceRequest.jobUniqueIdentifier,
            it.amount, false
        )
        val nodes = nodeWithGPURepo.findAll()
        val reshuffleToFit = optimalNodePacker.reshuffleToFit(allJobs, nodes)
        if (reshuffleToFit != null) {
            log.info(
                "Unable to place job even though the team has budget for ${it.deviceType}." +
                        " This is most likely a result of the total sum of all team budgets exceeding the total capacity or bad fragmentation"
            )

        }
        return reshuffleToFit
    }

}
