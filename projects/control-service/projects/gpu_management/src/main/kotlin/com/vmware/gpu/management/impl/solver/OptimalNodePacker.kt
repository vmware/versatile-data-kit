package com.vmware.gpu.management.impl.solver

import com.google.ortools.linearsolver.MPSolver
import com.google.ortools.linearsolver.MPVariable
import com.vmware.gpu.management.api.*
import com.vmware.gpu.management.jpa.NodeWithGPUs
import org.slf4j.Logger
import org.slf4j.LoggerFactory
import org.springframework.beans.factory.annotation.Value
import org.springframework.stereotype.Component

data class JobForSolver(
    val jobUniqueIdentifier: JobUniqueIdentifier,
    val consumedResources: Float,
    val jobIsEligibleFoDeletion: Boolean,
    val nodeItCurrentlyLivesOn: String? = null
) {
    val teamName = jobUniqueIdentifier.teamName
    val jobName = jobUniqueIdentifier.jobName
}

data class NodeForSolver(
    val reshuffleData: List<JobAndAssociatedVariable>,
    val totalDevices: Int,
    val nodeName: String
)

data class JobAndAssociatedVariable(val variable: MPVariable, val job: JobForSolver)



@Component
class OptimalNodePacker(@Value("\${gpu.management.job_portability:0.7}")val jobPortability: Double) {


    fun reshuffleToFit(
        allJobs: List<JobForSolver>,
        nodes: List<NodeWithGPUs>
    ): List<JobAction>? {

        val solver = MPSolver(
            "NodeReshuffle",
            MPSolver.OptimizationProblemType.CBC_MIXED_INTEGER_PROGRAMMING
        )
        val x = nodes.map { n ->
            NodeForSolver(
                allJobs.map { j ->
                    JobAndAssociatedVariable(solver.makeBoolVar(j.teamName + "____" + j.jobName + "____" + n.name),
                            j)
                }, n.deviceCount, n.name
            )
        }

        // Constraint 1:
        // Each item can only be in one node at most.
        (0 until x[0].reshuffleData.size)
            .filter { x[0].reshuffleData[it].job.jobIsEligibleFoDeletion }
            .forEach { j -> solver.createConstraint(x.map { it.reshuffleData[j].variable * 1.0f }.mustBeLessThanOrEqual(1.0f)) }


        // Constraint 2:
        // If a team is under budget or a job is marked as high priority then we need to ensure it is running after the re shuffle
        (0 until x[0].reshuffleData.size)
            .filterNot { x[0].reshuffleData[it].job.jobIsEligibleFoDeletion }
            .forEach { j -> solver.createConstraint(x.map { it.reshuffleData[j].variable * 1.0f }.mustBeExactly(1.0f)) }

        // Constraint 3:
        // We can't exceed the amount of resources on a single machine
        x.forEach { j ->
            solver.createConstraint(j.reshuffleData.map {
                it.variable * it.job.consumedResources
            }.mustBeLessThanOrEqual(j.totalDevices.toFloat()))
        }

        // maximize the amount of jobs we run, while also trying to minimize the amount of jobs we move
        val resultStatus = solver.maximize(
            x.flatMap { a ->
                a.reshuffleData.map {
                    it.variable * if (a.nodeName == it.job.nodeItCurrentlyLivesOn) 1.0 else jobPortability
                }
            })

        if (resultStatus === MPSolver.ResultStatus.OPTIMAL || resultStatus === MPSolver.ResultStatus.FEASIBLE) {
            val deleteJobs = x.flatMap { n ->
                n.reshuffleData.filter { it.variable.isDisabled() && it.job.nodeItCurrentlyLivesOn == n.nodeName }
                    .map { DeleteJob(it.job.jobUniqueIdentifier) }
            }
            val createJobs = x.flatMap { n ->
                n.reshuffleData.filter { it.variable.isEnabled() && it.job.nodeItCurrentlyLivesOn != n.nodeName }
                    .map { CreateJob(n.nodeName, it.job.jobUniqueIdentifier, it.job.consumedResources) }
            }
            val moveJob =
                createJobs.filter { cj -> deleteJobs.any { cj.jobUniqueIdentifier == it.jobUniqueIdentifier } }
                    .map { MoveJob(it.nodeName, it.jobUniqueIdentifier, it.amount) }
            return deleteJobs.filterNot {
                moveJob.map(MoveJob::jobUniqueIdentifier).contains(it.jobUniqueIdentifier)
            } + moveJob + createJobs.filterNot {
                moveJob.map(MoveJob::jobUniqueIdentifier).contains(it.jobUniqueIdentifier)
            }
        } else {
            return null
        }
    }
}
