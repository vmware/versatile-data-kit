/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.graphql;

import com.google.common.collect.Lists;
import com.vmware.taurus.controlplane.model.data.DataJobMode;
import com.vmware.taurus.service.JobExecutionRepository;
import com.vmware.taurus.service.execution.JobExecutionLogsUrlBuilder;
import com.vmware.taurus.service.execution.JobExecutionService;
import com.vmware.taurus.service.graphql.model.DataJobExecutionFilter;
import com.vmware.taurus.service.graphql.model.DataJobExecutionOrder;
import com.vmware.taurus.service.graphql.model.V2DataJob;
import com.vmware.taurus.service.graphql.model.V2DataJobConfig;
import com.vmware.taurus.service.graphql.model.V2DataJobDeployment;
import com.vmware.taurus.service.graphql.model.V2DataJobSchedule;
import com.vmware.taurus.service.graphql.strategy.datajob.JobFieldStrategyBy;
import com.vmware.taurus.service.model.DataJobExecution;
import graphql.GraphQLException;
import graphql.schema.DataFetchingEnvironment;
import graphql.schema.DataFetchingFieldSelectionSet;
import graphql.schema.SelectedField;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.data.jpa.domain.Specification;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class ExecutionDataFetcherTest {

  private ExecutionDataFetcher executionDataFetcher;
  @Mock private JobExecutionRepository jobExecutionRepository;
  @Mock private DataFetchingEnvironment dataFetchingEnvironment;
  @Mock private DataFetchingFieldSelectionSet dataFetchingFieldSelectionSet;
  @Mock private SelectedField selectedField;
  @Mock private JobExecutionService jobExecutionService;
  @Mock private JobExecutionLogsUrlBuilder jobExecutionLogsUrlBuilder;

  @BeforeEach
  public void init() {
    executionDataFetcher =
        new ExecutionDataFetcher(
            jobExecutionRepository, jobExecutionService, jobExecutionLogsUrlBuilder);
  }

  @Test
  void testDataFetcherOfJobs_whenInvalidExecutionPageNumberIsProvided_shouldThrowException() {
    when(dataFetchingEnvironment.getSelectionSet()).thenReturn(dataFetchingFieldSelectionSet);
    when(dataFetchingFieldSelectionSet.getFields(
            JobFieldStrategyBy.DEPLOYMENT_EXECUTIONS.getPath()))
        .thenReturn(Lists.newArrayList(selectedField));
    Map<String, Object> executionArgs = new HashMap<>();
    executionArgs.put("pageNumber", 0);
    executionArgs.put("pageSize", 25);
    when(selectedField.getArguments()).thenReturn(executionArgs);
    List<V2DataJob> v2DataJobs = mockListOfV2DataJobs();

    assertThrows(
        GraphQLException.class,
        () -> executionDataFetcher.populateExecutions(v2DataJobs, dataFetchingEnvironment));
  }

  @Test
  void testDataFetcherOfJobs_whenInvalidExecutionPageSizeIsProvided_shouldThrowException() {
    when(dataFetchingEnvironment.getSelectionSet()).thenReturn(dataFetchingFieldSelectionSet);
    when(dataFetchingFieldSelectionSet.getFields(
            JobFieldStrategyBy.DEPLOYMENT_EXECUTIONS.getPath()))
        .thenReturn(Lists.newArrayList(selectedField));
    Map<String, Object> executionArgs = new HashMap<>();
    executionArgs.put("pageNumber", 1);
    executionArgs.put("pageSize", 0);
    when(selectedField.getArguments()).thenReturn(executionArgs);
    List<V2DataJob> v2DataJobs = mockListOfV2DataJobs();

    assertThrows(
        GraphQLException.class,
        () -> executionDataFetcher.populateExecutions(v2DataJobs, dataFetchingEnvironment));
  }

  @Test
  void testDataFetcherOfJobs_whenRequestIncludesExecutions_shouldInvokeExecutions() {
    when(dataFetchingEnvironment.getSelectionSet()).thenReturn(dataFetchingFieldSelectionSet);
    when(dataFetchingFieldSelectionSet.getFields(
            JobFieldStrategyBy.DEPLOYMENT_EXECUTIONS.getPath()))
        .thenReturn(Lists.newArrayList(selectedField));
    Map<String, Object> executionArgs = new HashMap<>();
    executionArgs.put("pageNumber", 1);
    executionArgs.put("pageSize", 25);
    when(selectedField.getArguments()).thenReturn(executionArgs);
    List<V2DataJob> v2DataJobs = mockListOfV2DataJobs();
    when(jobExecutionRepository.findAll(any(Specification.class), any(Pageable.class)))
        .thenReturn(new PageImpl<DataJobExecution>(Collections.emptyList()));

    List<V2DataJob> result =
        executionDataFetcher.populateExecutions(v2DataJobs, dataFetchingEnvironment);

    assertEquals(3, result.size());
    verify(jobExecutionRepository, times(2)).findAll(any(Specification.class), any(Pageable.class));
  }

  @Test
  void testDataFetcherOfJobs_whenUnsupportedOrderInExecutionOperation_shouldThrowException() {
    when(dataFetchingEnvironment.getSelectionSet()).thenReturn(dataFetchingFieldSelectionSet);
    when(dataFetchingFieldSelectionSet.getFields(
            JobFieldStrategyBy.DEPLOYMENT_EXECUTIONS.getPath()))
        .thenReturn(Lists.newArrayList(selectedField));
    Map<String, Object> executionArgs = new HashMap<>();
    executionArgs.put("pageNumber", 1);
    executionArgs.put("pageSize", 25);

    executionArgs.put(
        "order",
        Map.of(
            DataJobExecutionOrder.PROPERTY_FIELD,
            UUID.randomUUID().toString(),
            DataJobExecutionOrder.DIRECTION_FIELD,
            Sort.Direction.ASC));
    when(selectedField.getArguments()).thenReturn(executionArgs);
    List<V2DataJob> v2DataJobs = mockListOfV2DataJobs();

    assertThrows(
        GraphQLException.class,
        () -> executionDataFetcher.populateExecutions(v2DataJobs, dataFetchingEnvironment));
  }

  @Test
  void testDataFetcherOfJobs_whenJobNameInIsSpecified_shouldThrowException() {
    when(dataFetchingEnvironment.getSelectionSet()).thenReturn(dataFetchingFieldSelectionSet);
    when(dataFetchingFieldSelectionSet.getFields(
            JobFieldStrategyBy.DEPLOYMENT_EXECUTIONS.getPath()))
        .thenReturn(Lists.newArrayList(selectedField));
    Map<String, Object> executionArgs = new HashMap<>();
    executionArgs.put("pageNumber", 1);
    executionArgs.put("pageSize", 25);
    executionArgs.put(
        "filter", Map.of(DataJobExecutionFilter.JOB_NAME_IN_FIELD, List.of("any-job")));
    when(selectedField.getArguments()).thenReturn(executionArgs);
    List<V2DataJob> v2DataJobs = mockListOfV2DataJobs();

    assertThrows(
        GraphQLException.class,
        () -> executionDataFetcher.populateExecutions(v2DataJobs, dataFetchingEnvironment));
  }

  static List<V2DataJob> mockListOfV2DataJobs() {
    List<V2DataJob> dataJobs = new ArrayList<>();

    dataJobs.add(mockSampleDataJob("sample-job-1", "Import SQL", true));
    dataJobs.add(mockSampleDataJob("sample-job-2", "Dump SQL", true));
    dataJobs.add(mockSampleDataJob("sample-job-3", "Delete users", false));

    return dataJobs;
  }

  static V2DataJob mockSampleDataJob(
      String jobName, String description, boolean includeDeployment) {
    V2DataJob dataJob = new V2DataJob();
    V2DataJobConfig jobConfig = new V2DataJobConfig();
    jobConfig.setSchedule(new V2DataJobSchedule());
    jobConfig.setDescription(description);
    dataJob.setConfig(jobConfig);
    if (includeDeployment) {
      dataJob.setDeployments(Collections.singletonList(mockSampleDeployment(jobName)));
    }
    dataJob.setJobName(jobName);

    return dataJob;
  }

  static V2DataJobDeployment mockSampleDeployment(String jobName) {
    V2DataJobDeployment status = new V2DataJobDeployment();
    status.setEnabled(true);
    status.setId(jobName + "-latest");
    status.setMode(DataJobMode.RELEASE);
    return status;
  }
}
