/*
 * Copyright 2023-2025 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.graphql.strategy.datajob;

import com.vmware.taurus.service.graphql.model.Criteria;
import com.vmware.taurus.service.graphql.model.V2DataJob;
import com.vmware.taurus.service.graphql.model.V2DataJobDeployment;
import com.vmware.taurus.service.graphql.model.Filter;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.springframework.data.domain.Sort;

import java.util.Collections;
import java.util.Comparator;
import java.util.Objects;
import java.util.function.Predicate;

import static org.assertj.core.api.Assertions.assertThat;

class JobFieldStrategyByJobPythonVersionTest {

  private final JobFieldStrategyByJobPythonVersion strategyByJobPythonVersion =
      new JobFieldStrategyByJobPythonVersion();

  @Test
  void testJobDescriptionStrategy_whenGettingStrategyName_shouldBeSpecific() {
    assertThat(strategyByJobPythonVersion.getStrategyName())
        .isEqualTo(JobFieldStrategyBy.DEPLOYMENT_JOBPYTHONVERSION);
  }

  @Test
  void testJobDescriptionStrategy_whenAlteringFieldData_shouldNotModifyState() {
    V2DataJob dataJob = createDummyJob("3.9");

    strategyByJobPythonVersion.alterFieldData(dataJob);

    assertThat(dataJob.getDeployments().stream().findFirst().orElseThrow().getJobPythonVersion())
        .isEqualTo("3.9");
  }

  @Test
  void
      testJobDescriptionStrategy_whenComputingValidCriteriaWithoutFilter_shouldReturnValidCriteria() {
    Criteria<V2DataJob> baseCriteria =
        new Criteria<>(Objects::nonNull, Comparator.comparing(V2DataJob::getJobName));
    Filter baseFilter = new Filter("random", null, Sort.Direction.DESC);
    V2DataJob a = createDummyJob("3.1");
    V2DataJob b = createDummyJob("3.2");

    Criteria<V2DataJob> v2DataJobCriteria =
        strategyByJobPythonVersion.computeFilterCriteria(baseCriteria, baseFilter);

    assertThat(v2DataJobCriteria.getPredicate().test(a)).isTrue();
    assertThat(v2DataJobCriteria.getComparator().compare(a, b)).isPositive();
  }

  @Test
  void testJobDescriptionStrategy_whenComputingValidCriteriaWithFilter_shouldReturnValidCriteria() {
    Criteria<V2DataJob> baseCriteria =
        new Criteria<>(Objects::nonNull, Comparator.comparing(V2DataJob::getJobName));
    Filter baseFilter = new Filter("JobPythonVersion", "3.1", Sort.Direction.ASC);
    V2DataJob a = createDummyJob("3.1");
    V2DataJob b = createDummyJob("3.2");

    Criteria<V2DataJob> v2DataJobCriteria =
        strategyByJobPythonVersion.computeFilterCriteria(baseCriteria, baseFilter);

    assertThat(v2DataJobCriteria.getPredicate().test(a)).isTrue();
    assertThat(v2DataJobCriteria.getPredicate().test(b)).isFalse();
    assertThat(v2DataJobCriteria.getComparator().compare(a, b)).isNegative();
  }

  @Test
  void testJobDescriptionStrategy_whenComputingValidSearchProvided_shouldReturnValidPredicate() {
    Predicate<V2DataJob> predicate = strategyByJobPythonVersion.computeSearchCriteria("3.1");

    V2DataJob a = createDummyJob("3.1");
    V2DataJob b = createDummyJob("3.2");

    assertThat(predicate.test(a)).isTrue();
    assertThat(predicate.test(b)).isFalse();
  }

  @Test
  void testJobDescriptionStrategy_whenComputingInvalidSearchProvided_shouldReturnValidPredicate() {
    Predicate<V2DataJob> predicate = strategyByJobPythonVersion.computeSearchCriteria("3.1");

    V2DataJob a = new V2DataJob();

    assertThat(predicate.test(a)).isFalse();
  }

  @Test
  public void testJobDescriptionComparator() {

    V2DataJob a = createDummyJob("3.1");
    V2DataJob a1 = createDummyJob("3.1");
    V2DataJob b = createDummyJob("3.2");
    V2DataJob c = createDummyJob(null);
    V2DataJob c1 = createDummyJob(null);

    var baseCriteria =
        new Criteria<>(Objects::nonNull, Comparator.comparing(V2DataJob::getJobName));
    var filter = new Filter("JobPythonVersion", "3.1", Sort.Direction.ASC);

    var jobPythonVersionCriteria =
        strategyByJobPythonVersion.computeFilterCriteria(baseCriteria, filter);
    var comparator = jobPythonVersionCriteria.getComparator();

    Assertions.assertEquals(-1, comparator.compare(a, b));
    Assertions.assertEquals(-1, comparator.compare(b, c));
    Assertions.assertEquals(-1, comparator.compare(a, c));
    Assertions.assertEquals(1, comparator.compare(b, a));
    Assertions.assertEquals(1, comparator.compare(c, a));
    Assertions.assertEquals(0, comparator.compare(a1, a));
    Assertions.assertEquals(0, comparator.compare(c1, c));
  }

  private V2DataJob createDummyJob(String jobPythonVersion) {
    V2DataJob job = new V2DataJob();
    V2DataJobDeployment deployment = new V2DataJobDeployment();
    deployment.setJobPythonVersion(jobPythonVersion);
    job.setDeployments(Collections.singletonList(deployment));
    return job;
  }
}
