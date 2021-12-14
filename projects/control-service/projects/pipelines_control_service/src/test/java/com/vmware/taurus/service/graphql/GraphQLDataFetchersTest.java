/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.graphql;

import com.vmware.taurus.controlplane.model.data.DataJobExecution;
import com.vmware.taurus.service.JobsRepository;
import com.vmware.taurus.service.deploy.DeploymentService;
import com.vmware.taurus.service.graphql.model.Filter;
import com.vmware.taurus.service.graphql.model.V2DataJob;
import com.vmware.taurus.service.graphql.strategy.FieldStrategy;
import com.vmware.taurus.service.graphql.strategy.JobFieldStrategyFactory;
import com.vmware.taurus.service.graphql.strategy.datajob.JobFieldStrategyBy;
import com.vmware.taurus.service.graphql.strategy.datajob.JobFieldStrategyByDescription;
import com.vmware.taurus.service.graphql.strategy.datajob.JobFieldStrategyByLastExecutionDuration;
import com.vmware.taurus.service.graphql.strategy.datajob.JobFieldStrategyByLastExecutionStatus;
import com.vmware.taurus.service.graphql.strategy.datajob.JobFieldStrategyByLastExecutionTime;
import com.vmware.taurus.service.graphql.strategy.datajob.JobFieldStrategyByName;
import com.vmware.taurus.service.graphql.strategy.datajob.JobFieldStrategyByNextRun;
import com.vmware.taurus.service.graphql.strategy.datajob.JobFieldStrategyByScheduleCron;
import com.vmware.taurus.service.graphql.strategy.datajob.JobFieldStrategyBySourceUrl;
import com.vmware.taurus.service.graphql.strategy.datajob.JobFieldStrategyByTeam;
import com.vmware.taurus.service.model.DataJob;
import com.vmware.taurus.service.graphql.model.DataJobPage;
import com.vmware.taurus.service.model.ExecutionStatus;
import com.vmware.taurus.service.model.JobConfig;
import com.vmware.taurus.service.model.JobDeploymentStatus;
import graphql.GraphQLException;
import graphql.schema.DataFetcher;
import graphql.schema.DataFetchingEnvironment;
import graphql.schema.DataFetchingFieldSelectionSet;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.data.domain.Sort;

import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

import static org.assertj.core.api.Assertions.assertThat;
import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.AdditionalMatchers.not;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class GraphQLDataFetchersTest {

   @Mock
   private ExecutionDataFetcher executionDataFetcher;

   @Mock
   private JobsRepository jobsRepository;

   @Mock
   private DeploymentService deploymentService;

   @Mock
   private DataFetchingEnvironment dataFetchingEnvironment;

   @Mock
   private DataFetchingFieldSelectionSet dataFetchingFieldSelectionSet;

   private DataFetcher<Object> findDataJobs;

   @BeforeEach
   public void before() {
      JobFieldStrategyFactory strategyFactory = new JobFieldStrategyFactory(collectSupportedFieldStrategies());
      GraphQLDataFetchers graphQLDataFetchers = new GraphQLDataFetchers(strategyFactory, jobsRepository, deploymentService, executionDataFetcher);
      findDataJobs = graphQLDataFetchers.findAllAndBuildDataJobPage();
   }

   @Test
   void testDataFetcherOfJobs_whenGettingFullList_shouldReturnAllDataJobs() throws Exception {
      when(dataFetchingEnvironment.getArgument("pageNumber")).thenReturn(1);
      when(dataFetchingEnvironment.getArgument("pageSize")).thenReturn(10);
      when(jobsRepository.findAll()).thenReturn(mockListOfDataJobs());
      when(dataFetchingEnvironment.getSelectionSet()).thenReturn(dataFetchingFieldSelectionSet);
      when(dataFetchingFieldSelectionSet.contains(not(eq(JobFieldStrategyBy.DEPLOYMENT_EXECUTIONS.getPath())))).thenReturn(true);
      when(dataFetchingFieldSelectionSet.contains(JobFieldStrategyBy.DEPLOYMENT_EXECUTIONS.getPath())).thenReturn(false);

      DataJobPage dataJobPage = (DataJobPage) findDataJobs.get(dataFetchingEnvironment);

      assertThat(dataJobPage.getContent().size()).isEqualTo(3);
   }

   @Test
   void testDataFetcherOfJobs_whenGettingPagedResult_shouldReturnPagedJobs() throws Exception {
      when(dataFetchingEnvironment.getArgument("pageNumber")).thenReturn(2);
      when(dataFetchingEnvironment.getArgument("pageSize")).thenReturn(2);
      when(jobsRepository.findAll()).thenReturn(mockListOfDataJobs());
      when(dataFetchingEnvironment.getSelectionSet()).thenReturn(dataFetchingFieldSelectionSet);
      when(dataFetchingFieldSelectionSet.contains(not(eq(JobFieldStrategyBy.DEPLOYMENT_EXECUTIONS.getPath())))).thenReturn(true);
      when(dataFetchingFieldSelectionSet.contains(JobFieldStrategyBy.DEPLOYMENT_EXECUTIONS.getPath())).thenReturn(false);

      DataJobPage dataJobPage = (DataJobPage) findDataJobs.get(dataFetchingEnvironment);

      assertThat(dataJobPage.getContent().size()).isEqualTo(1);
      V2DataJob dataJob = (V2DataJob) dataJobPage.getContent().get(0);
      assertThat(dataJob.getJobName()).isEqualTo("sample-job-3");
   }

   @Test
   void testDataFetcherOfJobs_whenSupportedFieldProvidedWithSorting_shouldReturnJobList() throws Exception {
      when(dataFetchingEnvironment.getArgument("pageNumber")).thenReturn(1);
      when(dataFetchingEnvironment.getArgument("pageSize")).thenReturn(10);
      when(dataFetchingEnvironment.getArgument("search")).thenReturn(null);
      when(jobsRepository.findAll()).thenReturn(mockListOfDataJobs());
      when(dataFetchingEnvironment.getSelectionSet()).thenReturn(dataFetchingFieldSelectionSet);
      when(dataFetchingEnvironment.getArgument("filter")).thenReturn(constructFilter(
            Filter.of("jobName", "sample-job", Sort.Direction.DESC)
      ));

      DataJobPage dataJobPage = (DataJobPage) findDataJobs.get(dataFetchingEnvironment);

      assertThat(dataJobPage.getContent().size()).isEqualTo(3);
      V2DataJob dataJob = (V2DataJob) dataJobPage.getContent().get(0);
      assertThat(dataJob.getJobName()).isEqualTo("sample-job-3");
   }



   @Test
   void testDataFetcherOfJobs_whenSearchingSpecificJob_shouldReturnSearchedJob() throws Exception {
      when(dataFetchingEnvironment.getArgument("pageNumber")).thenReturn(1);
      when(dataFetchingEnvironment.getArgument("pageSize")).thenReturn(10);
      when(dataFetchingEnvironment.getArgument("search")).thenReturn("sample-job-2");
      when(jobsRepository.findAll()).thenReturn(mockListOfDataJobs());
      when(dataFetchingEnvironment.getSelectionSet()).thenReturn(dataFetchingFieldSelectionSet);
      when(dataFetchingFieldSelectionSet.contains(not(eq(JobFieldStrategyBy.DEPLOYMENT_EXECUTIONS.getPath())))).thenReturn(true);
      when(dataFetchingFieldSelectionSet.contains(JobFieldStrategyBy.DEPLOYMENT_EXECUTIONS.getPath())).thenReturn(false);

      DataJobPage dataJobPage = (DataJobPage) findDataJobs.get(dataFetchingEnvironment);

      assertThat(dataJobPage.getContent().size()).isEqualTo(1);
      V2DataJob dataJob = (V2DataJob) dataJobPage.getContent().get(0);
      assertThat(dataJob.getJobName()).isEqualTo("sample-job-2");
   }

   @Test
   void testDataFetcherOfJobs_whenSearchingByPattern_shouldReturnMatchingJobs() throws Exception {
      when(dataFetchingEnvironment.getArgument("pageNumber")).thenReturn(1);
      when(dataFetchingEnvironment.getArgument("pageSize")).thenReturn(10);
      when(dataFetchingEnvironment.getArgument("search")).thenReturn("sample-job-2");
      when(jobsRepository.findAll()).thenReturn(mockListOfDataJobs());
      when(dataFetchingEnvironment.getSelectionSet()).thenReturn(dataFetchingFieldSelectionSet);
      when(dataFetchingFieldSelectionSet.contains(not(eq(JobFieldStrategyBy.DEPLOYMENT_EXECUTIONS.getPath())))).thenReturn(true);
      when(dataFetchingFieldSelectionSet.contains(JobFieldStrategyBy.DEPLOYMENT_EXECUTIONS.getPath())).thenReturn(false);

      DataJobPage dataJobPage = (DataJobPage) findDataJobs.get(dataFetchingEnvironment);

      assertThat(dataJobPage.getContent().size()).isEqualTo(1);
      V2DataJob dataJob = (V2DataJob) dataJobPage.getContent().get(0);
      assertThat(dataJob.getJobName()).isEqualTo("sample-job-2");
   }

   @Test
   void testDataFetcherOfJobs_whenInvalidPageSizeIsProvided_shouldThrowException() {
      when(dataFetchingEnvironment.getArgument("pageNumber")).thenReturn(1);
      when(dataFetchingEnvironment.getArgument("pageSize")).thenReturn(0);

      assertThrows(GraphQLException.class, () -> {
         findDataJobs.get(dataFetchingEnvironment);
      });
   }

   @Test
   void testDataFetcherOfJobs_whenInvalidPageNumberIsProvided_shouldThrowException() {
      when(dataFetchingEnvironment.getArgument("pageNumber")).thenReturn(0);
      when(dataFetchingEnvironment.getArgument("pageSize")).thenReturn(1);

      assertThrows(GraphQLException.class, () -> {
         findDataJobs.get(dataFetchingEnvironment);
      });
   }

   @Test
   void testDataFetcherOfJobs_whenValidPageNumberIsProvided_shouldNotThrowException() {
      when(jobsRepository.findAll()).thenReturn(mockListOfDataJobs());
      when(dataFetchingEnvironment.getSelectionSet()).thenReturn(dataFetchingFieldSelectionSet);
      when(dataFetchingEnvironment.getArgument("pageNumber")).thenReturn(1);
      when(dataFetchingEnvironment.getArgument("pageSize")).thenReturn(100);

      assertDoesNotThrow(() -> {
         findDataJobs.get(dataFetchingEnvironment);
      });
   }

   @Test
   void testPopulateDeployments() throws Exception {
      when(jobsRepository.findAll()).thenReturn(mockListOfDataJobsWithLastExecution());
      when(deploymentService.readDeployments()).thenReturn(mockListOfDeployments());
      when(dataFetchingEnvironment.getArgument("pageNumber")).thenReturn(1);
      when(dataFetchingEnvironment.getArgument("pageSize")).thenReturn(100);
      when(dataFetchingEnvironment.getSelectionSet()).thenReturn(dataFetchingFieldSelectionSet);
      when(dataFetchingFieldSelectionSet.contains(JobFieldStrategyBy.DEPLOYMENT.getPath())).thenReturn(true);

      DataJobPage dataJobPage = (DataJobPage) findDataJobs.get(dataFetchingEnvironment);

      assertThat(dataJobPage.getContent()).hasSize(5);
      var job1 = (V2DataJob)dataJobPage.getContent().get(0);
      assertThat(job1.getDeployments()).hasSize(1);
      assertThat(job1.getDeployments().get(0).getLastExecutionStatus()).isEqualTo(DataJobExecution.StatusEnum.PLATFORM_ERROR);
      assertThat(job1.getDeployments().get(0).getLastExecutionTime()).isEqualTo(OffsetDateTime.of(2000, 1, 1, 0, 0, 0, 0, ZoneOffset.UTC));
      assertThat(job1.getDeployments().get(0).getLastExecutionDuration()).isEqualTo(1000);
      var job2 = (V2DataJob)dataJobPage.getContent().get(1);
      assertThat(job2.getDeployments()).hasSize(1);
      assertThat(job2.getDeployments().get(0).getLastExecutionStatus()).isNull();
      assertThat(job2.getDeployments().get(0).getLastExecutionTime()).isNull();
      assertThat(job2.getDeployments().get(0).getLastExecutionDuration()).isNull();
   }

   @Test
   void testFilterByLastExecutionStatus() throws Exception {
      when(jobsRepository.findAll()).thenReturn(mockListOfDataJobsWithLastExecution());
      when(deploymentService.readDeployments()).thenReturn(mockListOfDeployments());
      when(dataFetchingEnvironment.getArgument("pageNumber")).thenReturn(1);
      when(dataFetchingEnvironment.getArgument("pageSize")).thenReturn(100);
      when(dataFetchingEnvironment.getArgument("search")).thenReturn(null);
      when(dataFetchingEnvironment.getSelectionSet()).thenReturn(dataFetchingFieldSelectionSet);
      when(dataFetchingFieldSelectionSet.contains(JobFieldStrategyBy.DEPLOYMENT.getPath())).thenReturn(true);
      when(dataFetchingEnvironment.getArgument("filter")).thenReturn(constructFilter(
              Filter.of("deployments.lastExecutionStatus", DataJobExecution.StatusEnum.SUCCEEDED.getValue(), null)
      ));

      DataJobPage dataJobPage = (DataJobPage) findDataJobs.get(dataFetchingEnvironment);

      assertThat(dataJobPage.getContent()).hasSize(1);
   }

   @Test
   void testSortingByLastExecutionStatus() throws Exception {
      when(jobsRepository.findAll()).thenReturn(mockListOfDataJobsWithLastExecution());
      when(deploymentService.readDeployments()).thenReturn(mockListOfDeployments());
      when(dataFetchingEnvironment.getArgument("pageNumber")).thenReturn(1);
      when(dataFetchingEnvironment.getArgument("pageSize")).thenReturn(100);
      when(dataFetchingEnvironment.getArgument("search")).thenReturn(null);
      when(dataFetchingEnvironment.getSelectionSet()).thenReturn(dataFetchingFieldSelectionSet);
      when(dataFetchingFieldSelectionSet.contains(JobFieldStrategyBy.DEPLOYMENT.getPath())).thenReturn(true);
      when(dataFetchingEnvironment.getArgument("filter")).thenReturn(constructFilter(
              Filter.of("deployments.lastExecutionStatus", null, Sort.Direction.ASC)
      ));

      DataJobPage dataJobPage = (DataJobPage) findDataJobs.get(dataFetchingEnvironment);

      var lastExecutionStatuses = dataJobPage.getContent().stream()
              .map(job -> ((V2DataJob)job).getDeployments().get(0).getLastExecutionStatus())
              .map(status -> status != null ? status.getValue() : null)
              .collect(Collectors.toList());
      assertThat(lastExecutionStatuses).hasSize(5);
      assertThat(lastExecutionStatuses.get(0)).isEqualTo(DataJobExecution.StatusEnum.PLATFORM_ERROR.getValue());
      assertThat(lastExecutionStatuses.get(1)).isEqualTo(DataJobExecution.StatusEnum.PLATFORM_ERROR.getValue());
      assertThat(lastExecutionStatuses.get(2)).isEqualTo(DataJobExecution.StatusEnum.SUCCEEDED.getValue());
      assertThat(lastExecutionStatuses.get(3)).isNull();
      assertThat(lastExecutionStatuses.get(4)).isNull();
   }

   @Test
   void testSortingByLastExecutionTime() throws Exception {
      when(jobsRepository.findAll()).thenReturn(mockListOfDataJobsWithLastExecution());
      when(deploymentService.readDeployments()).thenReturn(mockListOfDeployments());
      when(dataFetchingEnvironment.getArgument("pageNumber")).thenReturn(1);
      when(dataFetchingEnvironment.getArgument("pageSize")).thenReturn(100);
      when(dataFetchingEnvironment.getArgument("search")).thenReturn(null);
      when(dataFetchingEnvironment.getSelectionSet()).thenReturn(dataFetchingFieldSelectionSet);
      when(dataFetchingFieldSelectionSet.contains(JobFieldStrategyBy.DEPLOYMENT.getPath())).thenReturn(true);
      when(dataFetchingEnvironment.getArgument("filter")).thenReturn(constructFilter(
              Filter.of("deployments.lastExecutionTime", null, Sort.Direction.ASC)
      ));

      DataJobPage dataJobPage = (DataJobPage) findDataJobs.get(dataFetchingEnvironment);

      var lastExecutionTimes = dataJobPage.getContent().stream()
              .map(job -> ((V2DataJob)job).getDeployments().get(0).getLastExecutionTime())
              .collect(Collectors.toList());
      assertThat(lastExecutionTimes).hasSize(5);
      assertThat(lastExecutionTimes.get(0)).isEqualTo(OffsetDateTime.of(2000, 1, 1, 0, 0, 0, 0, ZoneOffset.UTC));
      assertThat(lastExecutionTimes.get(1)).isEqualTo(OffsetDateTime.of(2000, 1, 1, 0, 0, 0, 0, ZoneOffset.UTC));
      assertThat(lastExecutionTimes.get(2)).isEqualTo(OffsetDateTime.of(2000, 1, 3, 0, 0, 0, 0, ZoneOffset.UTC));
      assertThat(lastExecutionTimes.get(3)).isNull();
      assertThat(lastExecutionTimes.get(4)).isNull();
   }

   @Test
   void testSortingByLastExecutionDuration() throws Exception {
      when(jobsRepository.findAll()).thenReturn(mockListOfDataJobsWithLastExecution());
      when(deploymentService.readDeployments()).thenReturn(mockListOfDeployments());
      when(dataFetchingEnvironment.getArgument("pageNumber")).thenReturn(1);
      when(dataFetchingEnvironment.getArgument("pageSize")).thenReturn(100);
      when(dataFetchingEnvironment.getArgument("search")).thenReturn(null);
      when(dataFetchingEnvironment.getSelectionSet()).thenReturn(dataFetchingFieldSelectionSet);
      when(dataFetchingFieldSelectionSet.contains(JobFieldStrategyBy.DEPLOYMENT.getPath())).thenReturn(true);
      when(dataFetchingEnvironment.getArgument("filter")).thenReturn(constructFilter(
              Filter.of("deployments.lastExecutionDuration", null, Sort.Direction.DESC)
      ));

      DataJobPage dataJobPage = (DataJobPage) findDataJobs.get(dataFetchingEnvironment);

      var lastExecutionTimes = dataJobPage.getContent().stream()
              .map(job -> ((V2DataJob)job).getDeployments().get(0).getLastExecutionDuration())
              .collect(Collectors.toList());
      assertThat(lastExecutionTimes).hasSize(5);
      assertThat(lastExecutionTimes.get(0)).isNull();
      assertThat(lastExecutionTimes.get(1)).isNull();
      assertThat(lastExecutionTimes.get(2)).isEqualTo(1000);
      assertThat(lastExecutionTimes.get(3)).isEqualTo(1000);
      assertThat(lastExecutionTimes.get(4)).isEqualTo(0);
   }


   private List<JobDeploymentStatus> mockListOfDeployments() {
      List<JobDeploymentStatus> jobDeployments = new ArrayList<>();

      jobDeployments.add(mockSampleDeployment("sample-job-1", true));
      jobDeployments.add(mockSampleDeployment("sample-job-2", false));
      jobDeployments.add(mockSampleDeployment("sample-job-3", true));
      jobDeployments.add(mockSampleDeployment("sample-job-4", true));
      jobDeployments.add(mockSampleDeployment("sample-job-5", true));

      return jobDeployments;
   }

   private List<DataJob> mockListOfDataJobs() {
      List<DataJob> dataJobs = new ArrayList<>();

      dataJobs.add(mockSampleDataJob("sample-job-1", "Import SQL", "5 12 * * *"));
      dataJobs.add(mockSampleDataJob("sample-job-2", "Dump SQL", "0 22 * * 1-5"));
      dataJobs.add(mockSampleDataJob("sample-job-3", "Delete users", "0 4 8-14 * *"));

      return dataJobs;
   }

   private List<DataJob> mockListOfDataJobsWithLastExecution() {
      List<DataJob> dataJobs = new ArrayList<>();

      dataJobs.add(mockSampleDataJob("sample-job-1", "Import SQL", "5 12 * * *",
              ExecutionStatus.PLATFORM_ERROR, OffsetDateTime.of(2000, 1, 1, 0, 0, 0, 0, ZoneOffset.UTC), 1000));
      dataJobs.add(mockSampleDataJob("sample-job-2", "Dump SQL", "0 22 * * 1-5"));
      dataJobs.add(mockSampleDataJob("sample-job-3", "Import SQL", "5 12 * * *",
              ExecutionStatus.PLATFORM_ERROR, OffsetDateTime.of(2000, 1, 3, 0, 0, 0, 0, ZoneOffset.UTC), null));
      dataJobs.add(mockSampleDataJob("sample-job-4", "Import SQL", "5 12 * * *",
              ExecutionStatus.SUCCEEDED, null, 0));
      dataJobs.add(mockSampleDataJob("sample-job-5", "Import SQL", "5 12 * * *",
              null, OffsetDateTime.of(2000, 1, 1, 0, 0, 0, 0, ZoneOffset.UTC), 1000));

      return dataJobs;
   }

   private DataJob mockSampleDataJob(String jobName, String description, String schedule) {
      return mockSampleDataJob(jobName, description, schedule, null, null, null);
   }

   private DataJob mockSampleDataJob(String jobName,
                                     String description,
                                     String schedule,
                                     ExecutionStatus lastExecutionStatus,
                                     OffsetDateTime lastExecutionEndTime,
                                     Integer lastExecutionDuration) {
      DataJob dataJob = new DataJob();
      JobConfig jobConfig = new JobConfig();
      jobConfig.setSchedule(schedule);
      jobConfig.setDescription(description);
      dataJob.setJobConfig(jobConfig);
      dataJob.setName(jobName);
      dataJob.setLastExecutionStatus(lastExecutionStatus);
      dataJob.setLastExecutionEndTime(lastExecutionEndTime);
      dataJob.setLastExecutionDuration(lastExecutionDuration);

      return dataJob;
   }

   private JobDeploymentStatus mockSampleDeployment(String jobName, boolean enabled) {
      JobDeploymentStatus status = new JobDeploymentStatus();
      status.setEnabled(enabled);
      status.setDataJobName(jobName);
      status.setCronJobName(jobName+"-latest");
      status.setMode("release");
      return status;
   }

   static ArrayList<LinkedHashMap<String, String>> constructFilter(Filter ... filters) {
      ArrayList<LinkedHashMap<String, String>> rawFilters = new ArrayList<>();
      Arrays.stream(filters).forEach(filter -> {
         LinkedHashMap<String, String> map = new LinkedHashMap<>();

         map.put("property", filter.getProperty());
         map.put("pattern", filter.getPattern());
         if (filter.getSort() != null) {
            map.put("sort", filter.getSort().toString());
         }

         rawFilters.add(map);
      });

      return rawFilters;
   }

   private Set<FieldStrategy<V2DataJob>> collectSupportedFieldStrategies() {
      Set<FieldStrategy<V2DataJob>> strategies = new HashSet<>();

      strategies.add(new JobFieldStrategyByDescription());
      strategies.add(new JobFieldStrategyByName());
      strategies.add(new JobFieldStrategyByNextRun());
      strategies.add(new JobFieldStrategyByScheduleCron());
      strategies.add(new JobFieldStrategyBySourceUrl("gitlab.com/demo-data-jobs.git", "main", true));
      strategies.add(new JobFieldStrategyByTeam());
      strategies.add(new JobFieldStrategyByLastExecutionStatus());
      strategies.add(new JobFieldStrategyByLastExecutionTime());
      strategies.add(new JobFieldStrategyByLastExecutionDuration());

      return strategies;
   }
}
