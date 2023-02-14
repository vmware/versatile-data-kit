/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.graphql.strategy.datajob;

import com.vmware.taurus.controlplane.model.data.DataJobContacts;
import com.vmware.taurus.service.graphql.model.Criteria;
import com.vmware.taurus.service.graphql.model.Filter;
import com.vmware.taurus.service.graphql.model.V2DataJob;
import com.vmware.taurus.service.graphql.strategy.FieldStrategy;
import org.apache.commons.collections4.CollectionUtils;
import org.springframework.stereotype.Component;

import java.util.Comparator;
import java.util.function.Predicate;

@Component
public class JobFieldStrategyByDataJobContacts extends FieldStrategy<V2DataJob> {
  private static final Comparator<V2DataJob> COMPARATOR_DEFAULT =
      Comparator.comparing(
          e -> e.getConfig().getContacts(),
          Comparator.nullsLast(
              (o1, o2) -> {
                boolean o1ContactPresent = isContactPresent(o1);
                boolean o2ContactPresent = isContactPresent(o2);
                return Boolean.compare(o1ContactPresent, o2ContactPresent);
              }));

  @Override
  public JobFieldStrategyBy getStrategyName() {
    return JobFieldStrategyBy.DATA_JOB_CONTACTS;
  }

  @Override
  public Criteria<V2DataJob> computeFilterCriteria(Criteria<V2DataJob> criteria, Filter filter) {
    var predicate = criteria.getPredicate();
    return new Criteria<>(predicate, detectSortingComparator(filter, COMPARATOR_DEFAULT, criteria));
  }

  @Override
  public Predicate<V2DataJob> computeSearchCriteria(String searchStr) {
    // searching by notification is not meaningful yet
    return dataJob -> true;
  }

  private static boolean isContactPresent(DataJobContacts contacts) {
    return CollectionUtils.isNotEmpty(contacts.getNotifiedOnJobDeploy())
        || CollectionUtils.isNotEmpty(contacts.getNotifiedOnJobFailurePlatformError())
        || CollectionUtils.isNotEmpty(contacts.getNotifiedOnJobFailureUserError())
        || CollectionUtils.isNotEmpty(contacts.getNotifiedOnJobSuccess());
  }
}
