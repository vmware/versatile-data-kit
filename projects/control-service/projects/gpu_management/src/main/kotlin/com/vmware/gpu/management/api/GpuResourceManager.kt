package com.vmware.gpu.management.api


/**
 * Responsible for managing GPU resources most efficiently.
 */
interface GpuResourceManager {
    /**
     * Marks the completion of a job, releasing its resources.
     */
    fun jobEnded(jobUniqueIdentifier: JobUniqueIdentifier)
    /**
     * Marks a job's priority status. High priority jobs will never be killed in order to accommodate other jobs.
     * But it is subject to restarts during a reshuffle
     */
    fun markJobPriority(jobUniqueIdentifier: JobUniqueIdentifier, priority: Boolean)
    /**
     * Checks if a job can be deployed.
     * @throws NoAvailableBudgetException if the team trying to deploy a job doesn't have resources to deploy the job and there is no where on the cluster to run it
     * @return a list of actions that need to be complete to run the requested job
     *          This might involve deleting some jobs which belong to over budget teams and moving jobs to other machines to more effectively pack
     */
    @Throws(NoAvailableBudgetException::class)
    fun tryProvisionResources(jobUniqueIdentifier: JobUniqueIdentifier, deviceRequirements: DeviceRequirements): List<JobAction>
}
