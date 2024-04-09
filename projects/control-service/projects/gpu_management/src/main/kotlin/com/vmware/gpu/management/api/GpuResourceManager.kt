package com.vmware.gpu.management.api



interface GpuResourceManager {

    fun jobEnded(jobUniqueIdentifier: JobUniqueIdentifier)
    fun markJobPriority(jobUniqueIdentifier: JobUniqueIdentifier, priority: Boolean)
    fun tryProvisionResources(jobUniqueIdentifier: JobUniqueIdentifier, amount: Float): List<JobAction>
}

