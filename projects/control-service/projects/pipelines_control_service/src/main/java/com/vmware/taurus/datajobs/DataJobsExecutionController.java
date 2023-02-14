/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs;

import com.vmware.taurus.controlplane.model.api.DataJobsExecutionApi;
import com.vmware.taurus.controlplane.model.data.DataJobExecution;
import com.vmware.taurus.controlplane.model.data.DataJobExecutionLogs;
import com.vmware.taurus.controlplane.model.data.DataJobExecutionRequest;
import com.vmware.taurus.service.JobsService;
import com.vmware.taurus.service.execution.JobExecutionService;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.servlet.support.ServletUriComponentsBuilder;
import org.springframework.web.util.UriBuilder;

import java.net.URI;
import java.util.List;
import java.util.function.Supplier;

/**
 * REST controller for operations on data jobs for Execution API. POC of Execution API is
 * implemented.
 *
 * <p>
 *
 * @see DataJobsController
 */
@RestController
@RequiredArgsConstructor
@Tag(name = "Data Jobs Execution")
public class DataJobsExecutionController implements DataJobsExecutionApi {

  private final JobsService jobsService;

  private final JobExecutionService executionService;

  private final Supplier<UriBuilder> currentContextPathBuilderSupplier =
      ServletUriComponentsBuilder::fromCurrentContextPath;

  @Override
  public ResponseEntity<List<DataJobExecution>> dataJobDeploymentExecutionList(
      String teamName, String jobName, String deploymentId, List<String> executionStatus) {
    // TODO: add support for deployment ID
    return dataJobExecutionList(teamName, jobName, executionStatus);
  }

  @Override
  public ResponseEntity<List<DataJobExecution>> dataJobExecutionList(
      String teamName, String jobName, List<String> executionStatus) {

    List<DataJobExecution> executions =
        executionService.listJobExecutions(teamName, jobName, executionStatus);
    return ResponseEntity.ok(executions);
  }

  @Override
  public ResponseEntity<DataJobExecution> dataJobExecutionRead(
      String teamName, String jobName, String executionId) {
    DataJobExecution dataJobExecution =
        executionService.readJobExecution(teamName, jobName, executionId);
    return ResponseEntity.ok(dataJobExecution);
  }

  @Override
  public ResponseEntity<Void> dataJobExecutionCancel(
      String teamName, String jobName, String executionId) {
    executionService.cancelDataJobExecution(teamName, jobName, executionId);
    return ResponseEntity.ok().build();
  }

  @Override
  public ResponseEntity<Void> dataJobExecutionStart(
      String teamName,
      String jobName,
      String deploymentId,
      DataJobExecutionRequest jobExecutionRequest) {

    String executionId =
        executionService.startDataJobExecution(
            teamName, jobName, deploymentId, jobExecutionRequest);
    String contextPath =
        String.format(
            "/data-jobs/for-team/%s/jobs/%s/executions/%s", teamName, jobName, executionId);
    URI location = currentContextPathBuilderSupplier.get().path(contextPath).build();

    return ResponseEntity.accepted().location(location).build();
  }

  @Override
  public ResponseEntity<DataJobExecutionLogs> dataJobLogsDownload(
      String teamName, String jobName, String executionId, Integer tailLines) {
    DataJobExecutionLogs logs =
        executionService.getJobExecutionLogs(teamName, jobName, executionId, tailLines);
    return ResponseEntity.ok(logs);
  }
}
