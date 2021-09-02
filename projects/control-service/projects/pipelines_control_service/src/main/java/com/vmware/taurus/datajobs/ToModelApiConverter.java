/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs;

import com.vmware.taurus.controlplane.model.data.DataJobConfig;
import com.vmware.taurus.controlplane.model.data.DataJobDeployment;
import com.vmware.taurus.controlplane.model.data.DataJobExecution;
import com.vmware.taurus.service.model.*;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;

@Slf4j
public class ToModelApiConverter {

   public static JobDeployment toJobDeployment(String jobName, DataJobDeployment dataJobDeployment) {

      JobDeployment jobDeployment = new JobDeployment();
      jobDeployment.setDataJobName(jobName);
      jobDeployment.setEnabled(dataJobDeployment.getEnabled());
      jobDeployment.setResources(dataJobDeployment.getResources());
      jobDeployment.setMode(dataJobDeployment.getMode().toString());
      jobDeployment.setGitCommitSha(dataJobDeployment.getJobVersion());

      return jobDeployment;
   }

   public static DataJob toDataJob(com.vmware.taurus.controlplane.model.data.DataJob modelJob) {
      JobConfig config = new JobConfig();
      config.setJobName(modelJob.getJobName());
      config.setDescription(modelJob.getDescription());
      config.setTeam(modelJob.getTeam());
      DataJobConfig modelConfig = modelJob.getConfig();
      if (modelConfig != null) {
         config.setDbDefaultType(modelConfig.getDbDefaultType());

         if (modelConfig.getSchedule() != null) {
            config.setSchedule(modelConfig.getSchedule().getScheduleCron());
         }
         config.setEnableExecutionNotifications(modelConfig.getEnableExecutionNotifications());
         config.setNotificationDelayPeriodMinutes(modelConfig.getNotificationDelayPeriodMinutes());
         var contacts = modelConfig.getContacts();
         if (contacts != null) {
            config.setNotifiedOnJobSuccess(contacts.getNotifiedOnJobSuccess());
            config.setNotifiedOnJobDeploy(contacts.getNotifiedOnJobDeploy());
            config.setNotifiedOnJobFailurePlatformError(contacts.getNotifiedOnJobFailurePlatformError());
            config.setNotifiedOnJobFailureUserError(contacts.getNotifiedOnJobFailureUserError());
         }
         config.setGenerateKeytab(modelConfig.getGenerateKeytab());
      }
      return new DataJob(modelJob.getJobName(), config);
   }

   public static ExecutionType toExecutionType(DataJobExecution.TypeEnum type) {
      switch (type) {
         case MANUAL:
            return ExecutionType.MANUAL;
         case SCHEDULED:
            return ExecutionType.SCHEDULED;
         default: // no such type
            log.warn("Unexpected type: '" + type + "' in ExecutionType.");
            return null;
      }
   }

   public static ExecutionStatus toExecutionStatus(DataJobExecution.StatusEnum status) {
      switch (status) {
         case SUBMITTED:
            return ExecutionStatus.SUBMITTED;
         case RUNNING:
            return ExecutionStatus.RUNNING;
         case FAILED:
            return ExecutionStatus.FAILED;
         case CANCELLED:
            return ExecutionStatus.CANCELLED;
         case FINISHED:
            return ExecutionStatus.FINISHED;
         case SKIPPED:
            return ExecutionStatus.SKIPPED;
         default: // No such status
            log.warn("Unexpected status: '" + status + "' in ExecutionStatus.");
            return null;
      }
   }
}
