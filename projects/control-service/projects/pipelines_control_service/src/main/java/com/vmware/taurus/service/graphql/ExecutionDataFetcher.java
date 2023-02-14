/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

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
import com.vmware.taurus.service.execution.JobExecutionLogsUrlBuilder;
import com.vmware.taurus.service.execution.JobExecutionService;
import com.vmware.taurus.service.graphql.model.DataJobExecutionFilter;
import com.vmware.taurus.service.graphql.model.DataJobExecutionOrder;
import com.vmware.taurus.service.graphql.model.DataJobExecutionQueryVariables;
import com.vmware.taurus.service.graphql.model.DataJobPage;
import com.vmware.taurus.service.graphql.model.V2DataJob;
import com.vmware.taurus.service.graphql.model.V2DataJobDeployment;
import com.vmware.taurus.service.graphql.strategy.datajob.JobFieldStrategyBy;
import com.vmware.taurus.service.model.DataJobExecution;
import com.vmware.taurus.service.model.ExecutionStatus;
import graphql.GraphQLException;
import graphql.schema.DataFetcher;
import graphql.schema.DataFetchingEnvironment;
import graphql.schema.DataFetchingFieldSelectionSet;
import lombok.RequiredArgsConstructor;
import org.apache.commons.lang3.StringUtils;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
import org.springframework.data.jpa.domain.Specification;
import org.springframework.stereotype.Component;

import java.time.OffsetDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.stream.Collectors;

import static com.vmware.taurus.service.graphql.model.DataJobExecutionOrder.AVAILABLE_PROPERTIES;
import static com.vmware.taurus.service.graphql.model.DataJobExecutionOrder.DIRECTION_FIELD;
import static com.vmware.taurus.service.graphql.model.DataJobExecutionOrder.PROPERTY_FIELD;
import static com.vmware.taurus.service.graphql.model.DataJobExecutionOrder.PUBLIC_NAME_TO_DB_ENTITY_MAP;
import static com.vmware.taurus.service.graphql.model.DataJobExecutionQueryVariables.FILTER_FIELD;
import static com.vmware.taurus.service.graphql.model.DataJobExecutionQueryVariables.ORDER_FIELD;
import static com.vmware.taurus.service.graphql.model.DataJobExecutionQueryVariables.PAGE_NUMBER_FIELD;
import static com.vmware.taurus.service.graphql.model.DataJobExecutionQueryVariables.PAGE_SIZE_FIELD;

/**
 * Data fetcher class for Data Job Executions
 *
 * <p>Data fetchers are classes that provides to graphql api the needed data while it modify the
 * source data: By providing list of data jobs it alter each job and attach its execution while
 * reading requested information from graphql query to specify how many executions, are they sorted
 * by specific field, etc.
 */
@Component
@RequiredArgsConstructor
public class ExecutionDataFetcher {

  private final JobExecutionRepository jobsExecutionRepository;

  private final JobExecutionService jobExecutionService;

  private final JobExecutionLogsUrlBuilder jobExecutionLogsUrlBuilder;

  /** Populates the executions of the specified data jobs, that match the specified criteria. */
  List<V2DataJob> populateExecutions(
      List<V2DataJob> allDataJob, DataFetchingEnvironment dataFetchingEnvironment) {
    final Map<String, Object> arguments =
        dataFetchingEnvironment
            .getSelectionSet()
            .getFields(JobFieldStrategyBy.DEPLOYMENT_EXECUTIONS.getPath())
            .get(0)
            .getArguments();
    final DataJobExecutionQueryVariables dataJobExecutionQueryVariables =
        fetchDataJobExecutionQueryVariables(arguments);
    allDataJob.forEach(
        dataJob -> {
          if (dataJob.getDeployments() != null) {
            dataJob.getDeployments().stream()
                .findFirst()
                .ifPresent(
                    deployment ->
                        deployment.setExecutions(
                            findAllExecutions(dataJobExecutionQueryVariables, dataJob.getJobName())
                                .getContent()
                                .stream()
                                .map(
                                    dataJobExecution ->
                                        ToApiModelConverter.jobExecutionToConvert(
                                            dataJobExecution,
                                            jobExecutionLogsUrlBuilder.build(dataJobExecution)))
                                .collect(Collectors.toList())));
          }
        });
    return allDataJob;
  }

  public DataFetcher<Object> findAllAndBuildResponse() {
    return environment -> {
      DataJobExecutionQueryVariables dataJobExecutionQueryVariables =
          fetchDataJobExecutionQueryVariables(environment.getArguments());

      Page<DataJobExecution> dataJobExecutionsResult =
          findAllExecutions(dataJobExecutionQueryVariables, null);
      List<com.vmware.taurus.controlplane.model.data.DataJobExecution> dataJobExecutions =
          dataJobExecutionsResult.getContent().stream()
              .map(
                  dataJobExecution ->
                      ToApiModelConverter.jobExecutionToConvert(
                          dataJobExecution, jobExecutionLogsUrlBuilder.build(dataJobExecution)))
              .collect(Collectors.toList());

      return buildResponse(
          dataJobExecutionsResult.getTotalPages(),
          (int) dataJobExecutionsResult.getTotalElements(),
          dataJobExecutions);
    };
  }

  private Page<DataJobExecution> findAllExecutions(
      DataJobExecutionQueryVariables dataJobExecutionQueryVariables, String dataJobName) {
    DataJobExecutionFilter filter =
        dataJobExecutionQueryVariables.getFilter() != null
            ? dataJobExecutionQueryVariables.getFilter()
            : DataJobExecutionFilter.builder().build();

    if (dataJobName != null && filter.getJobNameIn() != null) {
      throw new GraphQLException("The jobNameIn filter is not supported for nested executions");
    }

    if (dataJobName != null) {
      filter.setJobNameIn(List.of(dataJobName));
    }

    Specification<DataJobExecution> filterSpec = new JobExecutionFilterSpec(filter);
    Page<DataJobExecution> result;
    DataJobExecutionOrder order = dataJobExecutionQueryVariables.getOrder();
    Sort sort = order != null ? Sort.by(order.getDirection(), order.getProperty()) : null;

    if (dataJobExecutionQueryVariables.getPageNumber() != null
        && dataJobExecutionQueryVariables.getPageSize() != null) {
      PageRequest pageRequest =
          PageRequest.of(
              dataJobExecutionQueryVariables.getPageNumber() - 1,
              dataJobExecutionQueryVariables.getPageSize());
      pageRequest = sort != null ? pageRequest.withSort(sort) : pageRequest;

      result = jobsExecutionRepository.findAll(filterSpec, pageRequest);
    } else {
      List<DataJobExecution> elements =
          sort == null
              ? jobsExecutionRepository.findAll(filterSpec)
              : jobsExecutionRepository.findAll(filterSpec, sort);

      result = new PageImpl(elements);
    }

    return result;
  }

  private static DataJobExecutionQueryVariables fetchDataJobExecutionQueryVariables(
      Map<String, Object> arguments) {
    DataJobExecutionQueryVariables queryVariables = new DataJobExecutionQueryVariables();

    Optional<ImmutablePair<Integer, Integer>> page =
        extractDataJobExecutionPage(
            arguments.get(PAGE_NUMBER_FIELD), arguments.get(PAGE_SIZE_FIELD));

    page.ifPresent(
        pair -> {
          queryVariables.setPageNumber(pair.getLeft());
          queryVariables.setPageSize(pair.getRight());
        });

    extractDataJobExecutionFilter((Map<String, Object>) arguments.get(FILTER_FIELD))
        .ifPresent(filter -> queryVariables.setFilter(filter));

    extractDataJobExecutionOrder((Map<String, Object>) arguments.get(ORDER_FIELD))
        .ifPresent(order -> queryVariables.setOrder(order));

    return queryVariables;
  }

  private static Optional<ImmutablePair<Integer, Integer>> extractDataJobExecutionPage(
      Object pageNumberRaw, Object pageSizeRaw) {
    Optional<ImmutablePair<Integer, Integer>> result = Optional.empty();

    if (pageNumberRaw != null && pageSizeRaw == null) {
      throw new GraphQLException(
          String.format("Executions field must contain %s", PAGE_SIZE_FIELD));
    }

    if (pageNumberRaw == null && pageSizeRaw != null) {
      throw new GraphQLException(
          String.format("Executions field must contain %s", PAGE_NUMBER_FIELD));
    }

    if (pageNumberRaw != null && pageSizeRaw != null) {
      Integer pageNumber = (Integer) pageNumberRaw;
      Integer pageSize = (Integer) pageSizeRaw;
      GraphQLUtils.validatePageInput(pageSize, pageNumber);
      result = Optional.of(ImmutablePair.of(pageNumber, pageSize));
    }

    return result;
  }

  private static Optional<DataJobExecutionFilter> extractDataJobExecutionFilter(
      Map<String, Object> filterRaw) {
    Optional<DataJobExecutionFilter> filter = Optional.empty();

    if (filterRaw != null) {
      DataJobExecutionFilter.DataJobExecutionFilterBuilder builder =
          DataJobExecutionFilter.builder();

      builder.statusIn(
          Optional.ofNullable(filterRaw.get(DataJobExecutionFilter.STATUS_IN_FIELD))
              .map(statusInRaw -> ((List<String>) statusInRaw))
              .stream()
              .flatMap(v1Jobs -> v1Jobs.stream())
              .filter(Objects::nonNull)
              .map(
                  status ->
                      com.vmware.taurus.controlplane.model.data.DataJobExecution.StatusEnum
                          .fromValue(status.toLowerCase()))
              .map(statusEnum -> ToModelApiConverter.toExecutionStatus(statusEnum))
              .collect(Collectors.toList()));

      filter =
          Optional.of(
              builder
                  .startTimeGte(
                      (OffsetDateTime) filterRaw.get(DataJobExecutionFilter.START_TIME_GTE_FIELD))
                  .endTimeGte(
                      (OffsetDateTime) filterRaw.get(DataJobExecutionFilter.END_TIME_GTE_FIELD))
                  .startTimeLte(
                      (OffsetDateTime) filterRaw.get(DataJobExecutionFilter.START_TIME_LTE_FIELD))
                  .endTimeLte(
                      (OffsetDateTime) filterRaw.get(DataJobExecutionFilter.END_TIME_LTE_FIELD))
                  .jobNameIn((List<String>) filterRaw.get(DataJobExecutionFilter.JOB_NAME_IN_FIELD))
                  .teamNameIn(
                      (List<String>) filterRaw.get(DataJobExecutionFilter.TEAM_NAME_IN_FIELD))
                  .build());
    }

    return filter;
  }

  private static Optional<DataJobExecutionOrder> extractDataJobExecutionOrder(
      Map<String, Object> orderRaw) {
    Optional<DataJobExecutionOrder> order = Optional.empty();

    if (orderRaw != null) {
      DataJobExecutionOrder.DataJobExecutionOrderBuilder builder = DataJobExecutionOrder.builder();

      builder.property(
          Optional.ofNullable(orderRaw.get(PROPERTY_FIELD))
              .map(o -> (String) o)
              .filter(p -> AVAILABLE_PROPERTIES.contains(p))
              .map(
                  p ->
                      PUBLIC_NAME_TO_DB_ENTITY_MAP.getOrDefault(
                          p, p)) // If no mapping present use user provided property name
              .orElseThrow(
                  () ->
                      new GraphQLException(
                          String.format(
                              "%s.%s must be in [%s]",
                              ORDER_FIELD,
                              PROPERTY_FIELD,
                              StringUtils.join(AVAILABLE_PROPERTIES, ",")))));

      builder.direction(
          Optional.ofNullable(orderRaw.get(DIRECTION_FIELD))
              .map(o -> Sort.Direction.fromString((String) o))
              .orElseThrow(
                  () ->
                      new GraphQLException(
                          String.format(
                              "Executions field must contain %s.%s",
                              ORDER_FIELD, DIRECTION_FIELD))));

      order = Optional.of(builder.build());
    }

    return order;
  }

  private static DataJobPage buildResponse(int pageSize, int count, List pageList) {

    return DataJobPage.builder()
        .content(new ArrayList<>(pageList))
        .totalPages(pageSize)
        .totalItems(count)
        .build();
  }

  List<V2DataJob> populateStatusCounts(
      List<V2DataJob> dataJobs, DataFetchingEnvironment dataFetchingEnvironment) {

    List<ExecutionStatus> statusesToCount = determineStatusesToCount(dataFetchingEnvironment);
    List<String> jobsList =
        dataJobs.stream().map(V2DataJob::getJobName).collect(Collectors.toList());
    Map<String, Map<ExecutionStatus, Integer>> statusCountMap =
        jobExecutionService.countExecutionStatuses(jobsList, statusesToCount);

    dataJobs.stream()
        .forEach(
            job -> {
              if (job.getDeployments() != null) {
                job.getDeployments().stream()
                    .findFirst()
                    .ifPresent(
                        deployment -> {
                          setStatusCounts(statusCountMap, job, dataFetchingEnvironment, deployment);
                        });
              }
            });
    return dataJobs;
  }

  private void setStatusCounts(
      Map<String, Map<ExecutionStatus, Integer>> response,
      V2DataJob job,
      DataFetchingEnvironment dataFetchingEnvironment,
      V2DataJobDeployment v2DataJobDeployment) {

    DataFetchingFieldSelectionSet selectionSet = dataFetchingEnvironment.getSelectionSet();
    Map<ExecutionStatus, Integer> statusCountsPerJob =
        response.getOrDefault(job.getJobName(), Map.of());

    if (selectionSet.contains(JobFieldStrategyBy.DEPLOYMENT_FAILED_EXECUTIONS.getPath())) {
      int failedExecutions =
          statusCountsPerJob.getOrDefault(ExecutionStatus.USER_ERROR, 0)
              + statusCountsPerJob.getOrDefault(ExecutionStatus.PLATFORM_ERROR, 0);
      v2DataJobDeployment.setFailedExecutions(failedExecutions);
    }
    if (selectionSet.contains(JobFieldStrategyBy.DEPLOYMENT_SUCCESSFUL_EXECUTIONS.getPath())) {
      v2DataJobDeployment.setSuccessfulExecutions(
          statusCountsPerJob.getOrDefault(ExecutionStatus.SUCCEEDED, 0));
    }
  }

  private List<ExecutionStatus> determineStatusesToCount(
      DataFetchingEnvironment dataFetchingEnvironment) {
    DataFetchingFieldSelectionSet selectionSet = dataFetchingEnvironment.getSelectionSet();
    List<ExecutionStatus> statusesToCount = new ArrayList<>();

    if (selectionSet.contains(JobFieldStrategyBy.DEPLOYMENT_FAILED_EXECUTIONS.getPath())) {
      statusesToCount.add(ExecutionStatus.USER_ERROR);
      statusesToCount.add(ExecutionStatus.PLATFORM_ERROR);
    }
    if (selectionSet.contains(JobFieldStrategyBy.DEPLOYMENT_SUCCESSFUL_EXECUTIONS.getPath())) {
      statusesToCount.add(ExecutionStatus.SUCCEEDED);
    }

    return statusesToCount;
  }
}
