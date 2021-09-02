/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs;

import com.vmware.taurus.service.model.JobDeployment;
import com.vmware.taurus.service.model.JobDeploymentStatus;
import lombok.AllArgsConstructor;
import org.springframework.stereotype.Service;

@Service
@AllArgsConstructor
public class DeploymentStatusToDeploymentConverter {
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
}
