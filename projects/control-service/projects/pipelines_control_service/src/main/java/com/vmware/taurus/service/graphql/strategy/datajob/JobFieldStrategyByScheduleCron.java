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
import com.vmware.taurus.service.graphql.model.V2DataJob;
import com.vmware.taurus.service.graphql.strategy.FieldStrategy;
import com.vmware.taurus.service.graphql.model.Filter;
import org.apache.commons.lang3.StringUtils;
import org.springframework.lang.NonNull;
import org.springframework.stereotype.Component;

import java.util.function.Predicate;

@Component
public class JobFieldStrategyByScheduleCron extends FieldStrategy<V2DataJob> {

  @Override
  public JobFieldStrategyBy getStrategyName() {
    return JobFieldStrategyBy.SCHEDULE_CRON;
  }

  /** Filtering and sorting by schedule is not meaningful */
  @Override
  public Criteria<V2DataJob> computeFilterCriteria(
      @NonNull Criteria<V2DataJob> criteria, @NonNull Filter filter) {
    return criteria;
  }

  @Override
  public Predicate<V2DataJob> computeSearchCriteria(@NonNull String searchStr) {
    return dataJob ->
        dataJob.getConfig() != null
            && dataJob.getConfig().getSchedule() != null
            && StringUtils.containsIgnoreCase(
                dataJob.getConfig().getSchedule().getScheduleCron(), searchStr);
  }
}
