/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.graphql.strategy;

import com.vmware.taurus.service.graphql.model.V2DataJob;
import com.vmware.taurus.service.graphql.strategy.datajob.JobFieldStrategyBy;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import java.util.EnumMap;
import java.util.Map;
import java.util.Set;

@Component
public class JobFieldStrategyFactory {
  private Map<JobFieldStrategyBy, FieldStrategy<V2DataJob>> strategies;

  @Autowired
  public JobFieldStrategyFactory(Set<FieldStrategy<V2DataJob>> strategySet) {
    createStrategy(strategySet);
  }

  public FieldStrategy<V2DataJob> findStrategy(JobFieldStrategyBy strategyName) {
    return strategies.get(strategyName);
  }

  private void createStrategy(Set<FieldStrategy<V2DataJob>> strategySet) {
    strategies = new EnumMap<>(JobFieldStrategyBy.class);
    strategySet.forEach(strategy -> strategies.put(strategy.getStrategyName(), strategy));
  }

  public Map<JobFieldStrategyBy, FieldStrategy<V2DataJob>> getStrategies() {
    return new EnumMap<>(strategies);
  }
}
