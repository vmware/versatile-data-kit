/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright (c) 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.graphql;

import com.vmware.taurus.datajobs.ToApiModelConverter;
import com.vmware.taurus.datajobs.ToModelApiConverter;
import com.vmware.taurus.service.JobExecutionFilterSpec;
import com.vmware.taurus.service.JobExecutionRepository;
import com.vmware.taurus.service.execution.JobExecutionService;
import com.vmware.taurus.service.graphql.model.*;
import com.vmware.taurus.service.graphql.strategy.datajob.JobFieldStrategyBy;
import com.vmware.taurus.service.model.DataJobExecution;
import com.vmware.taurus.service.model.ExecutionStatus;
import graphql.GraphQLException;
import graphql.schema.DataFetcher;
import graphql.schema.DataFetchingEnvironment;
import graphql.schema.SelectedField;
import lombok.RequiredArgsConstructor;
import org.apache.commons.lang3.StringUtils;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.springframework.data.domain.*;
import org.springframework.data.jpa.domain.Specification;
import org.springframework.stereotype.Component;

import java.time.OffsetDateTime;
import java.util.*;
import java.util.stream.Collectors;

import static com.vmware.taurus.service.graphql.model.DataJobExecutionOrder.*;
import static com.vmware.taurus.service.graphql.model.DataJobExecutionQueryVariables.*;

/**
 * Data fetcher class for Data Job Executions
 * <p>
 * Data fetchers are classes that provides to graphql api the needed data while it modify the source data:
 * By providing list of data jobs it alter each job and attach its execution while reading requested
 * information from graphql query to specify how many executions, are they sorted by specific field, etc.
 */
@Component
@RequiredArgsConstructor
public class ExecutionDataFetcher {

   private final JobExecutionRepository jobsExecutionRepository;
   private final JobExecutionService jobExecutionService;


   /**
    * Currently, it does not provide filtering by specifying fields due
    * to its post-pagination loading - the execution data is attached after slicing of the requested page.
    */
   List<V2DataJob> populateExecutions(List<V2DataJob> allDataJob, DataFetchingEnvironment dataFetchingEnvironment) {
      final ExecutionQueryVariables queryVariables = fetchQueryVariables(dataFetchingEnvironment);
      final Pageable pageable = constructPageable(queryVariables);
      allDataJob.forEach(dataJob -> {
         if (dataJob.getDeployments() != null) {
            dataJob.getDeployments()
                    .stream()
                    .findFirst()
                    .ifPresent(deployment -> deployment.setExecutions(
                            jobsExecutionRepository.findDataJobExecutionsByDataJobName(dataJob.getJobName(), pageable)
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

      Map<String, Object> execArgs = executionFields.getArguments();
      Optional<ImmutablePair<Integer, Integer>> page = extractDataJobExecutionPage(
            execArgs.get(PAGE_NUMBER_FIELD),
            execArgs.get(PAGE_SIZE_FIELD));

      page.ifPresent(pair -> {
         queryVariables.setPageNumber(pair.getLeft());
         queryVariables.setPageSize(pair.getRight());
      });

      queryVariables.setFilters(GraphQLUtils.convertFilters((ArrayList<LinkedHashMap<String, String>>)execArgs.get("filter")));
      validateFilterInputForExecutions(queryVariables.getFilters());

      return queryVariables;
   }

   public DataFetcher<Object> findAllAndBuildResponse() {
      return environment -> {
         DataJobExecutionQueryVariables dataJobExecutionQueryVariables = fetchDataJobExecutionQueryVariables(environment);

         Page<DataJobExecution> dataJobExecutionsResult = findAllExecutions(dataJobExecutionQueryVariables);
         List<com.vmware.taurus.controlplane.model.data.DataJobExecution> dataJobExecutions = dataJobExecutionsResult
               .getContent()
               .stream()
               .map(dataJobExecution -> ToApiModelConverter.jobExecutionToConvert(dataJobExecution))
               .collect(Collectors.toList());

         return buildResponse(
               dataJobExecutionsResult.getTotalPages(),
               dataJobExecutionsResult.getNumberOfElements(),
               dataJobExecutions);
      };
   }

   private Page<DataJobExecution> findAllExecutions(DataJobExecutionQueryVariables dataJobExecutionQueryVariables) {
      Specification<DataJobExecution> filterSpec = new JobExecutionFilterSpec(dataJobExecutionQueryVariables.getFilter());
      Page<DataJobExecution> result;
      DataJobExecutionOrder order = dataJobExecutionQueryVariables.getOrder();
      Sort sort = order != null ? Sort.by(order.getDirection(), order.getProperty()) : null;

      if (dataJobExecutionQueryVariables.getPageNumber() != null && dataJobExecutionQueryVariables.getPageSize() != null) {
         PageRequest pageRequest = PageRequest.of(
               dataJobExecutionQueryVariables.getPageNumber() - 1,
               dataJobExecutionQueryVariables.getPageSize());
         pageRequest = sort != null ? pageRequest.withSort(sort) : pageRequest;

         result = jobsExecutionRepository.findAll(filterSpec, pageRequest);
      } else {
         List<DataJobExecution> elements = sort == null ?
               jobsExecutionRepository.findAll(filterSpec) :
               jobsExecutionRepository.findAll(filterSpec, sort);

         result = new PageImpl(elements);
      }

      return result;
   }

   /**
    * As we receive filters as custom GraphQL object, this method translated it to Spring data Pageable element
    * By default if there isn't any fields specified we return only paginating details
    * If sorting is not provided we use the default (ASC), by design it take maximum 1 sorting
    *
    * @param queryVar
    *       Query variables which holds multiple Filter object
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

   private static DataJobExecutionQueryVariables fetchDataJobExecutionQueryVariables(DataFetchingEnvironment dataFetchingEnvironment) {
      DataJobExecutionQueryVariables queryVariables = new DataJobExecutionQueryVariables();

      Optional<ImmutablePair<Integer, Integer>> page = extractDataJobExecutionPage(
            dataFetchingEnvironment.getArgument(PAGE_NUMBER_FIELD),
            dataFetchingEnvironment.getArgument(PAGE_SIZE_FIELD));

      page.ifPresent(pair -> {
         queryVariables.setPageNumber(pair.getLeft());
         queryVariables.setPageSize(pair.getRight());
      });

      extractDataJobExecutionFilter(dataFetchingEnvironment.getArgument(FILTER_FIELD))
            .ifPresent(filter -> queryVariables.setFilter(filter));

      extractDataJobExecutionOrder(dataFetchingEnvironment.getArgument(ORDER_FIELD))
            .ifPresent(order -> queryVariables.setOrder(order));

      return queryVariables;
   }

   private static Optional<ImmutablePair<Integer, Integer>> extractDataJobExecutionPage(Object pageNumberRaw, Object pageSizeRaw) {
      Optional<ImmutablePair<Integer, Integer>> result = Optional.empty();

      if (pageNumberRaw != null && pageSizeRaw == null) {
         throw new GraphQLException(String.format("Executions field must contain %s", PAGE_SIZE_FIELD));
      }

      if (pageNumberRaw == null && pageSizeRaw != null) {
         throw new GraphQLException(String.format("Executions field must contain %s", PAGE_NUMBER_FIELD));
      }

      if (pageNumberRaw != null && pageSizeRaw != null) {
         Integer pageNumber = (Integer)pageNumberRaw;
         Integer pageSize = (Integer)pageSizeRaw;
         GraphQLUtils.validatePageInput(pageSize, pageNumber);
         result = Optional.of(ImmutablePair.of(pageNumber, pageSize));
      }

      return result;
   }

   private static Optional<DataJobExecutionFilter> extractDataJobExecutionFilter(Map<String, Object> filterRaw) {
      Optional<DataJobExecutionFilter> filter = Optional.empty();

      if (filterRaw != null) {
         DataJobExecutionFilter.DataJobExecutionFilterBuilder builder = DataJobExecutionFilter.builder();

         builder.statusIn(
               Optional.ofNullable(filterRaw.get(DataJobExecutionFilter.STATUS_IN_FIELD))
                     .map(statusInRaw -> ((List<String>)statusInRaw))
                     .stream()
                     .flatMap(v1Jobs -> v1Jobs.stream())
                     .filter(Objects::nonNull)
                     .map(status -> com.vmware.taurus.controlplane.model.data.DataJobExecution.StatusEnum.fromValue(status.toLowerCase()))
                     .map(statusEnum -> ToModelApiConverter.toExecutionStatus(statusEnum))
                     .collect(Collectors.toList())
         );

         filter = Optional.of(
               builder
                     .startTimeGte((OffsetDateTime)filterRaw.get(DataJobExecutionFilter.START_TIME_GTE_FIELD))
                     .endTimeGte((OffsetDateTime)filterRaw.get(DataJobExecutionFilter.END_TIME_GTE_FIELD))
                     .build()
         );
      }

      return filter;
   }

   private static Optional<DataJobExecutionOrder> extractDataJobExecutionOrder(Map<String, Object> orderRaw) {
      Optional<DataJobExecutionOrder> order = Optional.empty();

      if (orderRaw != null) {
         DataJobExecutionOrder.DataJobExecutionOrderBuilder builder = DataJobExecutionOrder.builder();

         builder.property(
               Optional.ofNullable(orderRaw.get(PROPERTY_FIELD))
                     .map(o -> (String)o)
                     .filter(p -> AVAILABLE_PROPERTIES.contains(p))
                     .orElseThrow(() -> new GraphQLException(String.format(
                           "%s.%s must be in [%s]",
                           ORDER_FIELD,
                           PROPERTY_FIELD,
                           StringUtils.join(AVAILABLE_PROPERTIES, ","))))
         );

         builder.direction(
               Optional.ofNullable(orderRaw.get(DIRECTION_FIELD))
                     .map(o -> Sort.Direction.fromString((String)o))
                     .orElseThrow(() -> new GraphQLException(String.format(
                           "Executions field must contain %s.%s",
                           ORDER_FIELD,
                           DIRECTION_FIELD)))
         );

         order = Optional.of(builder.build());
      }

      return order;
   }

   private static DataJobPage buildResponse(
         int pageSize,
         int count,
         List pageList) {

      return DataJobPage.builder()
            .content(new ArrayList<>(pageList))
            .totalPages(pageSize)
            .totalItems(count).build();
   }

   List<V2DataJob> populateStatusCounts(List<V2DataJob> dataJos, DataFetchingEnvironment dataFetchingEnvironment) {

      var statusesToCount = determineStatusesToCount(dataFetchingEnvironment);
      var jobsList = dataJos.stream().map(V2DataJob::getJobName).collect(Collectors.toList());
      var response = jobExecutionService.countExecutionStatuses(jobsList, statusesToCount);

      dataJos.stream()
              .forEach(job -> {
                 if (job.getDeployments() != null) {
                    job.getDeployments()
                            .stream()
                            .findFirst()
                            .ifPresent(deployment -> {
                               setStatusCounts(response, job, dataFetchingEnvironment, deployment);
                            });
                 }
              });
      return dataJos;
   }

   private void setStatusCounts(Map<String, Map<ExecutionStatus, Integer>> response, V2DataJob job,
                              DataFetchingEnvironment dataFetchingEnvironment, V2DataJobDeployment v2DataJobDeployment) {

      var selectionSet = dataFetchingEnvironment.getSelectionSet();
      var statusCountsPerJob = response.getOrDefault(job.getJobName(), Map.of());

      if (selectionSet.contains(JobFieldStrategyBy.DEPLOYMENT_FAILED_EXECUTIONS.getPath())) {
         v2DataJobDeployment.setFailedExecutions(statusCountsPerJob.getOrDefault(ExecutionStatus.FAILED, 0));
      }

      if (selectionSet.contains(JobFieldStrategyBy.DEPLOYMENT_SUCCESSFUL_EXECUTIONS.getPath())) {
         v2DataJobDeployment.setSuccessfulExecutions(statusCountsPerJob.getOrDefault(ExecutionStatus.FINISHED, 0));
      }
   }

   private List<ExecutionStatus> determineStatusesToCount(DataFetchingEnvironment dataFetchingEnvironment) {
      var selectionSet = dataFetchingEnvironment.getSelectionSet();
      List<ExecutionStatus> statusesToCount = new ArrayList<>();
      if (selectionSet.contains(JobFieldStrategyBy.DEPLOYMENT_FAILED_EXECUTIONS.getPath())) {
         statusesToCount.add(ExecutionStatus.FAILED);
      }
      if (selectionSet.contains(JobFieldStrategyBy.DEPLOYMENT_SUCCESSFUL_EXECUTIONS.getPath())) {
         statusesToCount.add(ExecutionStatus.FINISHED);
      }
      return statusesToCount;
   }

}
