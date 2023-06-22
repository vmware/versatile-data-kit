/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.notification;

import com.icegreen.greenmail.util.GreenMail;
import com.icegreen.greenmail.util.ServerSetup;
import com.vmware.taurus.service.model.JobConfig;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import javax.mail.MessagingException;
import org.jetbrains.annotations.NotNull;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mockito;
import org.springframework.boot.test.system.CapturedOutput;
import org.springframework.boot.test.system.OutputCaptureExtension;

@ExtendWith(OutputCaptureExtension.class)
public class AuthenticatedEmailNotificationTest {

  private final String TEST_USER = "test@user.com";
  private final String TEST_PASSWORD = "testPassword123";
  private final String TEST_PROTOCOL = "smtp";

  private GreenMail greenMail;
  private EmailPropertiesConfiguration emailPropertiesConfiguration;
  private DataJobNotification dataJobNotification;
  private String receiverMail = TEST_USER;

  @BeforeEach
  public void setup() {
    greenMail = new GreenMail(ServerSetup.SMTP.dynamicPort());
    greenMail.start();

    this.emailPropertiesConfiguration = Mockito.mock(EmailPropertiesConfiguration.class);
    Mockito.when(emailPropertiesConfiguration.smtpWithPrefix()).thenReturn(getMailProperties());
    Mockito.when(emailPropertiesConfiguration.isAuthEnabled()).thenReturn(true);
    Mockito.when(emailPropertiesConfiguration.getUsername()).thenReturn(TEST_USER);
    Mockito.when(emailPropertiesConfiguration.getPassword()).thenReturn(TEST_PASSWORD);
    Mockito.when(emailPropertiesConfiguration.getTransportProtocol()).thenReturn(TEST_PROTOCOL);

    this.dataJobNotification =
        new DataJobNotification(
            new EmailNotification(this.emailPropertiesConfiguration),
            "Example Name",
            TEST_USER,
            Collections.singletonList("cc@dummy.com"));
  }

  @AfterEach
  public void cleanup() {
    greenMail.stop();
  }

  @Test
  public void testAuthenticate_wrongCredentials(CapturedOutput output) {
    greenMail.setUser(TEST_USER, "wrong_password");
    dataJobNotification.notifyJobDeployError(getJobConfig(), "bad", "very bad");
    Assertions.assertTrue(
        output
            .getOut()
            .contains(
                "javax.mail.AuthenticationFailedException: 535 5.7.8  Authentication credentials"
                    + " invalid"));
  }

  @Test
  public void testAuthenticate_correctCredentials(CapturedOutput output) {
    greenMail.setUser(TEST_USER, TEST_PASSWORD);
    dataJobNotification.notifyJobDeployError(getJobConfig(), "bad", "very bad");
    Assertions.assertFalse(
        output
            .getOut()
            .contains(
                "javax.mail.AuthenticationFailedException: 535 5.7.8  Authentication credentials"
                    + " invalid"));
  }

  @Test
  public void testAuthenticate_correctCredentials_andMessageReceived()
      throws MessagingException, IOException {
    greenMail.setUser(TEST_USER, TEST_PASSWORD);
    dataJobNotification.notifyJobDeployError(getJobConfig(), "bad", "very bad");

    var messages = greenMail.getReceivedMessages();
    var from = messages[0].getFrom();
    var content = messages[0].getContent();

    Assertions.assertEquals(TEST_USER, from[0].toString());
    Assertions.assertTrue(content.toString().contains("Dear Data Pipelines user"));
  }

  private Map<String, String> getMailProperties() {
    Map<String, String> mailProps = new HashMap<>();
    mailProps.put("mail.smtp.host", ServerSetup.getLocalHostAddress());
    mailProps.put("mail.smtp.port", Integer.toString(greenMail.getSmtp().getPort()));
    mailProps.put("mail.smtp.auth", "true");
    mailProps.put("mail.smtp.starttls.enable", "true");
    mailProps.put("mail.transport.protocol", TEST_PROTOCOL);
    mailProps.put("mail.smtp.user", TEST_USER);
    mailProps.put("mail.smtp.password", TEST_PASSWORD);
    return mailProps;
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
}
