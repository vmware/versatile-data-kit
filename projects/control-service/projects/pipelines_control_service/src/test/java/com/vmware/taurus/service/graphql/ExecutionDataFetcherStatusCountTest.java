/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.graphql;

import com.vmware.taurus.service.JobExecutionRepository;
import com.vmware.taurus.service.execution.JobExecutionLogsUrlBuilder;
import com.vmware.taurus.service.execution.JobExecutionService;
import com.vmware.taurus.service.graphql.model.V2DataJob;
import com.vmware.taurus.service.graphql.model.V2DataJobDeployment;
import com.vmware.taurus.service.graphql.strategy.datajob.JobFieldStrategyBy;
import com.vmware.taurus.service.model.ExecutionStatus;
import graphql.schema.DataFetchingEnvironment;
import graphql.schema.DataFetchingFieldSelectionSet;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.lenient;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
public class ExecutionDataFetcherStatusCountTest {

  ExecutionDataFetcher executionDataFetcher;

  @Mock DataFetchingEnvironment dataFetchingEnvironment;

  @Mock DataFetchingFieldSelectionSet dataFetchingFieldSelectionSet;

  @Mock JobExecutionService jobExecutionService;

  @Mock JobExecutionRepository jobExecutionRepository;

  @Mock JobExecutionLogsUrlBuilder jobExecutionLogsUrlBuilder;

  @BeforeEach
  public void init() {
    executionDataFetcher =
        new ExecutionDataFetcher(
            jobExecutionRepository, jobExecutionService, jobExecutionLogsUrlBuilder);
  }

  @Test
  void testDataFetcherStatusCount_emptyExecutions() {
    when(dataFetchingEnvironment.getSelectionSet()).thenReturn(dataFetchingFieldSelectionSet);
    lenient()
        .when(
            dataFetchingFieldSelectionSet.contains(
                JobFieldStrategyBy.DEPLOYMENT_SUCCESSFUL_EXECUTIONS.getPath()))
        .thenReturn(true);
    lenient()
        .when(
            dataFetchingFieldSelectionSet.contains(
                JobFieldStrategyBy.DEPLOYMENT_FAILED_EXECUTIONS.getPath()))
        .thenReturn(true);
    when(jobExecutionService.countExecutionStatuses(any(), any())).thenReturn(Map.of());
    var testJob = new V2DataJob();
    var deployment = new V2DataJobDeployment();

    testJob.setJobName("test-job");
    testJob.setDeployments(List.of(deployment));

    var result =
        executionDataFetcher.populateStatusCounts(List.of(testJob), dataFetchingEnvironment);
    assertEquals(0, result.get(0).getDeployments().get(0).getSuccessfulExecutions());
    assertEquals(0, result.get(0).getDeployments().get(0).getFailedExecutions());
  }

  @Test
  void testDataFetcherStatusCount_twoFailedExecutions() {
    when(dataFetchingEnvironment.getSelectionSet()).thenReturn(dataFetchingFieldSelectionSet);
    lenient()
        .when(
            dataFetchingFieldSelectionSet.contains(
                JobFieldStrategyBy.DEPLOYMENT_FAILED_EXECUTIONS.getPath()))
        .thenReturn(true);
    when(jobExecutionService.countExecutionStatuses(any(), any()))
        .thenReturn(Map.of("test-job", Map.of(ExecutionStatus.PLATFORM_ERROR, 2)));
    var testJob = new V2DataJob();
    var deployment = new V2DataJobDeployment();

    testJob.setJobName("test-job");
    testJob.setDeployments(List.of(deployment));

    var result =
        executionDataFetcher.populateStatusCounts(List.of(testJob), dataFetchingEnvironment);
    assertEquals(2, result.get(0).getDeployments().get(0).getFailedExecutions());
  }

  @Test
  void testDataFetcherStatusCount_twoSuccessfulExecutions() {
    when(dataFetchingEnvironment.getSelectionSet()).thenReturn(dataFetchingFieldSelectionSet);
    lenient()
        .when(
            dataFetchingFieldSelectionSet.contains(
                JobFieldStrategyBy.DEPLOYMENT_SUCCESSFUL_EXECUTIONS.getPath()))
        .thenReturn(true);
    when(jobExecutionService.countExecutionStatuses(any(), any()))
        .thenReturn(Map.of("test-job", Map.of(ExecutionStatus.SUCCEEDED, 2)));
    var testJob = new V2DataJob();
    var deployment = new V2DataJobDeployment();

    testJob.setJobName("test-job");
    testJob.setDeployments(List.of(deployment));

    var result =
        executionDataFetcher.populateStatusCounts(List.of(testJob), dataFetchingEnvironment);
    assertEquals(2, result.get(0).getDeployments().get(0).getSuccessfulExecutions());
  }
}
