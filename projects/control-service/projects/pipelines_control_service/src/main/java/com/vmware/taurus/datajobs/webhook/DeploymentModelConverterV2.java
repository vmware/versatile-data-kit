/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs.webhook;

import com.vmware.taurus.service.model.DataJobDeployment;
import com.vmware.taurus.service.model.JobDeployment;
import lombok.AllArgsConstructor;
import org.springframework.stereotype.Service;

/**
 * Utility functions that convert between different model or DTO classes
 */
@Service
@AllArgsConstructor
public class DeploymentModelConverterV2 {

  public static DataJobDeployment toJobDeployment(String userDeployer, JobDeployment jobDeployment) {
    var newDeployment = new DataJobDeployment();
    newDeployment.setDataJobName(jobDeployment.getDataJobName());
    newDeployment.setPythonVersion(jobDeployment.getPythonVersion());
    newDeployment.setGitCommitSha(jobDeployment.getGitCommitSha());

    if(jobDeployment.getResources() != null) {
      newDeployment.setResourcesCpuRequest(jobDeployment.getResources().getCpuRequest());
      newDeployment.setResourcesCpuLimit(jobDeployment.getResources().getCpuLimit());
      newDeployment.setResourcesMemoryRequest(jobDeployment.getResources().getMemoryRequest());
      newDeployment.setResourcesMemoryLimit(jobDeployment.getResources().getMemoryLimit());
    }

    newDeployment.setLastDeployedBy(userDeployer);
    newDeployment.setEnabled(jobDeployment.getEnabled());

    return newDeployment;
  }

  public static DataJobDeployment mergeDeployments(DataJobDeployment oldDeployment,
      JobDeployment newDeployment) {
    if (!oldDeployment.getDataJobName().equals(newDeployment.getDataJobName())
        || !oldDeployment.getDataJob().getJobConfig().getTeam()
        .equals(newDeployment.getDataJobTeam())) {
      throw new IllegalArgumentException(
          "Cannot merge 2 deployments if team or job name is different."
              + oldDeployment
              + " vs "
              + newDeployment);
    }

    DataJobDeployment mergedDeployment = new DataJobDeployment();

    mergedDeployment.setDataJobName(newDeployment.getDataJobName());
    mergedDeployment.setDataJob(oldDeployment.getDataJob());

    mergedDeployment.setDeploymentVersionSha(
        oldDeployment.getDeploymentVersionSha()); // not present in newDeployment entity
    mergedDeployment.setGitCommitSha((newDeployment.getGitCommitSha() != null ?
        newDeployment.getGitCommitSha() : oldDeployment.getGitCommitSha()));
    mergedDeployment.setPythonVersion(
        newDeployment.getPythonVersion() != null ? newDeployment.getPythonVersion()
            : oldDeployment.getPythonVersion());

    if (newDeployment.getResources() != null) {
      mergedDeployment.setResourcesCpuRequest(
          newDeployment.getResources().getCpuRequest() != null ? newDeployment.getResources()
              .getCpuRequest() : oldDeployment.getResourcesCpuRequest());
      mergedDeployment.setResourcesCpuLimit(
          newDeployment.getResources().getCpuLimit() != null ? newDeployment.getResources()
              .getCpuLimit() : oldDeployment.getResourcesCpuLimit());
      mergedDeployment.setResourcesMemoryRequest(
          newDeployment.getResources().getMemoryRequest() != null ? newDeployment.getResources()
              .getMemoryRequest() : oldDeployment.getResourcesMemoryRequest());
      mergedDeployment.setResourcesMemoryLimit(
          newDeployment.getResources().getMemoryLimit() != null ? newDeployment.getResources()
              .getMemoryLimit() : oldDeployment.getResourcesMemoryLimit());
    }

    mergedDeployment.setLastDeployedBy(
        oldDeployment.getLastDeployedBy()); // not present in newDeployment entity
    mergedDeployment.setLastDeployedDate(
        oldDeployment.getLastDeployedDate()); // not present in newDeployment entity

    mergedDeployment.setEnabled(newDeployment.getEnabled() != null ? newDeployment.getEnabled()
        : oldDeployment.getEnabled());

    return mergedDeployment;
  }
}
