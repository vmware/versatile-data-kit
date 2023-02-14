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
import com.vmware.taurus.service.graphql.model.V2DataJobConfig;
import com.vmware.taurus.service.graphql.model.Filter;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.springframework.data.domain.Sort;

import java.util.Comparator;
import java.util.Objects;
import java.util.function.Predicate;

import static org.assertj.core.api.Assertions.assertThat;

class JobFieldStrategyByDescriptionTest {

  private final JobFieldStrategyByDescription strategyByDescription =
      new JobFieldStrategyByDescription();

  @Test
  void testJobDescriptionStrategy_whenGettingStrategyName_shouldBeSpecific() {
    assertThat(strategyByDescription.getStrategyName()).isEqualTo(JobFieldStrategyBy.DESCRIPTION);
  }

  @Test
  void testJobDescriptionStrategy_whenAlteringFieldData_shouldNotModifyState() {
    V2DataJob dataJob = createDummyJob("B");

    strategyByDescription.alterFieldData(dataJob);

    assertThat(dataJob.getConfig().getDescription()).isEqualTo("B");
  }

  @Test
  void
      testJobDescriptionStrategy_whenComputingValidCriteriaWithoutFilter_shouldReturnValidCriteria() {
    Criteria<V2DataJob> baseCriteria =
        new Criteria<>(Objects::nonNull, Comparator.comparing(V2DataJob::getJobName));
    Filter baseFilter = new Filter("random", null, Sort.Direction.DESC);
    V2DataJob a = createDummyJob("A");
    V2DataJob b = createDummyJob("B");

    Criteria<V2DataJob> v2DataJobCriteria =
        strategyByDescription.computeFilterCriteria(baseCriteria, baseFilter);

    assertThat(v2DataJobCriteria.getPredicate().test(a)).isTrue();
    assertThat(v2DataJobCriteria.getComparator().compare(a, b)).isPositive();
  }

  @Test
  void testJobDescriptionStrategy_whenComputingValidCriteriaWithFilter_shouldReturnValidCriteria() {
    Criteria<V2DataJob> baseCriteria =
        new Criteria<>(Objects::nonNull, Comparator.comparing(V2DataJob::getJobName));
    Filter baseFilter = new Filter("description", "A", Sort.Direction.ASC);
    V2DataJob a = createDummyJob("a");
    V2DataJob b = createDummyJob("b");

    Criteria<V2DataJob> v2DataJobCriteria =
        strategyByDescription.computeFilterCriteria(baseCriteria, baseFilter);

    assertThat(v2DataJobCriteria.getPredicate().test(a)).isTrue();
    assertThat(v2DataJobCriteria.getPredicate().test(b)).isFalse();
    assertThat(v2DataJobCriteria.getComparator().compare(a, b)).isNegative();
  }

  @Test
  void testJobDescriptionStrategy_whenComputingValidSearchProvided_shouldReturnValidPredicate() {
    Predicate<V2DataJob> predicate = strategyByDescription.computeSearchCriteria("A");

    V2DataJob a = createDummyJob("A");
    V2DataJob b = createDummyJob("B");

    assertThat(predicate.test(a)).isTrue();
    assertThat(predicate.test(b)).isFalse();
  }

  @Test
  void testJobDescriptionStrategy_whenComputingInvalidSearchProvided_shouldReturnValidPredicate() {
    Predicate<V2DataJob> predicate = strategyByDescription.computeSearchCriteria("A");

    V2DataJob a = new V2DataJob();

    assertThat(predicate.test(a)).isFalse();
  }

  @Test
  public void testJobDescriptionComparator() {

    V2DataJob a = createDummyJob("A");
    V2DataJob a1 = createDummyJob("A");
    V2DataJob b = createDummyJob("B");
    V2DataJob c = createDummyJob(null);
    V2DataJob c1 = createDummyJob(null);

    var baseCriteria =
        new Criteria<>(Objects::nonNull, Comparator.comparing(V2DataJob::getJobName));
    var filter = new Filter("description", "A", Sort.Direction.ASC);

    var descriptionCriteria = strategyByDescription.computeFilterCriteria(baseCriteria, filter);
    var comparator = descriptionCriteria.getComparator();

    Assertions.assertEquals(-1, comparator.compare(a, b));
    Assertions.assertEquals(-1, comparator.compare(b, c));
    Assertions.assertEquals(-1, comparator.compare(a, c));
    Assertions.assertEquals(1, comparator.compare(b, a));
    Assertions.assertEquals(1, comparator.compare(c, a));
    Assertions.assertEquals(0, comparator.compare(a1, a));
    Assertions.assertEquals(0, comparator.compare(c1, c));
  }

  private V2DataJob createDummyJob(String desc) {
    V2DataJob job = new V2DataJob();
    V2DataJobConfig config = new V2DataJobConfig();
    config.setDescription(desc);
    job.setConfig(config);

    return job;
  }
}
