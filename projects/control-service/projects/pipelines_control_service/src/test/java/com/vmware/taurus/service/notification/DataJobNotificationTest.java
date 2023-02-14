/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.notification;

import com.dumbster.smtp.SimpleSmtpServer;
import com.dumbster.smtp.SmtpMessage;
import com.vmware.taurus.service.model.JobConfig;
import org.jetbrains.annotations.NotNull;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

import java.io.IOException;
import java.util.*;

public class DataJobNotificationTest {

  private SimpleSmtpServer smptServer;
  private EmailNotification.SmtpProperties smtpProperties;
  private JobConfig jobConfig;
  private DataJobNotification dataJobNotification;
  private String receiverMail;

  @BeforeEach
  public void setup() throws IOException {
    this.smptServer = SimpleSmtpServer.start(SimpleSmtpServer.AUTO_SMTP_PORT);
    this.smtpProperties = Mockito.mock(EmailNotification.SmtpProperties.class);
    Mockito.when(smtpProperties.smtpWithPrefix())
        .thenReturn(getMailProperties(this.smptServer.getPort()));

    this.dataJobNotification =
        new DataJobNotification(
            new EmailNotification(this.smtpProperties),
            "Example Name",
            "your_username@vmware.com",
            Collections.singletonList("cc@dummy.com"));
    this.receiverMail = "dummy@dummy.dummy";
    this.jobConfig = getJobConfig();
  }

  @AfterEach
  public void clean() {
    this.smptServer.close();
  }

  @Test
  public void jobNotificationsMultiple() throws IOException {
    dataJobNotification.notifyJobDeployError(jobConfig, "bad", "very bad");
    dataJobNotification.notifyJobDeploySuccess(jobConfig);
    dataJobNotification.notifyJobDeployError(jobConfig, "Some error", "Some error body");

    List<SmtpMessage> emails = this.smptServer.getReceivedEmails();
    Assertions.assertEquals(3, emails.size());
    Assertions.assertEquals(
        "[deploy][data job failure] example_unittest_job", emails.get(0).getHeaderValue("Subject"));
    Assertions.assertEquals(
        "[deploy][data job success] example_unittest_job", emails.get(1).getHeaderValue("Subject"));
  }

  @Test
  public void jobNotificationsJobDeployError() throws IOException {
    dataJobNotification.notifyJobDeployError(jobConfig, "Some error", "Some error body");

    List<SmtpMessage> emails = this.smptServer.getReceivedEmails();
    Assertions.assertEquals(1, emails.size());
    var email = emails.get(0);
    Assertions.assertEquals(
        "[deploy][data job failure] example_unittest_job", email.getHeaderValue("Subject"));
    Assertions.assertEquals("cc@dummy.com, dummy@dummy.dummy", email.getHeaderValue("To"));
  }

  @Test
  public void jobNotificationsJobDeploySuccess() throws IOException {
    dataJobNotification.notifyJobDeploySuccess(jobConfig);

    List<SmtpMessage> emails = this.smptServer.getReceivedEmails();
    Assertions.assertEquals(1, emails.size());
    var email = emails.get(0);
    Assertions.assertEquals(
        "[deploy][data job success] example_unittest_job", email.getHeaderValue("Subject"));
    Assertions.assertEquals("cc@dummy.com, dummy@dummy.dummy", email.getHeaderValue("To"));
  }

  @NotNull
  private JobConfig getJobConfig() {
    JobConfig jobConfig = new JobConfig();
    List<String> receivers = new ArrayList<>();
    receivers.add(receiverMail);
    jobConfig.setNotifiedOnJobDeploy(receivers);
    jobConfig.setJobName("example_unittest_job");
    return jobConfig;
  }

  private Map<String, String> getMailProperties(int port) {
    Map<String, String> mailProps = new HashMap<>();
    mailProps.put("mail.smtp.host", "localhost");
    mailProps.put("mail.smtp.port", "" + port);
    mailProps.put("mail.smtp.sendpartial", "true");
    return mailProps;
  }
}
