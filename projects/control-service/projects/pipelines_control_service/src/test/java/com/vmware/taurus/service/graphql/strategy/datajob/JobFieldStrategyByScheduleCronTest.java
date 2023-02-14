/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.graphql.strategy.datajob;

import com.vmware.taurus.service.graphql.model.Criteria;
import com.vmware.taurus.service.graphql.model.V2DataJob;
import com.vmware.taurus.service.graphql.model.V2DataJobConfig;
import com.vmware.taurus.service.graphql.model.V2DataJobSchedule;
import org.junit.jupiter.api.Test;

import java.util.Comparator;
import java.util.Objects;
import java.util.function.Predicate;

import static org.assertj.core.api.Assertions.assertThat;

class JobFieldStrategyByScheduleCronTest {

  private final JobFieldStrategyByScheduleCron strategyBySchedule =
      new JobFieldStrategyByScheduleCron();

  @Test
  void testJobScheduleStrategy_whenGettingStrategyName_shouldBeSpecific() {
    assertThat(strategyBySchedule.getStrategyName()).isEqualTo(JobFieldStrategyBy.SCHEDULE_CRON);
  }

  @Test
  void testJobScheduleStrategy_whenAlteringFieldData_shouldNotModifyState() {
    String cron = "5 0 * 8 *";
    V2DataJob dataJob = createDummyJob(cron);

    strategyBySchedule.alterFieldData(dataJob);

    assertThat(dataJob.getConfig().getSchedule().getScheduleCron()).isEqualTo(cron);
  }

  @Test
  void
      testJobScheduleStrategy_whenComputingValidCriteriaWithoutFilter_shouldReturnTheSameCriteria() {
    Criteria<V2DataJob> baseCriteria =
        new Criteria<>(
            Objects::nonNull,
            Comparator.comparing(dataJob -> dataJob.getConfig().getDescription()));

    Criteria<V2DataJob> v2DataJobCriteria =
        strategyBySchedule.computeFilterCriteria(baseCriteria, null);

    assertThat(v2DataJobCriteria.getPredicate()).isEqualTo(baseCriteria.getPredicate());
    assertThat(v2DataJobCriteria.getComparator()).isEqualTo(baseCriteria.getComparator());
  }

  @Test
  void testJobScheduleStrategy_whenComputingValidSearchProvided_shouldReturnValidPredicate() {
    Predicate<V2DataJob> predicate = strategyBySchedule.computeSearchCriteria("5 0 * 8 *");

    V2DataJob a = createDummyJob("5 0 * 8 *");
    V2DataJob b = createDummyJob("5 0 * 8 1");

    assertThat(predicate.test(a)).isTrue();
    assertThat(predicate.test(b)).isFalse();
  }

  private V2DataJob createDummyJob(String schedule) {
    V2DataJob job = new V2DataJob();
    V2DataJobConfig config = new V2DataJobConfig();
    V2DataJobSchedule dataJobSchedule = new V2DataJobSchedule();

    dataJobSchedule.setScheduleCron(schedule);
    config.setSchedule(dataJobSchedule);
    job.setConfig(config);
    return job;
  }
}
