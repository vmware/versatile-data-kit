/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.graphql.strategy.datajob;

import com.vmware.taurus.service.graphql.model.Criteria;
import com.vmware.taurus.service.graphql.model.Filter;
import com.vmware.taurus.service.graphql.model.V2DataJob;
import com.vmware.taurus.service.graphql.model.V2DataJobConfig;
import com.vmware.taurus.service.graphql.strategy.FieldStrategy;
import java.util.Comparator;
import java.util.function.Predicate;
import org.apache.commons.lang3.StringUtils;
import org.springframework.lang.NonNull;
import org.springframework.stereotype.Component;

@Component
public class JobFieldStrategyByTeam extends FieldStrategy<V2DataJob> {

  private static final Comparator<V2DataJob> COMPARATOR_DEFAULT =
      Comparator.comparing(
          e -> e.getConfig().getTeam(), Comparator.nullsLast(Comparator.naturalOrder()));

  @Override
  public Criteria<V2DataJob> computeFilterCriteria(
      @NonNull Criteria<V2DataJob> criteria, @NonNull Filter filter) {
    Predicate<V2DataJob> predicate = criteria.getPredicate();

    if (filterProvided(filter)) {
      predicate =
          predicate.and(
              dataJob -> {
                V2DataJobConfig config = dataJob.getConfig();
                if (config == null || config.getTeam() == null) {
                  return false;
                }

                // Only the team field currently support the 'equals' and 'like' operator
                String part = filter.getPattern();
                part = part.replace("%", ".*").trim();
                var configTeamLower = config.getTeam().toLowerCase();
                var partLower = part.toLowerCase();
                return configTeamLower.matches(partLower)
                    || configTeamLower.trim().equals(partLower.trim());
              });
    }

    return new Criteria<>(predicate, detectSortingComparator(filter, COMPARATOR_DEFAULT, criteria));
  }

  @Override
  public Predicate<V2DataJob> computeSearchCriteria(@NonNull String searchStr) {
    return dataJob ->
        dataJob.getConfig() != null
            && StringUtils.containsIgnoreCase(dataJob.getConfig().getTeam(), searchStr);
  }

  @Override
  public JobFieldStrategyBy getStrategyName() {
    return JobFieldStrategyBy.TEAM;
  }
}
