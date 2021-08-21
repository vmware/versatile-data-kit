/*
 * Copyright (c) 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.graphql;

import com.vmware.taurus.datajobs.ToApiModelConverter;
import com.vmware.taurus.service.JobsRepository;
import com.vmware.taurus.service.deploy.DeploymentService;
import com.vmware.taurus.service.graphql.model.Criteria;
import com.vmware.taurus.service.graphql.model.DataJobQueryVariables;
import com.vmware.taurus.service.graphql.model.Filter;
import com.vmware.taurus.service.graphql.model.V2DataJob;
import com.vmware.taurus.service.graphql.strategy.FieldStrategy;
import com.vmware.taurus.service.graphql.strategy.JobFieldStrategyFactory;
import com.vmware.taurus.service.graphql.strategy.datajob.JobFieldStrategyBy;
import com.vmware.taurus.service.model.DataJobPage;
import com.vmware.taurus.service.model.JobDeploymentStatus;
import graphql.GraphqlErrorException;
import graphql.schema.DataFetcher;
import graphql.schema.DataFetchingEnvironment;
import graphql.schema.DataFetchingFieldSelectionSet;
import lombok.AllArgsConstructor;
import org.springframework.stereotype.Component;

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

@Component
@AllArgsConstructor
public class GraphQLDataFetchers {

   private static final Criteria<V2DataJob> JOB_CRITERIA_DEFAULT =
         new Criteria<>(Objects::nonNull, Comparator.comparing(V2DataJob::getJobName));

   private final JobFieldStrategyFactory strategyFactory;
   private final JobsRepository jobsRepository;
   private final DeploymentService deploymentService;
   private final ExecutionDataFetcher executionDataFetcher;

   public DataFetcher<Object> findAllAndBuildDataJobPage() {
      return dataFetchingEnvironment -> {
         DataJobQueryVariables queryVar = fetchDataJobQueryVariables(dataFetchingEnvironment);
         List<V2DataJob> allDataJob = StreamSupport.stream(jobsRepository.findAll().spliterator(), false)
               .map(ToApiModelConverter::toV2DataJob)
               .collect(Collectors.toList());

         final Criteria<V2DataJob> filterCriteria = populateCriteria(queryVar.getFilters());
         List<V2DataJob> dataJobsFiltered = populateDataJobsByRequestedFields(dataFetchingEnvironment, allDataJob).stream()
               .filter(filterCriteria.getPredicate())
               .filter(computeSearch(dataFetchingEnvironment.getSelectionSet(), queryVar.getSearch()))
               .sorted(filterCriteria.getComparator())
               .collect(Collectors.toList());

         int count = dataJobsFiltered.size();

         List<Object> resultList = dataJobsFiltered.stream()
               .skip((long) (queryVar.getPageNumber() - 1) * queryVar.getPageSize())
               .limit(queryVar.getPageSize())
               .collect(Collectors.toList());

         return buildDataJobPage(queryVar.getPageSize(), count, resultList);
      };
   }

   private DataJobQueryVariables fetchDataJobQueryVariables(DataFetchingEnvironment dataFetchingEnvironment) {
      DataJobQueryVariables queryVariables = new DataJobQueryVariables();

      queryVariables.setPageNumber(dataFetchingEnvironment.getArgument("pageNumber"));
      queryVariables.setPageSize(dataFetchingEnvironment.getArgument("pageSize"));
      GraphQLUtils.validatePageInput(queryVariables.getPageSize(), queryVariables.getPageNumber());
      queryVariables.setSearch(dataFetchingEnvironment.getArgument("search"));
      queryVariables.setFilters(GraphQLUtils.convertFilters(dataFetchingEnvironment.getArgument("filter")));

      return queryVariables;
   }

   /**
    * Alter each data job in order to populate fields that are requested from the GraphQL body
    * @param dataFetchingEnvironment Environment holder of the graphql requests
    * @param allDataJob      List of the data jobs which will be altered
    * @return Altered data job list
    */
   private List<V2DataJob> populateDataJobsByRequestedFields(DataFetchingEnvironment dataFetchingEnvironment, List<V2DataJob> allDataJob) {
      DataFetchingFieldSelectionSet requestedFields = dataFetchingEnvironment.getSelectionSet();
      if (requestedFields.contains(JobFieldStrategyBy.DEPLOYMENT.getPath())) {
         populateDeployments(allDataJob);
      }

      if (requestedFields.contains(JobFieldStrategyBy.DEPLOYMENT_EXECUTIONS.getPath())) {
         executionDataFetcher.populateExecutions(allDataJob, dataFetchingEnvironment);
      }

      allDataJob.forEach(dataJob -> strategyFactory.getStrategies().entrySet().stream()
            .filter(strategy -> requestedFields.contains(strategy.getKey().getPath()))
            .forEach(strategy -> strategy.getValue().alterFieldData(dataJob)));

      return allDataJob;
   }

   private Criteria<V2DataJob> populateCriteria(List<Filter> filterList) {
      // concurrent result, calculation might be using Fork-Join API to speed-up
      final AtomicReference<Criteria<V2DataJob>> criteriaResult = new AtomicReference<>(JOB_CRITERIA_DEFAULT);

      // handle non-supported or invalid filter(s)
      final Optional<Filter> filterNotSupported = filterList.stream()
            .filter(e -> e.getProperty() == null || (e.getPattern() == null && e.getSort() == null) || JobFieldStrategyBy.field(e.getProperty()) == null)
            .findAny(); // or all
      if (filterNotSupported.isPresent()) {
         throw GraphqlErrorException.newErrorException()
               .message("Provided filter for " + filterNotSupported.get().getProperty() + " is either not valid or currently not supported")
               .build();
      }

      // populate filter strategies
      final Map<Filter, FieldStrategy<V2DataJob>> filterStrategyMap = filterList.stream()
            .collect(Collectors.toMap(
                  f -> f,
                  filter -> strategyFactory.findStrategy(JobFieldStrategyBy.field(filter.getProperty()))
            ));

      // compute criteria
      filterStrategyMap.forEach((key, value) -> criteriaResult.getAndUpdate(c -> value.computeFilterCriteria(c, key)));
      return criteriaResult.get();
   }

   private Predicate<V2DataJob> computeSearch(DataFetchingFieldSelectionSet requestedFields, String search) {
      Predicate<V2DataJob> predicate = null;
      if (search != null && !search.isBlank()) {
         for (Map.Entry<JobFieldStrategyBy, FieldStrategy<V2DataJob>> entry : strategyFactory.getStrategies().entrySet()) {
            JobFieldStrategyBy strategyName = entry.getKey();
            FieldStrategy<V2DataJob> strategy = entry.getValue();

            if (requestedFields.contains(strategyName.getPath())) {
               predicate = (predicate == null) ?
                     strategy.computeSearchCriteria(search) : predicate.or(strategy.computeSearchCriteria(search));
            }
         }
      }
      return predicate == null ? Objects::nonNull : predicate;
   }

   private List<V2DataJob> populateDeployments(List<V2DataJob> allDataJob) {
      Map<String, JobDeploymentStatus> deploymentStatuses = deploymentService.readDeployments()
            .stream().collect(Collectors.toMap(JobDeploymentStatus::getDataJobName, cronJob -> cronJob));

      allDataJob.forEach(dataJob -> {
         var jobDeploymentStatus = deploymentStatuses.get(dataJob.getJobName());
         if (jobDeploymentStatus != null) {
            // TODO add multiple deployments when its supported
            dataJob.setDeployments(Collections.singletonList(
                  ToApiModelConverter.toV2DataJobDeployment(jobDeploymentStatus)));
         }
      });
      return allDataJob;
   }

   private static DataJobPage buildDataJobPage(int pageSize, int count, List<Object> pageList) {
      var dataJobPage = new DataJobPage();
      dataJobPage.setContent(pageList);
      dataJobPage.setTotalPages(((count - 1) / pageSize + 1));
      dataJobPage.setTotalItems(count);
      return dataJobPage;
   }
}
