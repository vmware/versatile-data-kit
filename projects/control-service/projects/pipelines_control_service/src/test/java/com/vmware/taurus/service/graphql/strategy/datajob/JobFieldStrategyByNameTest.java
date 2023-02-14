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
import com.vmware.taurus.service.graphql.model.Filter;
import org.junit.jupiter.api.Test;
import org.springframework.data.domain.Sort;

import java.util.Comparator;
import java.util.Objects;
import java.util.function.Predicate;

import static org.assertj.core.api.Assertions.assertThat;

class JobFieldStrategyByNameTest {

  private final JobFieldStrategyByName strategyByName = new JobFieldStrategyByName();

  @Test
  void testJobNameStrategy_whenGettingStrategyName_shouldBeSpecific() {
    assertThat(strategyByName.getStrategyName()).isEqualTo(JobFieldStrategyBy.JOB_NAME);
  }

  @Test
  void testJobNameStrategy_whenAlteringFieldData_shouldNotModifyState() {
    V2DataJob dataJob = createDummyJob("B");

    strategyByName.alterFieldData(dataJob);

    assertThat(dataJob.getJobName()).isEqualTo("B");
  }

  @Test
  void testJobNameStrategy_whenComputingValidCriteriaWithoutFilter_shouldReturnValidCriteria() {
    Criteria<V2DataJob> baseCriteria =
        new Criteria<>(
            Objects::nonNull,
            Comparator.comparing(dataJob -> dataJob.getConfig().getDescription()));
    Filter baseFilter = new Filter("random", null, Sort.Direction.DESC);
    V2DataJob a = createDummyJob("A");
    V2DataJob b = createDummyJob("B");

    Criteria<V2DataJob> v2DataJobCriteria =
        strategyByName.computeFilterCriteria(baseCriteria, baseFilter);

    assertThat(v2DataJobCriteria.getPredicate().test(a)).isTrue();
    assertThat(v2DataJobCriteria.getComparator().compare(a, b)).isPositive();
  }

  @Test
  void testJobNameStrategy_whenComputingValidCriteriaWithFilter_shouldReturnValidCriteria() {
    Criteria<V2DataJob> baseCriteria =
        new Criteria<>(
            Objects::nonNull,
            Comparator.comparing(dataJob -> dataJob.getConfig().getDescription()));
    Filter baseFilter = new Filter("jobName", "A", Sort.Direction.ASC);
    V2DataJob a = createDummyJob("a");
    V2DataJob b = createDummyJob("b");

    Criteria<V2DataJob> v2DataJobCriteria =
        strategyByName.computeFilterCriteria(baseCriteria, baseFilter);

    assertThat(v2DataJobCriteria.getPredicate().test(a)).isTrue();
    assertThat(v2DataJobCriteria.getPredicate().test(b)).isFalse();
    assertThat(v2DataJobCriteria.getComparator().compare(a, b)).isNegative();
  }

  @Test
  void testJobNameStrategy_whenComputingValidSearchProvided_shouldReturnValidPredicate() {
    Predicate<V2DataJob> predicate = strategyByName.computeSearchCriteria("A");

    V2DataJob a = createDummyJob("A");
    V2DataJob b = createDummyJob("B");

    assertThat(predicate.test(a)).isTrue();
    assertThat(predicate.test(b)).isFalse();
  }

  @Test
  void testJobNameStrategy_whenComputingInvalidSearchProvided_shouldReturnValidPredicate() {
    Predicate<V2DataJob> predicate = strategyByName.computeSearchCriteria("A");

    V2DataJob a = new V2DataJob();

    assertThat(predicate.test(a)).isFalse();
  }

  private V2DataJob createDummyJob(String jobName) {
    V2DataJob job = new V2DataJob();
    job.setJobName(jobName);

    return job;
  }
}
