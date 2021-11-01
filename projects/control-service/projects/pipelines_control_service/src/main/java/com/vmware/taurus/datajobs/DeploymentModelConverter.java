/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs;

import com.vmware.taurus.controlplane.model.data.DataJobResources;
import com.vmware.taurus.service.model.JobDeployment;
import com.vmware.taurus.service.model.JobDeploymentStatus;
import lombok.AllArgsConstructor;
import org.springframework.stereotype.Service;

/**
 * Utility functions that convert between different model or DTO classes
 */
@Service
@AllArgsConstructor
public class DeploymentModelConverter {

    public static JobDeployment toJobDeployment(JobDeploymentStatus jobDeploymentStatus) {
        JobDeployment deployment = new JobDeployment();
        deployment.setDataJobName(jobDeploymentStatus.getDataJobName());
        deployment.setCronJobName(jobDeploymentStatus.getCronJobName());
        deployment.setImageName(jobDeploymentStatus.getImageName());
        deployment.setEnabled(jobDeploymentStatus.getEnabled());
        deployment.setResources(jobDeploymentStatus.getResources());
        deployment.setMode(jobDeploymentStatus.getMode());
        deployment.setGitCommitSha(jobDeploymentStatus.getGitCommitSha());

        return deployment;
    }

    /**
     * Merge to deployments with preference of fields from newDeployment over oldDeployment.
     * @param oldDeployment the old deployment
     * @param newDeployment the new deployment if a field is not null it is set other oldDeployment field is used.
     * @return the merge deployment
     */
    public static JobDeployment mergeDeployments(JobDeployment oldDeployment, JobDeployment newDeployment) {
        JobDeployment mergedDeployment = new JobDeployment();
        mergedDeployment.setDataJobName(oldDeployment.getDataJobName());
        mergedDeployment.setCronJobName(newDeployment.getCronJobName() != null ? newDeployment.getCronJobName() : oldDeployment.getCronJobName());
        mergedDeployment.setImageName(newDeployment.getImageName() != null ? newDeployment.getImageName() : oldDeployment.getImageName());
        mergedDeployment.setEnabled(newDeployment.getEnabled() != null ? newDeployment.getEnabled() : oldDeployment.getEnabled());

        var mergedResources = new DataJobResources();
        var newResources = newDeployment.getResources();
        var oldResources = oldDeployment.getResources();
        if (newResources != null && oldResources != null) {
            mergedResources.setCpuLimit(newResources.getCpuLimit() != null ? newResources.getCpuLimit() : oldResources.getCpuLimit());
            mergedResources.setCpuRequest(newResources.getCpuRequest() != null ? newResources.getCpuRequest() : oldResources.getCpuRequest());
            mergedResources.setMemoryLimit(newResources.getMemoryLimit() != null ? newResources.getMemoryLimit() : oldResources.getMemoryLimit());
            mergedResources.setMemoryRequest(newResources.getMemoryRequest() != null ? newResources.getMemoryRequest() : oldResources.getMemoryRequest());
        } else {
            mergedResources = newResources != null ? newResources : oldResources;
        }
        mergedDeployment.setResources(mergedResources);

        mergedDeployment.setMode(newDeployment.getMode() != null ? newDeployment.getMode() : oldDeployment.getMode());
        mergedDeployment.setGitCommitSha(newDeployment.getGitCommitSha() != null ? newDeployment.getGitCommitSha() : oldDeployment.getGitCommitSha());
        return mergedDeployment;
    }
}
