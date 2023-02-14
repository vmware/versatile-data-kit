/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.model;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

/**
 * The purpose of this test class is to ensure that every change to the already defined Labels or
 * Annotations is intentional. This is because we will be persisting data based on those
 * labels/annotations.
 */
public class K8SAnnotationsLabelsTest {

  @Test
  public void testAnnotations() {
    var msg = "JobAnnotation enum changed, make sure this change is intentional and update tests.";

    var schedule = JobAnnotation.SCHEDULE.getValue();
    var startedBy = JobAnnotation.STARTED_BY.getValue();
    var deployedDate = JobAnnotation.DEPLOYED_DATE.getValue();
    var deployedBy = JobAnnotation.DEPLOYED_BY.getValue();
    var executionType = JobAnnotation.EXECUTION_TYPE.getValue();
    var opId = JobAnnotation.OP_ID.getValue();
    var unscheduled = JobAnnotation.UNSCHEDULED.getValue();

    Assertions.assertEquals("com.vmware.taurus/schedule", schedule, msg);
    Assertions.assertEquals("com.vmware.taurus/started-by", startedBy, msg);
    Assertions.assertEquals("com.vmware.taurus/deployed-date", deployedDate, msg);
    Assertions.assertEquals("com.vmware.taurus/deployed-by", deployedBy, msg);
    Assertions.assertEquals("com.vmware.taurus/execution-type", executionType, msg);
    Assertions.assertEquals("com.vmware.taurus/op-id", opId, msg);
    Assertions.assertEquals("com.vmware.taurus/unscheduled", unscheduled, msg);

    Assertions.assertEquals(7, JobAnnotation.values().length, msg);
  }

  @Test
  public void testLabels() {
    var msg = "JobLabel enum changed, make sure this change is intentional and update tests.";

    var jobName = JobLabel.NAME.getValue();
    var version = JobLabel.VERSION.getValue();
    var type = JobLabel.TYPE.getValue();
    var executionId = JobLabel.EXECUTION_ID.getValue();
    var startedByUsed = JobLabel.STARTED_BY_USER.getValue();

    Assertions.assertEquals("com.vmware.taurus/name", jobName, msg);
    Assertions.assertEquals("com.vmware.taurus/version", version, msg);
    Assertions.assertEquals("com.vmware.taurus/type", type, msg);
    Assertions.assertEquals("com.vmware.taurus/data-job-execution-id", executionId, msg);
    Assertions.assertEquals("com.vmware.taurus/start-by-user", startedByUsed, msg);

    Assertions.assertEquals(5, JobLabel.values().length, msg);
  }
}
