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
import org.junit.jupiter.api.Test;

import java.util.Comparator;
import java.util.Objects;
import java.util.function.Predicate;

import static org.assertj.core.api.Assertions.assertThat;

class JobFieldStrategyBySourceUrlTest {

  private static final String GIT_REPO_URL_RAW = "gitlab.com/taurus/jobs.git";
  private static final String GIT_REPO_URL_FORMATTED = "https://gitlab.com/taurus/jobs";
  private static final String GIT_REPO_BRANCH = "main";
  private final JobFieldStrategyBySourceUrl strategyBySourceUrl =
      new JobFieldStrategyBySourceUrl(GIT_REPO_URL_RAW, GIT_REPO_BRANCH, true);

  @Test
  void testJobSourceUrlStrategy_whenGettingStrategyName_shouldBeSpecific() {
    assertThat(strategyBySourceUrl.getStrategyName()).isEqualTo(JobFieldStrategyBy.SOURCE_URL);
  }

  @Test
  void testJobSourceUrlStrategy_whenAlteringFieldData_shouldModifyState() {
    String jobName = "sample-job";
    V2DataJob dataJob = createDummyJob(jobName);

    strategyBySourceUrl.alterFieldData(dataJob);

    assertThat(dataJob.getConfig().getSourceUrl())
        .isEqualTo(
            String.format("%s/-/tree/%s/%s", GIT_REPO_URL_FORMATTED, GIT_REPO_BRANCH, jobName));
  }

  @Test
  void
      testJobSourceUrlStrategy_whenComputingValidCriteriaWithoutFilter_shouldReturnTheSameCriteria() {
    Criteria<V2DataJob> baseCriteria =
        new Criteria<>(
            Objects::nonNull,
            Comparator.comparing(dataJob -> dataJob.getConfig().getDescription()));

    Criteria<V2DataJob> v2DataJobCriteria =
        strategyBySourceUrl.computeFilterCriteria(baseCriteria, null);

    assertThat(v2DataJobCriteria.getPredicate()).isEqualTo(baseCriteria.getPredicate());
    assertThat(v2DataJobCriteria.getComparator()).isEqualTo(baseCriteria.getComparator());
  }

  @Test
  void testJobSourceUrlStrategy_whenComputingValidSearchProvided_shouldReturnValidPredicate() {
    Predicate<V2DataJob> predicate = strategyBySourceUrl.computeSearchCriteria("sample-job");

    V2DataJob a = createDummyJob("sample-job");

    assertThat(predicate.test(a)).isFalse(); // always false cause its empty
  }

  private V2DataJob createDummyJob(String jobName) {
    V2DataJob job = new V2DataJob();
    job.setJobName(jobName);
    V2DataJobConfig config = new V2DataJobConfig();
    job.setConfig(config);
    return job;
  }
}
