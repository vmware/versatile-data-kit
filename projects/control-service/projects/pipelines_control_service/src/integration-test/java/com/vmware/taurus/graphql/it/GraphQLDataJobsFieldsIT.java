/*
 * Copyright 2023-2024 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.graphql.it;

import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.datajobs.it.common.BaseIT;
import com.vmware.taurus.service.model.JobConfig;
import com.vmware.taurus.service.notification.EmailNotification;
import com.vmware.taurus.service.notification.NotificationContent;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import java.util.ArrayList;

@SpringBootTest(
    webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT,
    classes = ControlplaneApplication.class)
public class GraphQLDataJobsFieldsIT extends BaseIT {
  @Autowired private EmailNotification emailNotification;

  @Test
  void testFields() throws Exception {
    emailNotification.send(new NotificationContent(new JobConfig("teamName", "sfdsf", "sdfdsfs",
            "jobName", false, 10, "paulm2@vmware.com","paulm2@vmware.com",
            "paulm2@vmware.com", "paulm2@vmware.com", false, "jobName"),
            "deplyo", "success",
            "paul murphy", "paulm2@vmware.com", new ArrayList<>()));

  }
}
