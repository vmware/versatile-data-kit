/*
 * Copyright 2023-2025 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.graphql.strategy.datajob;

import com.vmware.taurus.service.graphql.model.Criteria;
import com.vmware.taurus.service.graphql.model.Filter;
import com.vmware.taurus.service.graphql.model.V2DataJob;
import com.vmware.taurus.service.graphql.strategy.FieldStrategy;
import org.apache.commons.lang3.StringUtils;
import org.springframework.lang.NonNull;
import org.springframework.stereotype.Component;

import java.util.Comparator;
import java.util.function.Predicate;

@Component
public class JobFieldStrategyByJobPythonVersion extends FieldStrategy<V2DataJob> {

  private static final Comparator<V2DataJob> COMPARATOR_DEFAULT =
      Comparator.comparing(
          e -> e.getDeployments().stream().findFirst().orElseThrow().getJobPythonVersion(),
          Comparator.nullsLast(Comparator.naturalOrder()));

  @Override
  public Criteria<V2DataJob> computeFilterCriteria(
      @NonNull Criteria<V2DataJob> criteria, @NonNull Filter filter) {
    Predicate<V2DataJob> predicate = criteria.getPredicate();

    if (filterProvided(filter)) {
      predicate =
          predicate.and(
              dataJob ->
                  dataJob.getDeployments() != null
                      && StringUtils.containsIgnoreCase(
                          dataJob.getDeployments().stream()
                              .findFirst()
                              .orElseThrow()
                              .getJobPythonVersion(),
                          filter.getPattern()));
    }

    return new Criteria<>(predicate, detectSortingComparator(filter, COMPARATOR_DEFAULT, criteria));
  }

  @Override
  public Predicate<V2DataJob> computeSearchCriteria(@NonNull String searchStr) {
    return dataJob -> {
      if (dataJob.getDeployments() == null || dataJob.getDeployments().isEmpty()) {
        return false;
      }
      return StringUtils.containsIgnoreCase(
          dataJob.getDeployments().stream().findFirst().orElseThrow().getJobPythonVersion(),
          searchStr);
    };
  }

  @Override
  public JobFieldStrategyBy getStrategyName() {
    return JobFieldStrategyBy.DEPLOYMENT_JOBPYTHONVERSION;
  }
}
