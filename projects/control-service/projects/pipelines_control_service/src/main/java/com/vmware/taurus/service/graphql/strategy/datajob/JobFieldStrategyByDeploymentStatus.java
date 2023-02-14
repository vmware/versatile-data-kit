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
import org.springframework.lang.NonNull;
import org.springframework.stereotype.Component;

import java.util.Arrays;
import java.util.Comparator;
import java.util.function.Predicate;

/**
 * Strategy that uses deployment 'enabled' field to compute a deployment status.
 *
 * <p>It follow the algorithm: Job has deployment, and it is property 'enabled' is true - ENABLED;
 * Job has deployment, and it is property 'enabled' is false - DISABLED; Job has no deployment at
 * all - NOT_DEPLOYED
 *
 * <p>TODO when multiple deployments are implement refactor the class.
 */
@Component
public class JobFieldStrategyByDeploymentStatus extends FieldStrategy<V2DataJob> {

  private static final Comparator<V2DataJob> COMPARATOR_DEFAULT =
      Comparator.comparing(JobFieldStrategyByDeploymentStatus::toDeploymentStatus);

  @Override
  public JobFieldStrategyBy getStrategyName() {
    return JobFieldStrategyBy.DEPLOYMENT_ENABLED;
  }

  @Override
  public Criteria<V2DataJob> computeFilterCriteria(
      @NonNull Criteria<V2DataJob> criteria, @NonNull Filter filter) {
    Predicate<V2DataJob> predicate = criteria.getPredicate();

    if (filterProvided(filter)) {
      predicate = predicate.and(computeSearchCriteria(filter.getPattern()));
    }

    return new Criteria<>(predicate, detectSortingComparator(filter, COMPARATOR_DEFAULT, criteria));
  }

  @Override
  public Predicate<V2DataJob> computeSearchCriteria(@NonNull String searchStr) {
    try {
      DeploymentStatus deploymentStatus = DeploymentStatus.fromValue(searchStr);
      return dataJob -> deploymentStatus.equals(toDeploymentStatus(dataJob));
    } catch (IllegalArgumentException e) {
      // searching with non-compatible for the strategy string, ignoring search
      return x -> false;
    }
  }

  private static DeploymentStatus toDeploymentStatus(V2DataJob dataJob) {
    if (dataJob.getDeployments() == null || dataJob.getDeployments().isEmpty()) {
      return DeploymentStatus.NOT_DEPLOYED;
    }
    // TODO support for multiple deployments
    return dataJob.getDeployments().stream().findFirst().orElseThrow().getEnabled()
        ? DeploymentStatus.ENABLED
        : DeploymentStatus.DISABLED;
  }

  enum DeploymentStatus {
    ENABLED("enabled"),
    DISABLED("disabled"),
    NOT_DEPLOYED("not_deployed");

    private final String value;

    DeploymentStatus(String value) {
      this.value = value;
    }

    public String getValue() {
      return value;
    }

    public static DeploymentStatus fromValue(String value) {
      return Arrays.stream(DeploymentStatus.values())
          .filter(status -> status.getValue().equalsIgnoreCase(value))
          .findAny()
          .orElseThrow(
              () ->
                  new IllegalArgumentException(
                      "Deployment status could be only one of "
                          + Arrays.toString(DeploymentStatus.values()).toLowerCase()));
    }
  }
}
