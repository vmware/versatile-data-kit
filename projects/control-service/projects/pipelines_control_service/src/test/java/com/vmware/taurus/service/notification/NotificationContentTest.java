/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.notification;

import com.vmware.taurus.service.model.JobConfig;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

import javax.mail.internet.AddressException;
import javax.mail.internet.InternetAddress;
import java.util.Arrays;
import java.util.Collections;

public class NotificationContentTest {

  @Test
  public void test_basic_notification() {
    JobConfig jobConfig = createValidJobConfigStub();
    try {
      NotificationContent notificationContent =
          new NotificationContent(
              jobConfig,
              "run",
              "failure",
              "Example Name",
              "sender@vmware.com",
              Arrays.asList("foo@bar.com", "bar@foo.com"));

      InternetAddress expectedSender = new InternetAddress("sender@vmware.com");
      InternetAddress[] expectedRecipients =
          new InternetAddress[] {
            new InternetAddress("foo@bar.com"),
            new InternetAddress("bar@foo.com"),
            new InternetAddress("receiver@vmware.com")
          };
      String expectedSubject = "[run][data job failure] test_job";
      String expectedContent =
          "<p>Dear Data Pipelines user,<br/>\n"
              + "Last run of your data job <strong>test_job</strong> has status: failure.</p>\n"
              + "\n"
              + "<p>The sender mailbox is not monitored, please do not reply to this email.</p>\n"
              + "<p>Best,<br/>Example Name</p>\n";

      Assertions.assertEquals(
          notificationContent.getSender().getAddress(), expectedSender.getAddress());
      Assertions.assertArrayEquals(notificationContent.getRecipients(), expectedRecipients);
      Assertions.assertEquals(notificationContent.getSubject(), expectedSubject);
      Assertions.assertEquals(notificationContent.getContent(), expectedContent);
    } catch (AddressException e) {
      Assertions.fail("Unexpected exception" + e.toString());
    }
  }

  @Test
  public void test_address_exception() {
    JobConfig jobConfig = createInvalidJobConfigStub();
    try {
      new NotificationContent(
          jobConfig, "run", "failure", "Example Name", "@vmware.com", Collections.emptyList());
    } catch (AddressException e) {
      Assertions.assertEquals("Missing local name", e.getMessage());
    }
  }

  @Test
  public void test_error_notification() {
    JobConfig jobConfig = createValidJobConfigStub();
    try {
      NotificationContent notificationContent =
          new NotificationContent(
              jobConfig,
              "run",
              "failure",
              "RuntimeError",
              "Some body",
              "Example Name",
              "sender@vmware.com",
              Collections.emptyList());

      InternetAddress expectedSender = new InternetAddress("sender@vmware.com");
      InternetAddress[] expectedRecipients =
          new InternetAddress[] {new InternetAddress("receiver@vmware.com")};
      String expectedSubject = "[run][data job failure] test_job";
      String expectedContent =
          "<p>Dear Data Pipelines user,<br/>\n"
              + "Last run of your data job <strong>test_job</strong> has status: failure.</p>\n"
              + "<p>Data job: test_job error.</p>\n"
              + "<p>Details:</p>\n"
              + "<p style=\"padding-left: 30px; color:red;\">RuntimeError</p>\n"
              + "<p>Some body</p>\n"
              + "<p>For more information please visit&nbsp;\n"
              + "<a href=\"https://confluence.eng.vmware.com/display/SUPCR/Data+Pipelines+User+Guide#DataPipelinesUserGuide-Monitoring&amp;Troubleshooting\">Data"
              + " Pipelines User Guide - Monitoring&amp;Troubleshooting</a>.</p>\n"
              + "<p>The sender mailbox is not monitored, please do not reply to this email.</p>\n"
              + "<p>Best,<br/>Example Name</p>\n";

      Assertions.assertEquals(
          notificationContent.getSender().getAddress(), expectedSender.getAddress());
      Assertions.assertArrayEquals(notificationContent.getRecipients(), expectedRecipients);
      Assertions.assertEquals(notificationContent.getSubject(), expectedSubject);
      Assertions.assertEquals(notificationContent.getContent(), expectedContent);
    } catch (AddressException e) {
      Assertions.fail("Unexpected exception" + e.toString());
    }
  }

  private JobConfig createValidJobConfigStub() {
    JobConfig jobConfig = new JobConfig();
    jobConfig.setNotifiedOnJobDeploy(Collections.singletonList("receiver@vmware.com"));
    jobConfig.setJobName("test_job");
    return jobConfig;
  }

  private JobConfig createInvalidJobConfigStub() {
    JobConfig jobConfig = new JobConfig();
    jobConfig.setNotifiedOnJobDeploy(Collections.singletonList("@vmware.com"));
    jobConfig.setJobName("test_job");
    return jobConfig;
  }
}
