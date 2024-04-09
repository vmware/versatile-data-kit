package com.vmware.gpu.management.api


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

class NoAvailableBudgetException: Exception("Team has no budget available to deploy a job")
