/*
 * Copyright (c) 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.graphql;

import com.vmware.taurus.datajobs.ToApiModelConverter;
import com.vmware.taurus.service.JobExecutionRepository;
import com.vmware.taurus.service.graphql.model.V2DataJob;
import com.vmware.taurus.service.graphql.strategy.datajob.JobFieldStrategyBy;
import com.vmware.taurus.service.model.DataJobExecution;
import com.vmware.taurus.service.graphql.model.Filter;
import com.vmware.taurus.service.graphql.model.ExecutionQueryVariables;
import graphql.GraphQLException;
import graphql.schema.DataFetchingEnvironment;
import graphql.schema.SelectedField;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Component;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.stream.Collectors;

/**
 * Data fetcher class for Data Job Executions
 *
 * Data fetchers are classes that provides to graphql api the needed data while it modify the source data:
 * By providing list of data jobs it alter each job and attach its execution while reading requested
 * information from graphql query to specify how many executions, are they sorted by specific field, etc.
 *
 * Currently, execution data fetcher does not provide filtering by specifying fields due
 * to its post-pagination loading - the execution data is attached after slicing of the requested page.
 */
@Component
public class ExecutionDataFetcher {

   private final JobExecutionRepository jobsExecutionRepository;

   public ExecutionDataFetcher(JobExecutionRepository jobsExecutionRepository) {
      this.jobsExecutionRepository = jobsExecutionRepository;
   }

   List<V2DataJob> populateExecutions(List<V2DataJob> allDataJob, DataFetchingEnvironment dataFetchingEnvironment) {
      final ExecutionQueryVariables queryVariables = fetchQueryVariables(dataFetchingEnvironment);
      final Pageable pageable = constructPageable(queryVariables);
      allDataJob.forEach(dataJob -> {
         if (dataJob.getDeployments() != null) {
            List<DataJobExecution> executionsPerJob = jobsExecutionRepository.findDataJobExecutionsByDataJobName(dataJob.getJobName(), pageable);
            dataJob.getDeployments()
                  .stream()
                  .findFirst()
                  .ifPresent(deployment -> deployment.setExecutions(
                        executionsPerJob
                              .stream()
                              .map(ToApiModelConverter::jobExecutionToConvert)
                              .collect(Collectors.toList())));
         }
      });
      return allDataJob;
   }

   @SuppressWarnings("unchecked")
   private ExecutionQueryVariables fetchQueryVariables(DataFetchingEnvironment dataFetchingEnvironment) {
      ExecutionQueryVariables queryVariables = new ExecutionQueryVariables();
      SelectedField executionFields = dataFetchingEnvironment
            .getSelectionSet().getField(JobFieldStrategyBy.DEPLOYMENT_EXECUTIONS.getPath());

      Map<String, Object> execArgs =  executionFields.getArguments();
      if (execArgs.get("pageNumber") == null || execArgs.get("pageSize") == null) {
         throw new GraphQLException("Executions field must contain pageSize and pageNumber");
      }
      queryVariables.setPageNumber((int) execArgs.get("pageNumber"));
      queryVariables.setPageSize((int) execArgs.get("pageSize"));
      GraphQLUtils.validatePageInput(queryVariables.getPageSize(), queryVariables.getPageNumber());
      queryVariables.setFilters(GraphQLUtils.convertFilters((ArrayList<LinkedHashMap<String, String>>) execArgs.get("filter")));
      validateFilterInputForExecutions(queryVariables.getFilters());

      return queryVariables;
   }

   /**
    * As we receive filters as custom GraphQL object, this method translated it to Spring data Pageable element
    * By default if there isn't any fields specified we return only paginating details
    * If sorting is not provided we use the default (ASC), by design it take maximum 1 sorting
    * @param queryVar Query variables which holds multiple Filter object
    * @return Pageable element containing page and sort
    */
   private Pageable constructPageable(ExecutionQueryVariables queryVar) {
      Sort.Direction direction = queryVar.getFilters().stream()
            .map(Filter::getSort)
            .filter(Objects::nonNull)
            .findFirst()
            .orElse(Sort.Direction.ASC);

      List<Sort.Order> order = queryVar.getFilters().stream()
            .map(Filter::getProperty)
            .filter(Objects::nonNull)
            .map(s -> s.replace(JobFieldStrategyBy.DEPLOYMENT_EXECUTIONS.getField() + ".", ""))
            .map(s -> new Sort.Order(direction, s))
            .collect(Collectors.toList());

      PageRequest pageRequest = PageRequest.of(queryVar.getPageNumber() - 1, queryVar.getPageSize());
      return order.isEmpty() ? pageRequest : pageRequest.withSort(Sort.by(order));
   }

   void validateFilterInputForExecutions(List<Filter> executionsFilter) {
      final Optional<Filter> filterNotSupported = executionsFilter.stream()
            .filter(e -> e.getPattern() != null)
            .findAny();
      if (filterNotSupported.isPresent()) {
         throw new GraphQLException("Using patterns for execution filtering is currently not supported");
      }
   }

}
