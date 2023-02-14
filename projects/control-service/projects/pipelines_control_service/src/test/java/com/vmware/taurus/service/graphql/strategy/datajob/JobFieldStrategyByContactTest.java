/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.graphql.strategy.datajob;

import com.vmware.taurus.controlplane.model.data.DataJobContacts;
import com.vmware.taurus.service.graphql.model.Criteria;
import com.vmware.taurus.service.graphql.model.Filter;
import com.vmware.taurus.service.graphql.model.V2DataJob;
import com.vmware.taurus.service.graphql.model.V2DataJobConfig;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.springframework.data.domain.Sort;

import java.util.Comparator;
import java.util.List;
import java.util.Objects;
import java.util.function.Predicate;

public class JobFieldStrategyByContactTest {

  private final JobFieldStrategyByDataJobContacts strategyByDataJobContacts =
      new JobFieldStrategyByDataJobContacts();

  @Test
  public void testDataJobContactsStrategy_whenGettingStrategyName_shouldBeSpecific() {
    Assertions.assertTrue(
        strategyByDataJobContacts.getStrategyName().equals(JobFieldStrategyBy.DATA_JOB_CONTACTS));
  }

  @Test
  public void testDataJobContactsStrategy_testEmptyContacts_shouldBeEqual() {
    Criteria<V2DataJob> baseCriteria =
        new Criteria<>(Objects::nonNull, Comparator.comparing(V2DataJob::getJobName));
    Filter filter = new Filter("contacts", null, Sort.Direction.ASC);

    V2DataJob a = createDummyJob(new DataJobContacts());
    V2DataJob b = createDummyJob(new DataJobContacts());

    Criteria<V2DataJob> v2DataJobCriteria =
        strategyByDataJobContacts.computeFilterCriteria(baseCriteria, filter);

    Assertions.assertTrue(v2DataJobCriteria.getPredicate().test(a));
    Assertions.assertTrue(v2DataJobCriteria.getPredicate().test(b));
    Assertions.assertEquals(0, v2DataJobCriteria.getComparator().compare(a, b));
  }

  @Test
  public void testDataJobContactsStrategy_testNonEmptyContacts_shouldBeEqual() {
    Criteria<V2DataJob> baseCriteria =
        new Criteria<>(Objects::nonNull, Comparator.comparing(V2DataJob::getJobName));
    Filter filter = new Filter("contacts", null, Sort.Direction.ASC);

    var contactA = new DataJobContacts();
    var contactB = new DataJobContacts();

    contactA.setNotifiedOnJobDeploy(List.of("non-empty"));
    contactB.setNotifiedOnJobFailureUserError(List.of("non-empty"));

    V2DataJob a = createDummyJob(contactA);
    V2DataJob b = createDummyJob(contactB);

    Criteria<V2DataJob> v2DataJobCriteria =
        strategyByDataJobContacts.computeFilterCriteria(baseCriteria, filter);

    Assertions.assertTrue(v2DataJobCriteria.getPredicate().test(a));
    Assertions.assertTrue(v2DataJobCriteria.getPredicate().test(b));
    Assertions.assertEquals(0, v2DataJobCriteria.getComparator().compare(a, b));
  }

  @Test
  public void testDataJobContactsStrategy_testEmptyNonEmptyContacts_shouldBeGreater() {
    Criteria<V2DataJob> baseCriteria =
        new Criteria<>(Objects::nonNull, Comparator.comparing(V2DataJob::getJobName));
    Filter filter = new Filter("contacts", null, Sort.Direction.ASC);

    var contactA = new DataJobContacts();
    var contactB = new DataJobContacts();

    contactA.setNotifiedOnJobDeploy(List.of("non-empty"));

    V2DataJob a = createDummyJob(contactA);
    V2DataJob b = createDummyJob(contactB);

    Criteria<V2DataJob> v2DataJobCriteria =
        strategyByDataJobContacts.computeFilterCriteria(baseCriteria, filter);

    Assertions.assertTrue(v2DataJobCriteria.getPredicate().test(a));
    Assertions.assertTrue(v2DataJobCriteria.getPredicate().test(b));
    Assertions.assertEquals(1, v2DataJobCriteria.getComparator().compare(a, b));
  }

  @Test
  public void testDataJobContactsStrategy_testEmptyNonEmptyContacts_shouldBeLess() {
    Criteria<V2DataJob> baseCriteria =
        new Criteria<>(Objects::nonNull, Comparator.comparing(V2DataJob::getJobName));
    Filter filter = new Filter("contacts", null, Sort.Direction.ASC);

    var contactA = new DataJobContacts();
    var contactB = new DataJobContacts();

    contactB.setNotifiedOnJobFailureUserError(List.of("non-empty"));

    V2DataJob a = createDummyJob(contactA);
    V2DataJob b = createDummyJob(contactB);

    Criteria<V2DataJob> v2DataJobCriteria =
        strategyByDataJobContacts.computeFilterCriteria(baseCriteria, filter);

    Assertions.assertTrue(v2DataJobCriteria.getPredicate().test(a));
    Assertions.assertTrue(v2DataJobCriteria.getPredicate().test(b));
    Assertions.assertEquals(-1, v2DataJobCriteria.getComparator().compare(a, b));
  }

  @Test
  void testJobContactsStrategy_whenComputingProvidedSearch_shouldReturnValidPredicate() {
    Predicate<V2DataJob> predicate =
        strategyByDataJobContacts.computeSearchCriteria("some random string");

    var contactA = new DataJobContacts();
    var contactB = new DataJobContacts();

    contactB.setNotifiedOnJobFailureUserError(List.of("non-empty"));

    V2DataJob a = createDummyJob(contactA);
    V2DataJob b = createDummyJob(contactB);

    Assertions.assertTrue(predicate.test(a));
    Assertions.assertTrue(predicate.test(b));
  }

  private V2DataJob createDummyJob(DataJobContacts contacts) {
    V2DataJob job = new V2DataJob();
    V2DataJobConfig config = new V2DataJobConfig();
    config.setDescription("desc");
    config.setContacts(contacts);
    job.setConfig(config);
    return job;
  }
}
