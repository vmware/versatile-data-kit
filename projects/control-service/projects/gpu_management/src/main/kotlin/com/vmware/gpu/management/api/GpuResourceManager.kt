package com.vmware.gpu.management.api

interface GpuResourceManager {
    fun jobEnded(jobUniqueIdentifier: JobUniqueIdentifier)

    fun markJobPriority(jobUniqueIdentifier: JobUniqueIdentifier, priority: Boolean)
    fun tryProvisionResources(jobUniqueIdentifier: JobUniqueIdentifier, amount: Float): List<JobAction>
}


data class JobUniqueIdentifier(val jobName: String,val teamName: String){
    val uniqueID = this.teamName + "____" + this.jobName
}
sealed interface JobAction
data class CreateJob(val nodeName: String, val jobUniqueIdentifier: JobUniqueIdentifier, val amount: Float) :
    JobAction {
    constructor(nodeName: String, provisionResourceRequest: ProvisionResourceRequest) :
            this(
                nodeName,
                provisionResourceRequest.jobUniqueIdentifier,
                provisionResourceRequest.amount
            )
}
data class MoveJob(val nodeName: String, val jobUniqueIdentifier: JobUniqueIdentifier, val amount: Float) : JobAction
data class DeleteJob(val jobUniqueIdentifier: JobUniqueIdentifier) : JobAction {
    val uId = jobUniqueIdentifier.uniqueID
}

data class ProvisionResourceRequest(val jobUniqueIdentifier: JobUniqueIdentifier, val amount: Float){
    val teamName = jobUniqueIdentifier.teamName
}

