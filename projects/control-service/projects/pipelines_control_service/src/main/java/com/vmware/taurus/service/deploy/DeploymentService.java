/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.deploy;

import com.vmware.taurus.controlplane.model.data.DataJobDeployment;
import com.vmware.taurus.exception.ErrorMessage;
import com.vmware.taurus.exception.KubernetesException;
import com.vmware.taurus.service.JobsRepository;
import com.vmware.taurus.service.diag.OperationContext;
import com.vmware.taurus.service.diag.methodintercept.Measurable;
import com.vmware.taurus.service.model.*;
import com.vmware.taurus.service.notification.NotificationContent;
import io.kubernetes.client.ApiException;
import lombok.RequiredArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;

import java.util.Collections;
import java.util.List;
import java.util.Objects;
import java.util.Optional;

/**
 * CRUD operations for Versatile Data Kit deployments on kubernetes.
 *
 * This class is in a transition from operating against Kubernetes to operating against the database.
 * Currently, only the enabled flag is stored in the database. Eventually, all deployment information
 * will be stored (and retrieved) from a database from a dedicated table.
 */
@Service
@RequiredArgsConstructor
public class DeploymentService {
   private static final Logger log = LoggerFactory.getLogger(DeploymentService.class);

   private final DockerRegistryService dockerRegistryService;
   private final DeploymentProgress deploymentProgress;
   private final JobImageBuilder jobImageBuilder;
   private final JobImageDeployer jobImageDeployer;
   private final OperationContext operationContext;
   private final JobsRepository jobsRepository;

   public Optional<JobDeploymentStatus> readDeployment(String jobName) {
      return jobImageDeployer.readScheduledJob(jobName);
   }

   public List<JobDeploymentStatus> readDeployments() {
      return jobImageDeployer.readScheduledJobs();
   }

   /**
    * Enables/Disables a {@link DataJob}.
    * When disabled, the DataJob will still be deployed but it will never be executed.
    * When enabled, the DataJob will be executed according to its {@link JobConfig#getSchedule()}
    */
   public void enableDeployment(DataJob dataJob, JobDeployment jobDeployment,
                                boolean enable, String lastDeployedBy) throws ApiException {
      if (jobDeployment.getEnabled() != enable) {
         jobDeployment.setEnabled(enable);
         jobImageDeployer.scheduleJob(dataJob, jobDeployment, false, lastDeployedBy);

         saveDeployment(dataJob, jobDeployment);
      }
      deploymentProgress.configuration_updated(dataJob.getJobConfig(), jobDeployment, Collections.singletonMap("enabled", enable));
   }

   /**
    * Deploys data jobs on kubernetes as cron jobs.
    * Creates a new deployment if none is present for the data job.
    * Updates an existing deployment if it already exists.
    * This method is will be executed in a separate thread.
    *
    * @param dataJob The data job
    * @param jobDeployment Deployment configuration
    * @param sendNotification
    * @param lastDeployedBy name of the user that last updated the data job
    * @param opId Operation ID of the client request
    * @see org.springframework.scheduling.annotation.Async
    */
   @Async
   @Measurable(includeArg = 0, argName = "data_job")
   public void updateDeployment(DataJob dataJob, JobDeployment jobDeployment,
                                Boolean sendNotification, String lastDeployedBy, String opId) {
      // TODO: Consider introducing a generalised mechanism to propagate Operation Context properties to all ASYNC calls.
      // Add the opId value propagated from the operation context to a thread's local operation context.
      operationContext.setId(opId);

      try {
         log.info("Starting deployment of job {}", jobDeployment.getDataJobName());
         deploymentProgress.started(dataJob.getJobConfig(), jobDeployment);
         String imageName = dockerRegistryService.dataJobImage(
                 jobDeployment.getDataJobName(), jobDeployment.getGitCommitSha());

         if (jobImageBuilder.buildImage(imageName, dataJob, jobDeployment, sendNotification)) {
            log.info("Image {} has been built. Will now schedule job {} for execution", imageName, dataJob.getName());
            jobDeployment.setImageName(imageName);
            if (jobImageDeployer.scheduleJob(dataJob, jobDeployment, sendNotification, lastDeployedBy)) {
               log.info(String.format("Successfully updated job: %s with version: %s",
                       jobDeployment.getDataJobName(), jobDeployment.getGitCommitSha()));

               saveDeployment(dataJob, jobDeployment);

               deploymentProgress.completed(dataJob.getJobConfig(), jobDeployment, sendNotification);
            }
         }
      } catch (ApiException e) {
         handleException(dataJob, jobDeployment, sendNotification, new KubernetesException("", e));
      } catch (Exception e) {
         handleException(dataJob, jobDeployment, sendNotification, e);
      } catch (Throwable e) {
         handleException(dataJob, jobDeployment, sendNotification, e);
         throw e;
      }
   }

   private void saveDeployment(DataJob dataJob, JobDeployment jobDeployment) {
      // Currently, store only 'enabled' in the database
      if (!Objects.equals(dataJob.getEnabled(), jobDeployment.getEnabled())) {
         dataJob.setEnabled(jobDeployment.getEnabled());
         jobsRepository.save(dataJob);
         log.info("The deployment of the data job {} has been {}",
                 dataJob.getName(), Boolean.TRUE.equals(dataJob.getEnabled()) ? "ENABLED" : "DISABLED");
      }
   }

   private void handleException(DataJob dataJob, JobDeployment jobDeployment, Boolean sendNotification, Throwable e) {
      ErrorMessage message = new ErrorMessage(
              String.format("An error occurred while trying to deploy job: %s with version: %s",
                      jobDeployment.getDataJobName(), jobDeployment.getGitCommitSha()),
              "See exception message below for possible reason.",
              "Most likely the deployment has failed." +
                      " It is possible that deployment may have succeeded (or failed with User error)" +
                      " but there was communication issue." +
                      " Since we do not know we assume that it was platform error and SRE team need to investigate." +
                      " End user deploying the job would get notification for deploy failure due to platform error",
              "End user may verify which version is currently deployed and re-try if necessary. " +
                      "SRE team may investigate by looking at the logs or in kubernetes."
      );
      log.error(message.toString(), e);
      deploymentProgress.failed(dataJob.getJobConfig(), jobDeployment, DeploymentStatus.PLATFORM_ERROR,
              NotificationContent.getPlatformErrorBody(), sendNotification);
   }

   public void deleteDeployment(String dataJobName)  {
      if (this.deploymentExistsOrInProgress(dataJobName)) {
         jobImageBuilder.cancelBuildingJob(dataJobName);
         jobImageDeployer.unScheduleJob(dataJobName);
         jobsRepository.updateDataJobEnabledByName(dataJobName, false);
      }
      deploymentProgress.deleted(dataJobName);
   }

   private boolean deploymentExistsOrInProgress(String dataJobName)  {
      return jobImageBuilder.isBuildingJobInProgress(dataJobName) || readDeployment(dataJobName).isPresent();
   }

}
