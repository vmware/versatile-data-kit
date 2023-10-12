/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs;

import com.vmware.taurus.controlplane.model.api.DataJobsDeploymentApi;
import com.vmware.taurus.controlplane.model.data.DataJobDeployment;
import com.vmware.taurus.controlplane.model.data.DataJobDeploymentStatus;
import com.vmware.taurus.controlplane.model.data.DataJobMode;
import com.vmware.taurus.exception.ExternalSystemError;
import com.vmware.taurus.exception.ValidationException;
import com.vmware.taurus.service.JobsService;
import com.vmware.taurus.service.deploy.DeploymentService;
import com.vmware.taurus.service.diag.OperationContext;
import com.vmware.taurus.service.model.JobDeploymentStatus;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.RestController;

import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Optional;

/**
 * REST controller for operations on data job deployments
 *
 * <p>The controller may throw exception which will be handled by {@link
 * com.vmware.taurus.exception.ExceptionControllerAdvice}. The advice class logs error so no need to
 * log them here.
 *
 * <p>Wrap {@link org.springframework.dao.DataAccessException} from JobsService in {@link
 * ExternalSystemError} either here or in the service itself.
 */
@RestController
@AllArgsConstructor
@NoArgsConstructor
@Tag(name = "Data Jobs Deployment")
public class DataJobsDeploymentController implements DataJobsDeploymentApi {
  static Logger log = LoggerFactory.getLogger(DataJobsDeploymentController.class);

  @Autowired private JobsService jobsService;

  @Autowired private DeploymentService deploymentService;

  @Autowired private OperationContext operationContext;

  @Override
  public ResponseEntity<Void> deploymentDelete(
      String teamName, String jobName, String deploymentId) {
    if (jobsService.jobWithTeamExists(jobName, teamName)) {
      // TODO: deploymentId not implemented
      if (jobName != null) {
        deploymentService.deleteDeployment(jobName);
        return ResponseEntity.accepted().build();
      }
      return ResponseEntity.notFound().build();
    }
    return ResponseEntity.notFound().build();
  }

  @Override
  public ResponseEntity<Void> deploymentPatch(
      String teamName, String jobName, String deploymentId, DataJobDeployment dataJobDeployment) {
    deploymentService.validatePythonVersionIsSupported(dataJobDeployment.getPythonVersion());
    validateJobResources(dataJobDeployment);
    if (jobsService.jobWithTeamExists(jobName, teamName)) {
      // TODO: deploymentId not implemented
      Optional<com.vmware.taurus.service.model.DataJob> job = jobsService.getByName(jobName);

      if (job.isPresent()) {
        var jobDeployment =
            ToModelApiConverter.toJobDeployment(teamName, jobName, dataJobDeployment);
        deploymentService.patchDeployment(job.get(), jobDeployment);
        return ResponseEntity.accepted().build();
      }
    }
    return ResponseEntity.notFound().build();
  }

  @Override
  public ResponseEntity<List<DataJobDeploymentStatus>> deploymentList(
      String teamName, String jobName, String deploymentId, DataJobMode dataJobMode) {
    if (jobsService.jobWithTeamExists(jobName, teamName)) {
      // TODO: deploymentId and mode not implemented
      List<DataJobDeploymentStatus> deployments = Collections.emptyList();
      Optional<JobDeploymentStatus> jobDeploymentStatus =
          deploymentService.readDeployment(jobName.toLowerCase());
      if (jobDeploymentStatus.isPresent()) {
        deployments =
            Arrays.asList(ToApiModelConverter.toDataJobDeploymentStatus(jobDeploymentStatus.get()));
      }
      return ResponseEntity.ok(deployments);
    }
    return ResponseEntity.notFound().build();
  }

  @Override
  public ResponseEntity<DataJobDeploymentStatus> deploymentRead(
      String teamName, String jobName, String deploymentId) {
    if (jobsService.jobWithTeamExists(jobName, teamName)) {
      // TODO: deploymentId are not implemented.
      Optional<JobDeploymentStatus> jobDeploymentStatus =
          deploymentService.readDeployment(jobName.toLowerCase());
      if (jobDeploymentStatus.isPresent()) {
        return ResponseEntity.ok(
            ToApiModelConverter.toDataJobDeploymentStatus(jobDeploymentStatus.get()));
      }
    }
    return ResponseEntity.notFound().build();
  }

  @Override
  public ResponseEntity<Void> deploymentUpdate(
      String teamName,
      String jobName,
      Boolean sendNotification,
      DataJobDeployment dataJobDeployment) {
    deploymentService.validatePythonVersionIsSupported(dataJobDeployment.getPythonVersion());
    validateJobResources(dataJobDeployment);
    if (jobsService.jobWithTeamExists(jobName, teamName)) {
      Optional<com.vmware.taurus.service.model.DataJob> job =
          jobsService.getByName(jobName.toLowerCase());
      if (job.isPresent()) {
        var jobDeployment =
            ToModelApiConverter.toJobDeployment(teamName, jobName.toLowerCase(), dataJobDeployment);
        // TODO: Consider using a Task-oriented API approach
        deploymentService.updateDeployment(
            job.get(),
            jobDeployment,
            sendNotification,
            operationContext.getUser(),
            operationContext.getOpId());

        return ResponseEntity.accepted().build();
      }
    }
    return ResponseEntity.notFound().build();
  }

  private void validateJobResources(DataJobDeployment dataJobDeployment) {
    if (dataJobDeployment != null && dataJobDeployment.getResources() != null &&
            (dataJobDeployment.getResources().getCpuRequest() != null ||
                    dataJobDeployment.getResources().getCpuLimit() != null ||
                    dataJobDeployment.getResources().getMemoryRequest() != null &&
                            dataJobDeployment.getResources().getMemoryLimit() != null)) {
      throw new ValidationException(
                "The setting of job resources like CPU and memory is not allowed.",
                "The setting of job resources like CPU and memory is not supported by the platform.",
                "The deployment of the data job will not proceed.",
                "To deploy the data job, please do not configure job resources.");
    }
  }
}
