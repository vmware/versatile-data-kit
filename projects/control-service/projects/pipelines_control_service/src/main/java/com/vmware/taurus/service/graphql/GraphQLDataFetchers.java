/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.graphql;

import com.vmware.taurus.controlplane.model.data.DataJobResources;
import com.vmware.taurus.datajobs.ToApiModelConverter;
import com.vmware.taurus.service.model.ActualDataJobDeployment;
import com.vmware.taurus.service.model.DataJobDeploymentResources;
import com.vmware.taurus.service.repository.JobsRepository;
import com.vmware.taurus.service.repository.ActualJobDeploymentRepository;
import com.vmware.taurus.service.deploy.DataJobDeploymentPropertiesConfig;
import com.vmware.taurus.service.deploy.DataJobDeploymentPropertiesConfig.ReadFrom;
import com.vmware.taurus.service.deploy.DeploymentService;
import com.vmware.taurus.service.graphql.model.Criteria;
import com.vmware.taurus.service.graphql.model.DataJobPage;
import com.vmware.taurus.service.graphql.model.DataJobQueryVariables;
import com.vmware.taurus.service.graphql.model.Filter;
import com.vmware.taurus.service.graphql.model.V2DataJob;
import com.vmware.taurus.service.graphql.strategy.FieldStrategy;
import com.vmware.taurus.service.graphql.strategy.JobFieldStrategyFactory;
import com.vmware.taurus.service.graphql.strategy.datajob.JobFieldStrategyBy;
import com.vmware.taurus.service.model.DataJob;
import com.vmware.taurus.service.model.JobDeploymentStatus;
import graphql.GraphqlErrorException;
import graphql.schema.DataFetcher;
import graphql.schema.DataFetchingEnvironment;
import graphql.schema.DataFetchingFieldSelectionSet;
import lombok.AllArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicReference;
import java.util.function.Predicate;
import java.util.stream.Collectors;
import java.util.stream.StreamSupport;

@Slf4j
@Component
@AllArgsConstructor
public class GraphQLDataFetchers {

  private static final Criteria<V2DataJob> JOB_CRITERIA_DEFAULT =
      new Criteria<>(Objects::nonNull, Comparator.comparing(V2DataJob::getJobName));

  private final JobFieldStrategyFactory strategyFactory;
  private final JobsRepository jobsRepository;
  private final DeploymentService deploymentService;
  private final ExecutionDataFetcher executionDataFetcher;
  private final ActualJobDeploymentRepository actualJobDeploymentRepository;
  private final DataJobDeploymentPropertiesConfig dataJobDeploymentPropertiesConfig;

  public DataFetcher<Object> findAllAndBuildDataJobPage() {
    return dataFetchingEnvironment -> {
      DataJobQueryVariables queryVar = fetchDataJobQueryVariables(dataFetchingEnvironment);
      var dataJobs =
          StreamSupport.stream(jobsRepository.findAll().spliterator(), false)
              .collect(Collectors.toMap(DataJob::getName, job -> job));
      List<V2DataJob> allDataJob =
          dataJobs.values().stream()
              .map(ToApiModelConverter::toV2DataJob)
              .collect(Collectors.toList());

      final Criteria<V2DataJob> filterCriteria = populateCriteria(queryVar.getFilters());
      List<V2DataJob> dataJobsFiltered =
          populateDataJobsByRequestedFields(dataFetchingEnvironment, allDataJob, dataJobs).stream()
              .filter(filterCriteria.getPredicate())
              .filter(
                  computeSearch(dataFetchingEnvironment.getSelectionSet(), queryVar.getSearch()))
              .sorted(filterCriteria.getComparator())
              .collect(Collectors.toList());

      int count = dataJobsFiltered.size();

      List<V2DataJob> dataJobList =
          dataJobsFiltered.stream()
              .skip((long) (queryVar.getPageNumber() - 1) * queryVar.getPageSize())
              .limit(queryVar.getPageSize())
              .collect(Collectors.toList());

      List<V2DataJob> resultList =
          populateDataJobsPostPagination(dataJobList, dataFetchingEnvironment);

      return buildResponse(queryVar.getPageSize(), count, resultList);
    };
  }

  private List<V2DataJob> populateDataJobsPostPagination(
      List<V2DataJob> allDataJob, DataFetchingEnvironment dataFetchingEnvironment) {
    if (dataFetchingEnvironment
        .getSelectionSet()
        .contains(JobFieldStrategyBy.DEPLOYMENT_EXECUTIONS.getPath())) {
      executionDataFetcher.populateExecutions(allDataJob, dataFetchingEnvironment);
    }

    if (dataFetchingEnvironment
            .getSelectionSet()
            .contains(JobFieldStrategyBy.DEPLOYMENT_FAILED_EXECUTIONS.getPath())
        || dataFetchingEnvironment
            .getSelectionSet()
            .contains(JobFieldStrategyBy.DEPLOYMENT_SUCCESSFUL_EXECUTIONS.getPath())) {
      executionDataFetcher.populateStatusCounts(allDataJob, dataFetchingEnvironment);
    }

    return allDataJob;
  }

  private DataJobQueryVariables fetchDataJobQueryVariables(
      DataFetchingEnvironment dataFetchingEnvironment) {
    DataJobQueryVariables queryVariables = new DataJobQueryVariables();

    queryVariables.setPageNumber(dataFetchingEnvironment.getArgument("pageNumber"));
    queryVariables.setPageSize(dataFetchingEnvironment.getArgument("pageSize"));
    GraphQLUtils.validatePageInput(queryVariables.getPageSize(), queryVariables.getPageNumber());
    queryVariables.setSearch(dataFetchingEnvironment.getArgument("search"));
    queryVariables.setFilters(
        GraphQLUtils.convertFilters(dataFetchingEnvironment.getArgument("filter")));

    return queryVariables;
  }

  /**
   * Alter each data job in order to populate fields that are requested from the GraphQL body
   *
   * @param dataFetchingEnvironment Environment holder of the graphql requests
   * @param allDataJob List of the data jobs which will be altered
   * @return Altered data job list
   */
  private List<V2DataJob> populateDataJobsByRequestedFields(
      DataFetchingEnvironment dataFetchingEnvironment,
      List<V2DataJob> allDataJob,
      Map<String, DataJob> dataJobs) {
    DataFetchingFieldSelectionSet requestedFields = dataFetchingEnvironment.getSelectionSet();
    if (requestedFields.contains(JobFieldStrategyBy.DEPLOYMENT.getPath())) {
      populateDeployments(allDataJob, dataJobs);
    }

    allDataJob.forEach(
        dataJob ->
            strategyFactory.getStrategies().entrySet().stream()
                .filter(strategy -> requestedFields.contains(strategy.getKey().getPath()))
                .forEach(strategy -> strategy.getValue().alterFieldData(dataJob)));

    return allDataJob;
  }

  private Criteria<V2DataJob> populateCriteria(List<Filter> filterList) {
    // concurrent result, calculation might be using Fork-Join API to speed-up
    final AtomicReference<Criteria<V2DataJob>> criteriaResult =
        new AtomicReference<>(JOB_CRITERIA_DEFAULT);

    // handle non-supported or invalid filter(s)
    final Optional<Filter> filterNotSupported =
        filterList.stream()
            .filter(
                e ->
                    e.getProperty() == null
                        || (e.getPattern() == null && e.getSort() == null)
                        || JobFieldStrategyBy.field(e.getProperty()) == null)
            .findAny(); // or all
    if (filterNotSupported.isPresent()) {
      throw GraphqlErrorException.newErrorException()
          .message(
              "Provided filter for "
                  + filterNotSupported.get().getProperty()
                  + " is either not valid or currently not supported")
          .build();
    }

    // populate filter strategies
    final Map<Filter, FieldStrategy<V2DataJob>> filterStrategyMap =
        filterList.stream()
            .collect(
                Collectors.toMap(
                    f -> f,
                    filter ->
                        strategyFactory.findStrategy(
                            JobFieldStrategyBy.field(filter.getProperty()))));

    // compute criteria
    filterStrategyMap.forEach(
        (key, value) -> criteriaResult.getAndUpdate(c -> value.computeFilterCriteria(c, key)));
    return criteriaResult.get();
  }

  private Predicate<V2DataJob> computeSearch(
      DataFetchingFieldSelectionSet requestedFields, String search) {
    Predicate<V2DataJob> predicate = null;
    if (search != null && !search.isBlank()) {
      for (Map.Entry<JobFieldStrategyBy, FieldStrategy<V2DataJob>> entry :
          strategyFactory.getStrategies().entrySet()) {
        JobFieldStrategyBy strategyName = entry.getKey();
        FieldStrategy<V2DataJob> strategy = entry.getValue();

        if (requestedFields.contains(strategyName.getPath())) {
          predicate =
              (predicate == null)
                  ? strategy.computeSearchCriteria(search)
                  : predicate.or(strategy.computeSearchCriteria(search));
        }
      }
    }
    return predicate == null ? Objects::nonNull : predicate;
  }

  private List<V2DataJob> populateDeployments(
      List<V2DataJob> allDataJob, Map<String, DataJob> dataJobs) {
    Map<String, JobDeploymentStatus> deploymentStatuses =
        (dataJobDeploymentPropertiesConfig.getReadDataSource().equals(ReadFrom.DB))
            ? readJobDeploymentsFromDb()
            : readJobDeploymentsFromK8s();

    allDataJob.forEach(
        dataJob -> {
          var jobDeploymentStatus = deploymentStatuses.get(dataJob.getJobName());
          if (jobDeploymentStatus != null) {
            // TODO add multiple deployments when its supported
            var sourceDataJob = dataJobs.get(dataJob.getJobName());
            if (sourceDataJob == null) {
              log.warn("Data job {} not found when populating deployments", dataJob.getJobName());
            }
            dataJob.setDeployments(
                Collections.singletonList(
                    ToApiModelConverter.toV2DataJobDeployment(jobDeploymentStatus, sourceDataJob)));
          }
        });
    return allDataJob;
  }

  private Map<String, JobDeploymentStatus> readJobDeploymentsFromK8s() {
    return deploymentService.readDeployments().stream()
        .collect(Collectors.toMap(JobDeploymentStatus::getDataJobName, cronJob -> cronJob));
  }

  private Map<String, JobDeploymentStatus> readJobDeploymentsFromDb() {
    var deployments =
        StreamSupport.stream(actualJobDeploymentRepository.findAll().spliterator(), false)
            .collect(Collectors.toMap(ActualDataJobDeployment::getDataJobName, cronjob -> cronjob));

    return deployments.entrySet().stream()
        .collect(
            Collectors.toMap(
                Map.Entry::getKey, entry -> convertToJobDeploymentStatus(entry.getValue())));
  }

  private JobDeploymentStatus convertToJobDeploymentStatus(
      ActualDataJobDeployment deploymentStatus) {
    JobDeploymentStatus jobDeploymentStatus = new JobDeploymentStatus();
    jobDeploymentStatus.setDataJobName(deploymentStatus.getDataJobName());
    jobDeploymentStatus.setPythonVersion(deploymentStatus.getPythonVersion());
    jobDeploymentStatus.setGitCommitSha(deploymentStatus.getGitCommitSha());
    jobDeploymentStatus.setEnabled(deploymentStatus.getEnabled());
    jobDeploymentStatus.setLastDeployedBy(deploymentStatus.getLastDeployedBy());
    jobDeploymentStatus.setLastDeployedDate(deploymentStatus.getLastDeployedDate().toString());
    jobDeploymentStatus.setResources(getDataJobResources(deploymentStatus.getResources()));
    // The ActualDataJobDeployment does not have a mode attribute, which is required by the
    // JobDeploymentStatus,
    // so we need to set something in order to avoid errors.
    jobDeploymentStatus.setMode("release");

    return jobDeploymentStatus;
  }

  private DataJobResources getDataJobResources(DataJobDeploymentResources deploymentResources) {
    DataJobResources resources = new DataJobResources();
    resources.setCpuLimit(deploymentResources.getCpuLimitCores());
    resources.setCpuRequest(deploymentResources.getCpuRequestCores());
    resources.setMemoryLimit(deploymentResources.getMemoryLimitMi());
    resources.setMemoryRequest(deploymentResources.getMemoryRequestMi());
    return resources;
  }

  private static DataJobPage buildResponse(int pageSize, int count, List pageList) {

    return DataJobPage.builder()
        .content(new ArrayList<>(pageList))
        .totalPages(((count - 1) / pageSize + 1))
        .totalItems(count)
        .build();
  }
}
