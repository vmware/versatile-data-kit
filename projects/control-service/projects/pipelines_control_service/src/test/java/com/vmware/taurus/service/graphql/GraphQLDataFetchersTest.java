/*
 * Copyright (c) 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.graphql;

import com.vmware.taurus.service.JobsRepository;
import com.vmware.taurus.service.deploy.DeploymentService;
import com.vmware.taurus.service.graphql.model.Filter;
import com.vmware.taurus.service.graphql.model.V2DataJob;
import com.vmware.taurus.service.graphql.strategy.FieldStrategy;
import com.vmware.taurus.service.graphql.strategy.JobFieldStrategyFactory;
import com.vmware.taurus.service.graphql.strategy.datajob.JobFieldStrategyBy;
import com.vmware.taurus.service.graphql.strategy.datajob.JobFieldStrategyByDescription;
import com.vmware.taurus.service.graphql.strategy.datajob.JobFieldStrategyByName;
import com.vmware.taurus.service.graphql.strategy.datajob.JobFieldStrategyByNextRun;
import com.vmware.taurus.service.graphql.strategy.datajob.JobFieldStrategyByScheduleCron;
import com.vmware.taurus.service.graphql.strategy.datajob.JobFieldStrategyBySourceUrl;
import com.vmware.taurus.service.graphql.strategy.datajob.JobFieldStrategyByTeam;
import com.vmware.taurus.service.model.DataJob;
import com.vmware.taurus.service.model.DataJobPage;
import com.vmware.taurus.service.model.JobConfig;
import com.vmware.taurus.service.model.JobDeploymentStatus;
import graphql.GraphQLException;
import graphql.schema.DataFetcher;
import graphql.schema.DataFetchingEnvironment;
import graphql.schema.DataFetchingFieldSelectionSet;
import graphql.schema.SelectedField;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.data.domain.Sort;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

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
   @Mock
   private SelectedField selectedField;
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

      when(dataFetchingEnvironment.getArgument("pageSize")).thenReturn(101);
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


   private List<JobDeploymentStatus> mockListOfDeployments() {
      List<JobDeploymentStatus> jobDeployments = new ArrayList<>();

      jobDeployments.add(mockSampleDeployment("sample-job-1", true));
      jobDeployments.add(mockSampleDeployment("sample-job-2", false));

      return jobDeployments;
   }

   private List<DataJob> mockListOfDataJobs() {
      List<DataJob> dataJobs = new ArrayList<>();

      dataJobs.add(mockSampleDataJob("sample-job-1", "Import SQL", "5 12 * * *"));
      dataJobs.add(mockSampleDataJob("sample-job-2", "Dump SQL", "0 22 * * 1-5"));
      dataJobs.add(mockSampleDataJob("sample-job-3", "Delete users", "0 4 8-14 * *"));

      return dataJobs;
   }

   private DataJob mockSampleDataJob(String jobName, String description, String schedule) {
      DataJob dataJob = new DataJob();
      JobConfig jobConfig = new JobConfig();
      jobConfig.setSchedule(schedule);
      jobConfig.setDescription(description);
      dataJob.setJobConfig(jobConfig);
      dataJob.setName(jobName);

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

   static ArrayList<LinkedHashMap<String, String>> constructFilter(Filter ... filters ) {
      ArrayList<LinkedHashMap<String, String>> rawFilters = new ArrayList<>();
      Arrays.stream(filters).forEach(filter -> {
         LinkedHashMap<String, String> map = new LinkedHashMap<>();

         map.put("property", filter.getProperty());
         map.put("pattern", filter.getPattern());
         map.put("sort", filter.getSort().toString());

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
      strategies.add(new JobFieldStrategyBySourceUrl("gitlab.com/demo-data-jobs.git", "main"));
      strategies.add(new JobFieldStrategyByTeam());

      return strategies;
   }
}
