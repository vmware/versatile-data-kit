/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.graphql.strategy.datajob;

import com.vmware.taurus.controlplane.model.data.DataJobExecution;
import com.vmware.taurus.service.graphql.model.Criteria;
import com.vmware.taurus.service.graphql.model.Filter;
import com.vmware.taurus.service.graphql.model.V2DataJob;
import com.vmware.taurus.service.graphql.strategy.FieldStrategy;
import org.springframework.lang.NonNull;
import org.springframework.stereotype.Component;
import org.springframework.util.CollectionUtils;

import java.util.Comparator;
import java.util.function.Predicate;

@Component
public class JobFieldStrategyByLastExecutionStatus extends FieldStrategy<V2DataJob> {

  private static final Comparator<V2DataJob> COMPARATOR_DEFAULT =
      Comparator.comparing(
          JobFieldStrategyByLastExecutionStatus::getLastExecutionStatusAsString,
          Comparator.nullsFirst(Comparator.naturalOrder()));

  @Override
  public JobFieldStrategyBy getStrategyName() {
    return JobFieldStrategyBy.DEPLOYMENT_LAST_EXECUTION_STATUS;
  }

  @Override
  public Criteria<V2DataJob> computeFilterCriteria(
      @NonNull Criteria<V2DataJob> criteria, @NonNull Filter filter) {
    Predicate<V2DataJob> predicate = criteria.getPredicate();

    if (filterProvided(filter)) {
      predicate = predicate.and(computeSearchCriteria(filter.getPattern()));
    }

    return new Criteria<>(predicate, detectSortingComparator(filter, COMPARATOR_DEFAULT, criteria));
  }

  @Override
  public Predicate<V2DataJob> computeSearchCriteria(@NonNull String searchStr) {
    try {
      DataJobExecution.StatusEnum executionStatus =
          DataJobExecution.StatusEnum.fromValue(searchStr);
      return dataJob -> executionStatus.equals(getLastExecutionStatus(dataJob));
    } catch (IllegalArgumentException e) {
      // searching with non-compatible for the strategy string, ignoring search
      return x -> false;
    }
  }

  private static DataJobExecution.StatusEnum getLastExecutionStatus(V2DataJob dataJob) {
    if (CollectionUtils.isEmpty(dataJob.getDeployments())) {
      return null;
    }
    // TODO support for multiple deployments
    return dataJob.getDeployments().stream().findFirst().orElseThrow().getLastExecutionStatus();
  }

  private static String getLastExecutionStatusAsString(V2DataJob dataJob) {
    DataJobExecution.StatusEnum lastExecutionStatus = getLastExecutionStatus(dataJob);
    if (lastExecutionStatus == null) {
      return null;
    }
    return lastExecutionStatus.getValue();
  }
}
