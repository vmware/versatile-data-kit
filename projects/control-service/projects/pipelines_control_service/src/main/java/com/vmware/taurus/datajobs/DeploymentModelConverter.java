/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs;

import com.vmware.taurus.controlplane.model.data.DataJobResources;
import com.vmware.taurus.service.model.DataJobDeploymentResources;
import com.vmware.taurus.service.model.DesiredDataJobDeployment;
import com.vmware.taurus.service.model.JobDeployment;
import com.vmware.taurus.service.model.JobDeploymentStatus;
import com.vmware.taurus.service.model.ActualDataJobDeployment;
import lombok.AllArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.OffsetDateTime;

/** Utility functions that convert between different model or DTO classes */
@Service
@AllArgsConstructor
public class DeploymentModelConverter {

  public static JobDeployment toJobDeployment(
      String teamName, String jobName, JobDeploymentStatus jobDeploymentStatus) {
    JobDeployment deployment = new JobDeployment();
    deployment.setDataJobTeam(teamName);
    deployment.setDataJobName(jobName);
    deployment.setCronJobName(jobDeploymentStatus.getCronJobName());
    deployment.setImageName(jobDeploymentStatus.getImageName());
    deployment.setEnabled(jobDeploymentStatus.getEnabled());
    deployment.setResources(jobDeploymentStatus.getResources());
    deployment.setMode(jobDeploymentStatus.getMode());
    deployment.setGitCommitSha(jobDeploymentStatus.getGitCommitSha());
    deployment.setVdkVersion(jobDeploymentStatus.getVdkVersion());
    deployment.setPythonVersion(jobDeploymentStatus.getPythonVersion());

    return deployment;
  }

  public static DesiredDataJobDeployment toDesiredDataJobDeployment(JobDeployment jobDeploymentStatus) {
    DesiredDataJobDeployment deployment = new DesiredDataJobDeployment();
    deployment.setDataJobName(jobDeploymentStatus.getDataJobName());
    deployment.setEnabled(jobDeploymentStatus.getEnabled());

    DataJobResources dataJobResources = jobDeploymentStatus.getResources();

    if (dataJobResources != null) {
      DataJobDeploymentResources deploymentResources = toDataJooDeploymentResources(
              dataJobResources.getCpuRequest(),
              dataJobResources.getCpuLimit(),
              dataJobResources.getMemoryRequest(),
              dataJobResources.getMemoryLimit());

      deployment.setResources(deploymentResources);
    }

    deployment.setGitCommitSha(jobDeploymentStatus.getGitCommitSha());
    deployment.setPythonVersion(jobDeploymentStatus.getPythonVersion());

    return deployment;
  }

  public static ActualDataJobDeployment toActualJobDeployment(DesiredDataJobDeployment desiredDataJobDeployment, String deploymentVersionSha, OffsetDateTime lastDeployedDate) {
    ActualDataJobDeployment deployment = new ActualDataJobDeployment();
    deployment.setDataJobName(desiredDataJobDeployment.getDataJobName());
    deployment.setDataJob(desiredDataJobDeployment.getDataJob());
    deployment.setEnabled(desiredDataJobDeployment.getEnabled());

    DataJobDeploymentResources desiredDataJobDeploymentResources = desiredDataJobDeployment.getResources();

    if (desiredDataJobDeploymentResources != null) {
      DataJobDeploymentResources deploymentResources = toDataJooDeploymentResources(
              desiredDataJobDeploymentResources.getCpuRequestCores(),
              desiredDataJobDeploymentResources.getCpuLimitCores(),
              desiredDataJobDeploymentResources.getMemoryRequestMi(),
              desiredDataJobDeploymentResources.getMemoryLimitMi());

      deployment.setResources(deploymentResources);
    }

    deployment.setGitCommitSha(desiredDataJobDeployment.getGitCommitSha());
    deployment.setPythonVersion(desiredDataJobDeployment.getPythonVersion());
    deployment.setSchedule(desiredDataJobDeployment.getSchedule());
    deployment.setDeploymentVersionSha(deploymentVersionSha);

    deployment.setLastDeployedDate(lastDeployedDate);
    deployment.setLastDeployedBy(desiredDataJobDeployment.getLastDeployedBy());

    return deployment;
  }

  /**
   * Merge two deployments with preference of fields from newDeployment over oldDeployment.
   *
   * @param oldDeployment the old deployment
   * @param newDeployment the new deployment if a field is not null it is set other oldDeployment
   *     field is used.
   * @return the merge deployment
   */
  public static JobDeployment mergeDeployments(
      JobDeployment oldDeployment, JobDeployment newDeployment) {
    JobDeployment mergedDeployment = new JobDeployment();
    if (!newDeployment.getDataJobName().equals(oldDeployment.getDataJobName())
        || !newDeployment.getDataJobTeam().equals(oldDeployment.getDataJobTeam())) {
      throw new IllegalArgumentException(
          "Cannot merge 2 deployments if team or job name is different."
              + oldDeployment
              + " vs "
              + newDeployment);
    }
    mergedDeployment.setDataJobTeam(newDeployment.getDataJobTeam());
    mergedDeployment.setDataJobName(newDeployment.getDataJobName());
    mergedDeployment.setCronJobName(
        newDeployment.getCronJobName() != null
            ? newDeployment.getCronJobName()
            : oldDeployment.getCronJobName());
    mergedDeployment.setImageName(
        newDeployment.getImageName() != null
            ? newDeployment.getImageName()
            : oldDeployment.getImageName());
    mergedDeployment.setEnabled(
        newDeployment.getEnabled() != null
            ? newDeployment.getEnabled()
            : oldDeployment.getEnabled());

    var mergedResources = new DataJobResources();
    var newResources = newDeployment.getResources();
    var oldResources = oldDeployment.getResources();
    if (newResources != null && oldResources != null) {
      mergedResources.setCpuLimit(
          newResources.getCpuLimit() != null
              ? newResources.getCpuLimit()
              : oldResources.getCpuLimit());
      mergedResources.setCpuRequest(
          newResources.getCpuRequest() != null
              ? newResources.getCpuRequest()
              : oldResources.getCpuRequest());
      mergedResources.setMemoryLimit(
          newResources.getMemoryLimit() != null
              ? newResources.getMemoryLimit()
              : oldResources.getMemoryLimit());
      mergedResources.setMemoryRequest(
          newResources.getMemoryRequest() != null
              ? newResources.getMemoryRequest()
              : oldResources.getMemoryRequest());
    } else {
      mergedResources = newResources != null ? newResources : oldResources;
    }
    mergedDeployment.setResources(mergedResources);

    mergedDeployment.setMode(
        newDeployment.getMode() != null ? newDeployment.getMode() : oldDeployment.getMode());
    mergedDeployment.setGitCommitSha(
        newDeployment.getGitCommitSha() != null
            ? newDeployment.getGitCommitSha()
            : oldDeployment.getGitCommitSha());
    mergedDeployment.setVdkVersion(
        newDeployment.getVdkVersion() != null
            ? newDeployment.getVdkVersion()
            : oldDeployment.getVdkVersion());
    mergedDeployment.setPythonVersion(
        newDeployment.getPythonVersion() != null
            ? newDeployment.getPythonVersion()
            : oldDeployment.getPythonVersion());

    return mergedDeployment;
  }

  private static DataJobDeploymentResources toDataJooDeploymentResources(Float cpuRequestCores, Float cpuLimitCores, Integer memoryRequestMi, Integer memoryLimitMi) {
      DataJobDeploymentResources deploymentResources = new DataJobDeploymentResources();
      deploymentResources.setCpuRequestCores(cpuRequestCores);
      deploymentResources.setCpuLimitCores(cpuLimitCores);
      deploymentResources.setMemoryRequestMi(memoryRequestMi);
      deploymentResources.setMemoryLimitMi(memoryLimitMi);

      return deploymentResources;
  }
}
