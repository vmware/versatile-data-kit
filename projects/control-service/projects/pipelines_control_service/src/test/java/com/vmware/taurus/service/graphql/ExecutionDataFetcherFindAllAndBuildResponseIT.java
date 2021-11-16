/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.graphql;

import static com.vmware.taurus.service.graphql.model.DataJobExecutionQueryVariables.FILTER_FIELD;
import static com.vmware.taurus.service.graphql.model.DataJobExecutionQueryVariables.ORDER_FIELD;
import static com.vmware.taurus.service.graphql.model.DataJobExecutionQueryVariables.PAGE_NUMBER_FIELD;
import static com.vmware.taurus.service.graphql.model.DataJobExecutionQueryVariables.PAGE_SIZE_FIELD;
import static org.mockito.Mockito.when;

import java.time.OffsetDateTime;
import java.util.List;
import java.util.Map;

import graphql.GraphQLException;
import graphql.schema.DataFetcher;
import graphql.schema.DataFetchingEnvironment;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mock;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.RepositoryUtil;
import com.vmware.taurus.service.JobExecutionRepository;
import com.vmware.taurus.service.JobsRepository;
import com.vmware.taurus.service.graphql.model.DataJobExecutionFilter;
import com.vmware.taurus.service.graphql.model.DataJobExecutionOrder;
import com.vmware.taurus.service.graphql.model.DataJobPage;
import com.vmware.taurus.service.model.DataJob;
import com.vmware.taurus.service.model.DataJobExecution;
import com.vmware.taurus.service.model.ExecutionStatus;

@SpringBootTest(classes = ControlplaneApplication.class)
public class ExecutionDataFetcherFindAllAndBuildResponseIT {

   @Autowired
   private JobsRepository jobsRepository;

   @Autowired
   private JobExecutionRepository jobExecutionRepository;

   @Autowired
   private ExecutionDataFetcher executionDataFetcher;

   @Mock
   private DataFetchingEnvironment dataFetchingEnvironment;

   @Mock
   private Map<String, Object> filterRaw;

   @Mock
   private Map<String, Object> orderRaw;

   @BeforeEach
   public void setUp() throws Exception {
      jobsRepository.deleteAll();
   }

   @Test
   public void testFindAllAndBuildResponse_withoutFilters_shouldReturnResult() throws Exception {
      DataJob actualDataJob = RepositoryUtil.createDataJob(jobsRepository);

      RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-1", actualDataJob, ExecutionStatus.CANCELLED);
      RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-2", actualDataJob, ExecutionStatus.RUNNING);
      RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-3", actualDataJob, ExecutionStatus.SUBMITTED);
      RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-4", actualDataJob, ExecutionStatus.FAILED);

      when(dataFetchingEnvironment.getArgument(FILTER_FIELD)).thenReturn(null);
      when(dataFetchingEnvironment.getArgument(ORDER_FIELD)).thenReturn(null);

      DataFetcher<Object> allAndBuildResponse = executionDataFetcher.findAllAndBuildResponse();
      DataJobPage response = (DataJobPage)allAndBuildResponse.get(dataFetchingEnvironment);
      List<Object> actualJobExecutions = response.getContent();

      Assertions.assertNotNull(actualJobExecutions);
      Assertions.assertEquals(4, actualJobExecutions.size());
   }

   @Test
   public void testFindAllAndBuildResponse_filerByStatusIn_shouldReturnResult() throws Exception {
      DataJob actualDataJob = RepositoryUtil.createDataJob(jobsRepository);

      RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-1", actualDataJob, ExecutionStatus.CANCELLED);
      DataJobExecution expectedJobExecution1 =
            RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-2", actualDataJob, ExecutionStatus.RUNNING);
      DataJobExecution expectedJobExecution2 =
            RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-3", actualDataJob, ExecutionStatus.SUBMITTED);
      RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-4", actualDataJob, ExecutionStatus.FAILED);

      when(filterRaw.get(DataJobExecutionFilter.STATUS_IN_FIELD)).thenReturn(List.of(
            com.vmware.taurus.controlplane.model.data.DataJobExecution.StatusEnum.RUNNING.toString(),
            com.vmware.taurus.controlplane.model.data.DataJobExecution.StatusEnum.SUBMITTED.toString()));
      when(dataFetchingEnvironment.getArgument(FILTER_FIELD)).thenReturn(filterRaw);
      when(dataFetchingEnvironment.getArgument(ORDER_FIELD)).thenReturn(null);

      DataFetcher<Object> allAndBuildResponse = executionDataFetcher.findAllAndBuildResponse();
      DataJobPage response = (DataJobPage)allAndBuildResponse.get(dataFetchingEnvironment);
      List<Object> actualJobExecutions = response.getContent();

      Assertions.assertNotNull(actualJobExecutions);
      Assertions.assertEquals(2, actualJobExecutions.size());

      assertExecutionsEquals(expectedJobExecution1, actualJobExecutions.get(0));
      assertExecutionsEquals(expectedJobExecution2, actualJobExecutions.get(1));
   }

   @Test
   public void testFindAllAndBuildResponse_filerByStartTimeGte_shouldReturnResult() throws Exception {
      DataJob actualDataJob = RepositoryUtil.createDataJob(jobsRepository);
      OffsetDateTime now = OffsetDateTime.now();

      RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-1", actualDataJob, ExecutionStatus.CANCELLED, now.minusMinutes(2));
      DataJobExecution expectedJobExecution1 =
            RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-2", actualDataJob, ExecutionStatus.RUNNING, now.minusMinutes(1));
      DataJobExecution expectedJobExecution2 =
            RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-3", actualDataJob, ExecutionStatus.SUBMITTED, now.minusMinutes(1));
      RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-4", actualDataJob, ExecutionStatus.FAILED, now.minusMinutes(2));

      when(filterRaw.get(DataJobExecutionFilter.START_TIME_GTE_FIELD)).thenReturn(now.minusMinutes(1));
      when(dataFetchingEnvironment.getArgument(FILTER_FIELD)).thenReturn(filterRaw);
      when(dataFetchingEnvironment.getArgument(ORDER_FIELD)).thenReturn(null);

      DataFetcher<Object> allAndBuildResponse = executionDataFetcher.findAllAndBuildResponse();
      DataJobPage response = (DataJobPage)allAndBuildResponse.get(dataFetchingEnvironment);
      List<Object> actualJobExecutions = response.getContent();

      Assertions.assertNotNull(actualJobExecutions);
      Assertions.assertEquals(2, actualJobExecutions.size());

      assertExecutionsEquals(expectedJobExecution1, actualJobExecutions.get(0));
      assertExecutionsEquals(expectedJobExecution2, actualJobExecutions.get(1));
   }

   @Test
   public void testFindAllAndBuildResponse_filerByEndTimeGte_shouldReturnResult() throws Exception {
      DataJob actualDataJob = RepositoryUtil.createDataJob(jobsRepository);
      OffsetDateTime now = OffsetDateTime.now();

      RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-1", actualDataJob, ExecutionStatus.CANCELLED, now.minusMinutes(2), now.minusMinutes(2));
      DataJobExecution expectedJobExecution1 =
            RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-2", actualDataJob, ExecutionStatus.RUNNING, now.minusMinutes(1), now.minusMinutes(1));
      DataJobExecution expectedJobExecution2 =
            RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-3", actualDataJob, ExecutionStatus.SUBMITTED, now.minusMinutes(1), now.minusMinutes(1));
      RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-4", actualDataJob, ExecutionStatus.FAILED, now.minusMinutes(2), now.minusMinutes(2));

      when(filterRaw.get(DataJobExecutionFilter.END_TIME_GTE_FIELD)).thenReturn(now.minusMinutes(1));
      when(dataFetchingEnvironment.getArgument(FILTER_FIELD)).thenReturn(filterRaw);
      when(dataFetchingEnvironment.getArgument(ORDER_FIELD)).thenReturn(null);

      DataFetcher<Object> allAndBuildResponse = executionDataFetcher.findAllAndBuildResponse();
      DataJobPage response = (DataJobPage)allAndBuildResponse.get(dataFetchingEnvironment);
      List<Object> actualJobExecutions = response.getContent();

      Assertions.assertNotNull(actualJobExecutions);
      Assertions.assertEquals(2, actualJobExecutions.size());

      assertExecutionsEquals(expectedJobExecution1, actualJobExecutions.get(0));
      assertExecutionsEquals(expectedJobExecution2, actualJobExecutions.get(1));
   }

   @Test
   public void testFindAllAndBuildResponse_filerByAllFields_shouldReturnResult() throws Exception {
      DataJob actualDataJob = RepositoryUtil.createDataJob(jobsRepository);
      OffsetDateTime now = OffsetDateTime.now();

      RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-1", actualDataJob, ExecutionStatus.CANCELLED, now.minusMinutes(2), now.minusMinutes(2));
      DataJobExecution expectedJobExecution1 =
            RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-2", actualDataJob, ExecutionStatus.RUNNING, now.minusMinutes(1), now.minusMinutes(1));
      RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-3", actualDataJob, ExecutionStatus.SUBMITTED, now.minusMinutes(1), now.minusMinutes(1));
      RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-4", actualDataJob, ExecutionStatus.FAILED, now.minusMinutes(2), now.minusMinutes(2));

      when(filterRaw.get(DataJobExecutionFilter.START_TIME_GTE_FIELD)).thenReturn(now.minusMinutes(1));
      when(filterRaw.get(DataJobExecutionFilter.END_TIME_GTE_FIELD)).thenReturn(now.minusMinutes(1));
      when(filterRaw.get(DataJobExecutionFilter.STATUS_IN_FIELD)).thenReturn(List.of(
            com.vmware.taurus.controlplane.model.data.DataJobExecution.StatusEnum.RUNNING.toString()));

      when(dataFetchingEnvironment.getArgument(FILTER_FIELD)).thenReturn(filterRaw);
      when(dataFetchingEnvironment.getArgument(ORDER_FIELD)).thenReturn(null);

      DataFetcher<Object> allAndBuildResponse = executionDataFetcher.findAllAndBuildResponse();
      DataJobPage response = (DataJobPage)allAndBuildResponse.get(dataFetchingEnvironment);
      List<Object> actualJobExecutions = response.getContent();

      Assertions.assertNotNull(actualJobExecutions);
      Assertions.assertEquals(1, actualJobExecutions.size());

      assertExecutionsEquals(expectedJobExecution1, actualJobExecutions.get(0));
   }

   @Test
   public void testFindAllAndBuildResponse_orderByEndTime_shouldReturnResult() throws Exception {
      DataJob actualDataJob = RepositoryUtil.createDataJob(jobsRepository);

      DataJobExecution expectedJobExecution1 =
            RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-1", actualDataJob, ExecutionStatus.CANCELLED);
      DataJobExecution expectedJobExecution2 =
            RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-2", actualDataJob, ExecutionStatus.RUNNING);
      DataJobExecution expectedJobExecution3 =
            RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-3", actualDataJob, ExecutionStatus.SUBMITTED);
      DataJobExecution expectedJobExecution4 =
            RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-4", actualDataJob, ExecutionStatus.FAILED);

      when(dataFetchingEnvironment.getArgument(FILTER_FIELD)).thenReturn(null);

      when(orderRaw.get(DataJobExecutionOrder.PROPERTY_FIELD)).thenReturn("startTime");
      when(orderRaw.get(DataJobExecutionOrder.DIRECTION_FIELD)).thenReturn("DESC");
      when(dataFetchingEnvironment.getArgument(ORDER_FIELD)).thenReturn(orderRaw);

      DataFetcher<Object> allAndBuildResponse = executionDataFetcher.findAllAndBuildResponse();
      DataJobPage response = (DataJobPage)allAndBuildResponse.get(dataFetchingEnvironment);
      List<Object> actualJobExecutions = response.getContent();

      Assertions.assertNotNull(actualJobExecutions);
      Assertions.assertEquals(4, actualJobExecutions.size());

      assertExecutionsEquals(expectedJobExecution1, actualJobExecutions.get(3));
      assertExecutionsEquals(expectedJobExecution2, actualJobExecutions.get(2));
      assertExecutionsEquals(expectedJobExecution3, actualJobExecutions.get(1));
      assertExecutionsEquals(expectedJobExecution4, actualJobExecutions.get(0));
   }

   @Test
   public void testFindAllAndBuildResponse_orderWithoutProperty_shouldReturnResult() {
      when(dataFetchingEnvironment.getArgument(PAGE_NUMBER_FIELD)).thenReturn(1);
      when(dataFetchingEnvironment.getArgument(PAGE_SIZE_FIELD)).thenReturn(3);
      when(dataFetchingEnvironment.getArgument(FILTER_FIELD)).thenReturn(null);

      when(orderRaw.get(DataJobExecutionOrder.PROPERTY_FIELD)).thenReturn("startTime");
      when(dataFetchingEnvironment.getArgument(ORDER_FIELD)).thenReturn(orderRaw);
      DataFetcher<Object> allAndBuildResponse = executionDataFetcher.findAllAndBuildResponse();

      Assertions.assertThrows(GraphQLException.class, () -> allAndBuildResponse.get(dataFetchingEnvironment));
   }

   @Test
   public void testFindAllAndBuildResponse_orderWithoutDirection_shouldReturnResult() {
      when(dataFetchingEnvironment.getArgument(PAGE_NUMBER_FIELD)).thenReturn(1);
      when(dataFetchingEnvironment.getArgument(PAGE_SIZE_FIELD)).thenReturn(3);
      when(dataFetchingEnvironment.getArgument(FILTER_FIELD)).thenReturn(null);

      when(orderRaw.get(DataJobExecutionOrder.DIRECTION_FIELD)).thenReturn("DESC");
      when(dataFetchingEnvironment.getArgument(ORDER_FIELD)).thenReturn(orderRaw);
      DataFetcher<Object> allAndBuildResponse = executionDataFetcher.findAllAndBuildResponse();

      Assertions.assertThrows(GraphQLException.class, () -> allAndBuildResponse.get(dataFetchingEnvironment));
   }

   @Test
   public void testFindAllAndBuildResponse_withPageNumberAndPageSize_shouldReturnResult() throws Exception {
      DataJob actualDataJob = RepositoryUtil.createDataJob(jobsRepository);

      DataJobExecution expectedJobExecution1 =
            RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-1", actualDataJob, ExecutionStatus.CANCELLED);
      DataJobExecution expectedJobExecution2 =
            RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-2", actualDataJob, ExecutionStatus.RUNNING);
      DataJobExecution expectedJobExecution3 =
            RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-3", actualDataJob, ExecutionStatus.SUBMITTED);
      RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-4", actualDataJob, ExecutionStatus.FAILED);

      when(dataFetchingEnvironment.getArgument(PAGE_NUMBER_FIELD)).thenReturn(1);
      when(dataFetchingEnvironment.getArgument(PAGE_SIZE_FIELD)).thenReturn(3);

      when(dataFetchingEnvironment.getArgument(FILTER_FIELD)).thenReturn(null);
      when(dataFetchingEnvironment.getArgument(ORDER_FIELD)).thenReturn(null);

      DataFetcher<Object> allAndBuildResponse = executionDataFetcher.findAllAndBuildResponse();
      DataJobPage response = (DataJobPage)allAndBuildResponse.get(dataFetchingEnvironment);
      List<Object> actualJobExecutions = response.getContent();

      Assertions.assertNotNull(actualJobExecutions);
      Assertions.assertEquals(3, actualJobExecutions.size());

      assertExecutionsEquals(expectedJobExecution1, actualJobExecutions.get(0));
      assertExecutionsEquals(expectedJobExecution2, actualJobExecutions.get(1));
      assertExecutionsEquals(expectedJobExecution3, actualJobExecutions.get(2));
   }

   @Test
   public void testFindAllAndBuildResponse_withPageNumber_shouldReturnResult() {
      when(dataFetchingEnvironment.getArgument(PAGE_NUMBER_FIELD)).thenReturn(1);
      when(dataFetchingEnvironment.getArgument(FILTER_FIELD)).thenReturn(null);
      when(dataFetchingEnvironment.getArgument(ORDER_FIELD)).thenReturn(null);

      DataFetcher<Object> allAndBuildResponse = executionDataFetcher.findAllAndBuildResponse();

      Assertions.assertThrows(GraphQLException.class, () -> allAndBuildResponse.get(dataFetchingEnvironment));
   }

   @Test
   public void testFindAllAndBuildResponse_withPageSize_shouldReturnResult() {
      when(dataFetchingEnvironment.getArgument(PAGE_SIZE_FIELD)).thenReturn(1);
      when(dataFetchingEnvironment.getArgument(FILTER_FIELD)).thenReturn(null);
      when(dataFetchingEnvironment.getArgument(ORDER_FIELD)).thenReturn(null);

      DataFetcher<Object> allAndBuildResponse = executionDataFetcher.findAllAndBuildResponse();

      Assertions.assertThrows(GraphQLException.class, () -> allAndBuildResponse.get(dataFetchingEnvironment));
   }

   private void assertExecutionsEquals(DataJobExecution expectedJobExecution, Object actualJobExecutionObject) {
      com.vmware.taurus.controlplane.model.data.DataJobExecution actualJobExecution =
            (com.vmware.taurus.controlplane.model.data.DataJobExecution)actualJobExecutionObject;

      Assertions.assertEquals(expectedJobExecution.getId(), actualJobExecution.getId());
      Assertions.assertEquals(expectedJobExecution.getStartTime(), actualJobExecution.getStartTime());
      Assertions.assertEquals(expectedJobExecution.getEndTime(), actualJobExecution.getEndTime());
      Assertions.assertEquals(expectedJobExecution.getJobVersion(), actualJobExecution.getDeployment().getJobVersion());
   }
}
