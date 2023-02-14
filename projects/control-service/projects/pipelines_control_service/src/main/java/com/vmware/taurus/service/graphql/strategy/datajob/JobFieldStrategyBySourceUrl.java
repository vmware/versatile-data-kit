/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.graphql.strategy.datajob;

import com.vmware.taurus.service.graphql.model.Criteria;
import com.vmware.taurus.service.graphql.model.V2DataJob;
import com.vmware.taurus.service.graphql.model.V2DataJobConfig;
import com.vmware.taurus.service.graphql.strategy.FieldStrategy;
import com.vmware.taurus.service.graphql.model.Filter;
import com.vmware.taurus.service.upload.GitWrapper;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.lang.NonNull;
import org.springframework.stereotype.Component;
import org.springframework.util.StringUtils;

import java.util.function.Predicate;

@Component
public class JobFieldStrategyBySourceUrl extends FieldStrategy<V2DataJob> {

  private final String gitDataJobsUrl;

  private final String getGitDataJobsBranch;

  public JobFieldStrategyBySourceUrl(
      @Value("${datajobs.git.url}") String gitDataJobsUrl,
      @Value("${datajobs.git.branch}") String getGitDataJobsBranch,
      @Value("${datajobs.git.ssl.enabled}") boolean gitDataJobsSslEnabled) {

    this.gitDataJobsUrl = GitWrapper.constructCorrectGitUrl(gitDataJobsUrl, gitDataJobsSslEnabled);
    this.getGitDataJobsBranch = getGitDataJobsBranch;
  }

  @Override
  public JobFieldStrategyBy getStrategyName() {
    return JobFieldStrategyBy.SOURCE_URL;
  }

  /** Sorting and filtering through the source url is meaningless */
  @Override
  public Criteria<V2DataJob> computeFilterCriteria(
      @NonNull Criteria<V2DataJob> criteria, @NonNull Filter filter) {
    return criteria;
  }

  /** Searching through the source url is meaningless */
  @Override
  public Predicate<V2DataJob> computeSearchCriteria(@NonNull String searchStr) {
    return x -> false;
  }

  @Override
  public void alterFieldData(V2DataJob dataJob) {
    V2DataJobConfig config = dataJob.getConfig();

    if (config == null || gitDataJobsUrl == null) {
      return;
    }

    String sourceUrl =
        StringUtils.stripFilenameExtension(gitDataJobsUrl)
            .concat(
                String.format(
                    "/-/tree/%s/%s",
                    getGitDataJobsBranch,
                    dataJob.getJobName())); // TODO in TAUR-1400, when deployments are implemented,
    // replace master
    config.setSourceUrl(sourceUrl);
    dataJob.setConfig(config);
  }
}
