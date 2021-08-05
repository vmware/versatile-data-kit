/*
 * Copyright (c) 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs;


import com.vmware.taurus.controlplane.model.api.DataJobsExecutionApi;
import com.vmware.taurus.controlplane.model.data.DataJobExecution;
import com.vmware.taurus.controlplane.model.data.DataJobExecutionRequest;
import com.vmware.taurus.service.JobsService;
import com.vmware.taurus.service.execution.JobExecutionService;
import io.swagger.annotations.Api;
import lombok.RequiredArgsConstructor;
import org.apache.commons.lang3.NotImplementedException;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.servlet.support.ServletUriComponentsBuilder;
import org.springframework.web.util.UriBuilder;

import java.net.URI;
import java.util.List;
import java.util.function.Supplier;


/**
 * REST controller for operations on data jobs for Execution API.
 * POC of Execution API is implemented.
 *
 * <p>
 *
 * @see DataJobsController
 */
@RestController
@RequiredArgsConstructor
@Api(tags = {"Data Jobs Execution"})
public class DataJobsExecutionController implements DataJobsExecutionApi {

   private final JobsService jobsService;

   private final JobExecutionService executionService;

   private final Supplier<UriBuilder> currentContextPathBuilderSupplier = ServletUriComponentsBuilder::fromCurrentContextPath;

   @Override
   @Deprecated
   public ResponseEntity<List<DataJobExecution>> dataJobDeploymentExecutionListDeprecated(final String teamName,
                                                                                          final String jobName,
                                                                                          final String deploymentId,
                                                                                          final List<String> executionStatus) {
      return dataJobDeploymentExecutionList(teamName, jobName, deploymentId, executionStatus);
   }

   @Override
   @Deprecated
   public ResponseEntity<Void> dataJobExecutionCancelDeprecated(final String teamName,
                                                                final String jobName,
                                                                final String executionId) {
      return dataJobExecutionCancel(teamName, jobName, executionId);
   }

   @Override
   @Deprecated
   public ResponseEntity<List<DataJobExecution>> dataJobExecutionListDeprecated(final String teamName,
                                                                                final String jobName,
                                                                                final List<String> executionStatus) {
      return dataJobExecutionList(teamName, jobName, executionStatus);
   }

   @Override
   @Deprecated
   public ResponseEntity<DataJobExecution> dataJobExecutionReadDeprecated(final String teamName,
                                                                          final String jobName,
                                                                          final String executionId) {
      return dataJobExecutionRead(teamName, jobName, executionId);
   }

   @Override
   @Deprecated
   public ResponseEntity<Void> dataJobExecutionStartDeprecated(final String teamName,
                                                               final String jobName,
                                                               final String deploymentId,
                                                               final DataJobExecutionRequest jobExecutionRequest) {
      return dataJobExecutionStart(teamName, jobName, deploymentId, jobExecutionRequest);
   }

   @Override
   public ResponseEntity<List<DataJobExecution>> dataJobDeploymentExecutionList(
         String teamName,
         String jobName,
         String deploymentId,
         List<String> executionStatus) {
      // TODO: add support for deployment ID
      return dataJobExecutionList(teamName, jobName, executionStatus);
   }

   @Override
   public ResponseEntity<List<DataJobExecution>> dataJobExecutionList(
         String teamName,
         String jobName,
         List<String> executionStatus) {

      List<DataJobExecution> executions = executionService.listJobExecutions(teamName, jobName, executionStatus);
      return ResponseEntity.ok(executions);
   }

   @Override
   public ResponseEntity<DataJobExecution> dataJobExecutionRead(String teamName, String jobName, String executionId) {
      DataJobExecution dataJobExecution = executionService.readJobExecution(teamName, jobName, executionId);
      return ResponseEntity.ok(dataJobExecution);
   }

   @Override
   public ResponseEntity<Void> dataJobExecutionCancel(String teamName, String jobName, String executionId) {
      throw new NotImplementedException("Cancel is not implemented");
   }

   @Override
   public ResponseEntity<Void> dataJobExecutionStart(
         String teamName,
         String jobName,
         String deploymentId,
         DataJobExecutionRequest jobExecutionRequest) {

      String executionId = executionService.startDataJobExecution(teamName, jobName, deploymentId, jobExecutionRequest);
      String contextPath = String.format(
            "/data-jobs/for-team/%s/jobs/%s/executions/%s",
            teamName, jobName, executionId);
      URI location = currentContextPathBuilderSupplier.get().path(contextPath).build();

      return ResponseEntity.accepted().location(location).build();
   }
}
