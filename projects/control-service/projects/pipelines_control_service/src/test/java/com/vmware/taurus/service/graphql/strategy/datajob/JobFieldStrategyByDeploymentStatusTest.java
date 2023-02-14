/*
 * Copyright 2021-2023 VMware, Inc.
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

class JobFieldStrategyByDeploymentStatusTest {

  private final JobFieldStrategyByDeploymentStatus strategyByDeploymentStatus =
      new JobFieldStrategyByDeploymentStatus();

  @Test
  void testJobDeploymentStatusStrategy_whenGettingStrategyName_shouldBeSpecific() {
    assertThat(strategyByDeploymentStatus.getStrategyName())
        .isEqualTo(JobFieldStrategyBy.DEPLOYMENT_ENABLED);
  }

  @Test
  void testJobDeploymentStatusStrategy_whenAlteringFieldData_shouldNotModifyState() {
    V2DataJob dataJob = createDummyJob(JobFieldStrategyByDeploymentStatus.DeploymentStatus.ENABLED);

    strategyByDeploymentStatus.alterFieldData(dataJob);

    assertThat(dataJob.getDeployments().get(0).getEnabled()).isTrue();
  }

  @Test
  void
      testJobDeploymentStatusStrategy_whenComputingValidCriteriaWithoutFilter_shouldReturnValidCriteria() {
    Criteria<V2DataJob> baseCriteria =
        new Criteria<>(Objects::nonNull, Comparator.comparing(V2DataJob::getJobName));
    Filter baseFilter = new Filter("random", null, Sort.Direction.DESC);
    V2DataJob a = createDummyJob(JobFieldStrategyByDeploymentStatus.DeploymentStatus.ENABLED);
    V2DataJob b = createDummyJob(JobFieldStrategyByDeploymentStatus.DeploymentStatus.DISABLED);

    Criteria<V2DataJob> v2DataJobCriteria =
        strategyByDeploymentStatus.computeFilterCriteria(baseCriteria, baseFilter);

    assertThat(v2DataJobCriteria.getPredicate().test(a)).isTrue();
    assertThat(v2DataJobCriteria.getComparator().compare(a, b)).isPositive();
  }

  @Test
  void
      testJobDeploymentStatusStrategy_whenComputingValidCriteriaWithFilter_shouldReturnValidCriteria() {
    Criteria<V2DataJob> baseCriteria =
        new Criteria<>(Objects::nonNull, Comparator.comparing(V2DataJob::getJobName));

    V2DataJob a = createDummyJob(JobFieldStrategyByDeploymentStatus.DeploymentStatus.ENABLED);
    V2DataJob b = createDummyJob(JobFieldStrategyByDeploymentStatus.DeploymentStatus.DISABLED);
    V2DataJob c = createDummyJob(JobFieldStrategyByDeploymentStatus.DeploymentStatus.NOT_DEPLOYED);

    Filter enabledFilter = new Filter("deployments.status", "enabled", Sort.Direction.ASC);
    Criteria<V2DataJob> criteriaForEnabledJobs =
        strategyByDeploymentStatus.computeFilterCriteria(baseCriteria, enabledFilter);

    assertThat(criteriaForEnabledJobs.getPredicate().test(a)).isTrue();
    assertThat(criteriaForEnabledJobs.getPredicate().test(b)).isFalse();
    assertThat(criteriaForEnabledJobs.getPredicate().test(c)).isFalse();
    assertThat(criteriaForEnabledJobs.getComparator().compare(a, b)).isNegative();
    assertThat(criteriaForEnabledJobs.getComparator().compare(c, b)).isPositive();
    assertThat(criteriaForEnabledJobs.getComparator().compare(a, c)).isNegative();

    Filter disabledFilter = new Filter("deployments.status", "disabled", Sort.Direction.ASC);
    Criteria<V2DataJob> criteriaForDisabledJobs =
        strategyByDeploymentStatus.computeFilterCriteria(baseCriteria, disabledFilter);

    assertThat(criteriaForDisabledJobs.getPredicate().test(a)).isFalse();
    assertThat(criteriaForDisabledJobs.getPredicate().test(b)).isTrue();
    assertThat(criteriaForDisabledJobs.getPredicate().test(c)).isFalse();

    Filter notDeployedFilter = new Filter("deployments.status", "not_deployed", Sort.Direction.ASC);
    Criteria<V2DataJob> criteriaForNotDeployedJobs =
        strategyByDeploymentStatus.computeFilterCriteria(baseCriteria, notDeployedFilter);

    assertThat(criteriaForNotDeployedJobs.getPredicate().test(a)).isFalse();
    assertThat(criteriaForNotDeployedJobs.getPredicate().test(b)).isFalse();
    assertThat(criteriaForNotDeployedJobs.getPredicate().test(c)).isTrue();
  }

  @Test
  void
      testJobDeploymentStatusStrategy_whenComputingValidSearchProvided_shouldReturnValidPredicate() {
    Predicate<V2DataJob> predicate = strategyByDeploymentStatus.computeSearchCriteria("enabled");

    V2DataJob a = createDummyJob(JobFieldStrategyByDeploymentStatus.DeploymentStatus.ENABLED);
    V2DataJob b = createDummyJob(JobFieldStrategyByDeploymentStatus.DeploymentStatus.DISABLED);
    V2DataJob c = createDummyJob(JobFieldStrategyByDeploymentStatus.DeploymentStatus.NOT_DEPLOYED);

    assertThat(predicate.test(a)).isTrue();
    assertThat(predicate.test(b)).isFalse();
    assertThat(predicate.test(c)).isFalse();

    Predicate<V2DataJob> predicateIgnoredCase =
        strategyByDeploymentStatus.computeSearchCriteria("eNaBlEd");
    assertThat(predicateIgnoredCase.test(a)).isTrue();
  }

  @Test
  void
      testJobDeploymentStatusStrategy_whenComputingInvalidSearchProvided_shouldReturnValidPredicate() {
    Predicate<V2DataJob> predicate = strategyByDeploymentStatus.computeSearchCriteria("blah");

    V2DataJob a = new V2DataJob();

    assertThat(predicate.test(a)).isFalse();
  }

  @Test
  void testJobDeploymentStatusStrategy_whenUsingInvalidPatternValue_shouldThrowException() {
    Assertions.assertThrows(
        IllegalArgumentException.class,
        () -> {
          JobFieldStrategyByDeploymentStatus.DeploymentStatus.fromValue("not-existing-value-123");
        });
  }

  private V2DataJob createDummyJob(JobFieldStrategyByDeploymentStatus.DeploymentStatus status) {
    V2DataJob job = new V2DataJob();
    if (status.equals(JobFieldStrategyByDeploymentStatus.DeploymentStatus.NOT_DEPLOYED)) {
      return job;
    }
    V2DataJobDeployment deployment = new V2DataJobDeployment();
    deployment.setEnabled(
        JobFieldStrategyByDeploymentStatus.DeploymentStatus.ENABLED.equals(status));
    job.setDeployments(Collections.singletonList(deployment));
    return job;
  }
}
