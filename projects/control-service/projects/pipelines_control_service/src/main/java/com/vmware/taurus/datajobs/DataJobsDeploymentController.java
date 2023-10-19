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
import com.vmware.taurus.service.deploy.DataJobDeploymentPropertiesConfig;
import com.vmware.taurus.service.deploy.DataJobDeploymentPropertiesConfig.ReadFrom;
import com.vmware.taurus.service.deploy.DataJobDeploymentPropertiesConfig.WriteTo;
import com.vmware.taurus.service.deploy.DeploymentService;
import com.vmware.taurus.service.deploy.DeploymentServiceV2;
import com.vmware.taurus.service.diag.OperationContext;
import com.vmware.taurus.service.model.JobDeploymentStatus;
import io.swagger.v3.oas.annotations.tags.Tag;
import java.util.Collections;
import java.util.List;
import java.util.Optional;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.RestController;

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

  @Autowired private DeploymentServiceV2 deploymentServiceV2;

  @Autowired private DataJobDeploymentPropertiesConfig dataJobDeploymentPropertiesConfig;

  @Override
  public ResponseEntity<Void> deploymentDelete(
      String teamName, String jobName, String deploymentId) {
    if (jobsService.jobWithTeamExists(jobName, teamName)) {
      // TODO: deploymentId not implemented
      if (jobName != null) {
        if (dataJobDeploymentPropertiesConfig.getWriteTos().contains(WriteTo.K8S)) {
          deploymentService.deleteDeployment(jobName);
        }

        if (dataJobDeploymentPropertiesConfig.getWriteTos().contains(WriteTo.DB)) {
          deploymentServiceV2.deleteDesiredDeployment(jobName);
        }

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

        if (dataJobDeploymentPropertiesConfig.getWriteTos().contains(WriteTo.K8S)) {
          deploymentService.patchDeployment(job.get(), jobDeployment);
        }

        if (dataJobDeploymentPropertiesConfig.getWriteTos().contains(WriteTo.DB)) {
          deploymentServiceV2.patchDesiredDbDeployment(
              job.get(), jobDeployment, operationContext.getUser());
        }

        return ResponseEntity.accepted().build();
      }
    }
    return ResponseEntity.notFound().build();
  }

  @Override
  public ResponseEntity<List<DataJobDeploymentStatus>> deploymentList(
      String teamName, String jobName, String deploymentId, DataJobMode dataJobMode) {
    // TODO: deploymentId and mode not implemented
    if (jobsService.jobWithTeamExists(jobName, teamName)) {
      var responseOptional = getDeploymentStatusOptional(jobName.toLowerCase());
      if (!responseOptional.isPresent()) {
        return ResponseEntity.of(Optional.of(Collections.emptyList()));
      }
      return ResponseEntity.ok(List.of(responseOptional.get()));
    }
    return ResponseEntity.notFound().build();
  }

  private Optional<DataJobDeploymentStatus> getDeploymentStatusOptional(String jobName) {
    Optional<DataJobDeploymentStatus> jobDeploymentStatus = Optional.empty();
    if (dataJobDeploymentPropertiesConfig.getReadDataSource().equals(ReadFrom.DB)) {
      jobDeploymentStatus = readFromDB(jobName);
    } else if (dataJobDeploymentPropertiesConfig.getReadDataSource().equals(ReadFrom.K8S)) {
      jobDeploymentStatus = readFromK8S(jobName);
    }
    return jobDeploymentStatus;
  }

  @Override
  public ResponseEntity<DataJobDeploymentStatus> deploymentRead(
      String teamName, String jobName, String deploymentId) {
    if (jobsService.jobWithTeamExists(jobName, teamName)) {
      Optional<DataJobDeploymentStatus> jobDeploymentOptional = getDeploymentStatusOptional(
          jobName);
      if (jobDeploymentOptional.isPresent()) {
        return ResponseEntity.ok(jobDeploymentOptional.get());
      }
    }
    return ResponseEntity.notFound().build();
  }

  private Optional<DataJobDeploymentStatus> readFromK8S(String jobName) {
    Optional<JobDeploymentStatus> jobDeploymentStatus = deploymentService.readDeployment(jobName.toLowerCase());
    if (jobDeploymentStatus.isPresent()) {
      return Optional.of(
          ToApiModelConverter.toDataJobDeploymentStatus(jobDeploymentStatus.get()));
    }
    return Optional.empty();
  }

  private Optional<DataJobDeploymentStatus> readFromDB(String dataJobName) {
    var jobDeploymentOptional = deploymentServiceV2.readDeployment(dataJobName.toLowerCase());
    var jobOptional = jobsService.getByName(dataJobName);
    if (jobDeploymentOptional.isPresent()) {
      var deploymentResponse =
          DeploymentModelConverter.toJobDeploymentStatus(
              jobDeploymentOptional.get(), jobOptional.get());
      return Optional.of(deploymentResponse);
    }
    return Optional.empty();
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

        if (dataJobDeploymentPropertiesConfig.getWriteTos().contains(WriteTo.K8S)) {
          // TODO: Consider using a Task-oriented API approach
          deploymentService.updateDeployment(
              job.get(),
              jobDeployment,
              sendNotification,
              operationContext.getUser(),
              operationContext.getOpId());
        }

        if (dataJobDeploymentPropertiesConfig.getWriteTos().contains(WriteTo.DB)) {
          deploymentServiceV2.updateDesiredDbDeployment(
              job.get(), jobDeployment, operationContext.getUser());
        }

        return ResponseEntity.accepted().build();
      }
    }
    return ResponseEntity.notFound().build();
  }

  private void validateJobResources(DataJobDeployment dataJobDeployment) {
    if (dataJobDeployment != null
        && dataJobDeployment.getResources() != null
        && (dataJobDeployment.getResources().getCpuRequest() != null
            || dataJobDeployment.getResources().getCpuLimit() != null
            || dataJobDeployment.getResources().getMemoryRequest() != null
                && dataJobDeployment.getResources().getMemoryLimit() != null)) {
      throw new ValidationException(
          "The setting of job resources like CPU and memory is not allowed.",
          "The setting of job resources like CPU and memory is not supported by the platform.",
          "The deployment of the data job will not proceed.",
          "To deploy the data job, please do not configure job resources.");
    }
  }
}
