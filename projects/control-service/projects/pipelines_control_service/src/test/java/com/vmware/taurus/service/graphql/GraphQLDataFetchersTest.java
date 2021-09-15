/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.graphql;

import com.vmware.taurus.service.JobsRepository;
import com.vmware.taurus.service.deploy.DeploymentService;
import com.vmware.taurus.service.graphql.model.V2DataJob;
import com.vmware.taurus.service.graphql.strategy.FieldStrategy;
import com.vmware.taurus.service.graphql.strategy.JobFieldStrategyFactory;
import com.vmware.taurus.service.graphql.strategy.datajob.*;
import com.vmware.taurus.service.model.DataJob;
import com.vmware.taurus.service.model.DataJobPage;
import com.vmware.taurus.service.model.Filter;
import com.vmware.taurus.service.model.JobConfig;
import graphql.GraphQLException;
import graphql.GraphqlErrorException;
import graphql.schema.DataFetcher;
import graphql.schema.DataFetchingEnvironment;
import graphql.schema.DataFetchingFieldSelectionSet;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.*;

import static org.assertj.core.api.Assertions.assertThat;
import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class GraphQLDataFetchersTest {


   @Mock
   private JobsRepository jobsRepository;
   @Mock
   private DeploymentService deploymentService;
   @Mock
   private DataFetchingEnvironment dataFetchingEnvironment;
   @Mock
   private DataFetchingFieldSelectionSet dataFetchingFieldSelectionSet;
   private DataFetcher<Object> findDataJobs;
   private ArrayList<LinkedHashMap<String, String>> rawFilters;

   @BeforeEach
   public void before() {
      JobFieldStrategyFactory strategyFactory = new JobFieldStrategyFactory(collectSupportedFieldStrategies());
      GraphQLDataFetchers graphQLDataFetchers = new GraphQLDataFetchers(strategyFactory, jobsRepository, deploymentService);
      findDataJobs = graphQLDataFetchers.findAllAndBuildDataJobPage();
   }

   @Test
   void testDataFetcherOfJobs_whenGettingFullList_shouldReturnAllDataJobs() throws Exception {
      when(dataFetchingEnvironment.getArgument("pageNumber")).thenReturn(1);
      when(dataFetchingEnvironment.getArgument("pageSize")).thenReturn(10);
      when(jobsRepository.findAll()).thenReturn(mockListOfDataJobs());
      when(dataFetchingEnvironment.getSelectionSet()).thenReturn(dataFetchingFieldSelectionSet);
      when(dataFetchingFieldSelectionSet.contains(anyString())).thenReturn(true);

      DataJobPage dataJobPage = (DataJobPage) findDataJobs.get(dataFetchingEnvironment);

      assertThat(dataJobPage.getContent().size()).isEqualTo(3);
   }

   @Test
   void testDataFetcherOfJobs_whenGettingPagedResult_shouldReturnPagedJobs() throws Exception {
      when(dataFetchingEnvironment.getArgument("pageNumber")).thenReturn(2);
      when(dataFetchingEnvironment.getArgument("pageSize")).thenReturn(2);
      when(jobsRepository.findAll()).thenReturn(mockListOfDataJobs());
      when(dataFetchingEnvironment.getSelectionSet()).thenReturn(dataFetchingFieldSelectionSet);
      when(dataFetchingFieldSelectionSet.contains(anyString())).thenReturn(true);

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
            Filter.of("jobName", "sample-job", Filter.Direction.DESC)
      ));

      DataJobPage dataJobPage = (DataJobPage) findDataJobs.get(dataFetchingEnvironment);

      assertThat(dataJobPage.getContent().size()).isEqualTo(3);
      V2DataJob dataJob = (V2DataJob) dataJobPage.getContent().get(0);
      assertThat(dataJob.getJobName()).isEqualTo("sample-job-3");
   }

   @Test
   void testDataFetcherOfJobs_whenUnsupportedFieldProvided_shouldThrowException() {
      when(dataFetchingEnvironment.getArgument("pageNumber")).thenReturn(2);
      when(dataFetchingEnvironment.getArgument("pageSize")).thenReturn(2);
      when(jobsRepository.findAll()).thenReturn(mockListOfDataJobs());
      when(dataFetchingEnvironment.getSelectionSet()).thenReturn(dataFetchingFieldSelectionSet);
      when(dataFetchingEnvironment.getArgument("search")).thenReturn(null);
      when(dataFetchingEnvironment.getArgument("filter")).thenReturn(constructFilter(
            Filter.of(UUID.randomUUID().toString(), "sample-job-1", Filter.Direction.ASC)
      ));

      assertThrows(GraphqlErrorException.class, () -> {
         findDataJobs.get(dataFetchingEnvironment);
      });
   }

   @Test
   void testDataFetcherOfJobs_whenSearchingSpecificJob_shouldReturnSearchedJob() throws Exception {
      when(dataFetchingEnvironment.getArgument("pageNumber")).thenReturn(1);
      when(dataFetchingEnvironment.getArgument("pageSize")).thenReturn(10);
      when(dataFetchingEnvironment.getArgument("search")).thenReturn("sample-job-2");
      when(jobsRepository.findAll()).thenReturn(mockListOfDataJobs());
      when(dataFetchingEnvironment.getSelectionSet()).thenReturn(dataFetchingFieldSelectionSet);
      when(dataFetchingFieldSelectionSet.contains(anyString())).thenReturn(true);

      DataJobPage dataJobPage = (DataJobPage) findDataJobs.get(dataFetchingEnvironment);

      assertThat(dataJobPage.getContent().size()).isEqualTo(1);
      V2DataJob dataJob = (V2DataJob) dataJobPage.getContent().get(0);
      assertThat(dataJob.getJobName()).isEqualTo("sample-job-2");
   }

   @Test
   void testDataFetcherOfJobs_whenSearchingByPattern_shouldReturnMathchingJobs() throws Exception {
      when(dataFetchingEnvironment.getArgument("pageNumber")).thenReturn(1);
      when(dataFetchingEnvironment.getArgument("pageSize")).thenReturn(10);
      when(dataFetchingEnvironment.getArgument("search")).thenReturn("sample-job-2");
      when(jobsRepository.findAll()).thenReturn(mockListOfDataJobs());
      when(dataFetchingEnvironment.getSelectionSet()).thenReturn(dataFetchingFieldSelectionSet);
      when(dataFetchingFieldSelectionSet.contains(anyString())).thenReturn(true);

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

   private ArrayList<LinkedHashMap<String, String>> constructFilter(Filter ... filters ) {
      rawFilters = new ArrayList<>();
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
      strategies.add(new JobFieldStrategyBySourceUrl("gitlab.com/demo-data-jobs.git", "main", true));
      strategies.add(new JobFieldStrategyByTeam());

      return strategies;
   }
}
