/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.graphql.strategy;

import com.vmware.taurus.service.graphql.model.V2DataJob;
import com.vmware.taurus.service.graphql.strategy.datajob.JobFieldStrategyBy;
import com.vmware.taurus.service.graphql.strategy.datajob.JobFieldStrategyByDescription;
import com.vmware.taurus.service.graphql.strategy.datajob.JobFieldStrategyByName;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.springframework.test.context.junit.jupiter.SpringExtension;

import java.util.HashSet;
import java.util.Map;
import java.util.Set;

import static org.assertj.core.api.Assertions.assertThat;

@ExtendWith(SpringExtension.class)
class JobFieldStrategyFactoryTest {

  private final JobFieldStrategyByName jobFieldStrategyByName = new JobFieldStrategyByName();
  private final JobFieldStrategyByDescription jobFieldStrategyByDescription =
      new JobFieldStrategyByDescription();
  private final Set<FieldStrategy<V2DataJob>> strategies = new HashSet<>();

  @BeforeEach
  public void beforeEach() {
    strategies.add(jobFieldStrategyByName);
    strategies.add(jobFieldStrategyByDescription);
  }

  @Test
  void testStrategies_whenSearchingForValidStrategy_shouldReturnValidStrategy() {
    JobFieldStrategyFactory factory = new JobFieldStrategyFactory(strategies);

    FieldStrategy<V2DataJob> strategy =
        factory.findStrategy(jobFieldStrategyByDescription.getStrategyName());

    assertThat(strategy).isEqualTo(jobFieldStrategyByDescription);
  }

  @Test
  void testStrategies_whenGettingAllStrategies_shouldReturnStrategiesMap() {
    JobFieldStrategyFactory factory = new JobFieldStrategyFactory(strategies);

    Map<JobFieldStrategyBy, FieldStrategy<V2DataJob>> strategyMap = factory.getStrategies();

    assertThat(strategyMap)
        .hasSize(2)
        .containsKey(jobFieldStrategyByName.getStrategyName())
        .containsKey(jobFieldStrategyByDescription.getStrategyName());
  }
}
