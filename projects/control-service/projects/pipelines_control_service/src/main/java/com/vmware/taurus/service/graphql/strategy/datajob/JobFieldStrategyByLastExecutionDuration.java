/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.graphql.strategy.datajob;

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
public class JobFieldStrategyByLastExecutionDuration extends FieldStrategy<V2DataJob> {

  private static final Comparator<V2DataJob> COMPARATOR_DEFAULT =
      Comparator.comparing(
          JobFieldStrategyByLastExecutionDuration::getLastExecutionDuration,
          Comparator.nullsFirst(Comparator.naturalOrder()));

  @Override
  public JobFieldStrategyBy getStrategyName() {
    return JobFieldStrategyBy.DEPLOYMENT_LAST_EXECUTION_DURATION;
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
    return dataJob -> false;
  }

  private static Integer getLastExecutionDuration(V2DataJob dataJob) {
    if (CollectionUtils.isEmpty(dataJob.getDeployments())) {
      return null;
    }
    // TODO support for multiple deployments
    return dataJob.getDeployments().stream().findFirst().orElseThrow().getLastExecutionDuration();
  }
}
