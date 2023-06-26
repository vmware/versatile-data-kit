/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.notification;

import com.vmware.taurus.ControlplaneApplication;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

@SpringBootTest(classes = ControlplaneApplication.class)
public class TestEmailConfiguration {

  @Autowired private EmailConfiguration emailConfiguration;

  @Test
  public void testAllDefaultPropertiesPresent() {
    /*
    Default settings are as follows:
      mail.transport.protocol= ${MAIL_TRANSPORT_PROTOCOL:smtp}
      mail.smtp.host=smtp.vmware.com
      mail.smtp.auth=${MAIL_SMTP_AUTH:false}
      mail.smtp.starttls.enable=${MAIL_SMTP_STARTTLS_ENABLE:false}
      mail.smtp.user=${MAIL_SMTP_USER:}
      mail.smtp.password=${MAIL_SMTP_PASSWORD:}
      mail.smtp.ssl.protocols= ${MAIL_SMTP_SSL_PROTOCOLS:TLSv1.2}
      mail.smtp.port=${MAIL_SMTP_PORT:25}
     */
    Assertions.assertEquals(emailConfiguration.getTransportProtocol(), "smtp");
    Assertions.assertEquals(
        emailConfiguration.smtpWithPrefix().get("mail.smtp.host"), "smtp.vmware.com");
    Assertions.assertEquals(
        emailConfiguration.smtpWithPrefix().get("mail.smtp.auth"), "false");
    Assertions.assertEquals(
        emailConfiguration.smtpWithPrefix().get("mail.smtp.starttls.enable"), "false");
    Assertions.assertEquals(
        emailConfiguration.smtpWithPrefix().get("mail.smtp.user"), "");
    Assertions.assertEquals(
        emailConfiguration.smtpWithPrefix().get("mail.smtp.password"), "");
    Assertions.assertEquals(
        emailConfiguration.smtpWithPrefix().get("mail.smtp.ssl.protocols"), "TLSv1.2");
    Assertions.assertEquals(
        emailConfiguration.smtpWithPrefix().get("mail.smtp.port"), "25");
  }

  @Test
  public void testPropertyGetters() {
    Assertions.assertEquals(emailConfiguration.getPassword(), "");
    Assertions.assertEquals(emailConfiguration.getUsername(), "");
    Assertions.assertEquals(emailConfiguration.getTransportProtocol(), "smtp");
    Assertions.assertFalse(emailConfiguration.isAuthEnabled());
  }
}
