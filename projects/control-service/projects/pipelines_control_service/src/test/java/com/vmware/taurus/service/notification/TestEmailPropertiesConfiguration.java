package com.vmware.taurus.service.notification;

import com.vmware.taurus.ControlplaneApplication;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

@SpringBootTest(classes = ControlplaneApplication.class)
public class TestEmailPropertiesConfiguration {

  @Autowired private EmailPropertiesConfiguration emailPropertiesConfiguration;

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
    Assertions.assertEquals(emailPropertiesConfiguration.getTransportProtocol(), "smtp");
    Assertions.assertEquals(
        emailPropertiesConfiguration.smtpWithPrefix().get("mail.smtp.host"), "smtp.vmware.com");
    Assertions.assertEquals(
        emailPropertiesConfiguration.smtpWithPrefix().get("mail.smtp.auth"), "false");
    Assertions.assertEquals(
        emailPropertiesConfiguration.smtpWithPrefix().get("mail.smtp.starttls.enable"), "false");
    Assertions.assertEquals(
        emailPropertiesConfiguration.smtpWithPrefix().get("mail.smtp.user"), "");
    Assertions.assertEquals(
        emailPropertiesConfiguration.smtpWithPrefix().get("mail.smtp.password"), "");
    Assertions.assertEquals(
        emailPropertiesConfiguration.smtpWithPrefix().get("mail.smtp.ssl.protocols"), "TLSv1.2");
    Assertions.assertEquals(
        emailPropertiesConfiguration.smtpWithPrefix().get("mail.smtp.port"), "25");
  }

  @Test
  public void testPropertyGetters() {
    Assertions.assertEquals(emailPropertiesConfiguration.getPassword(), "");
    Assertions.assertEquals(emailPropertiesConfiguration.getUsername(), "");
    Assertions.assertEquals(emailPropertiesConfiguration.getTransportProtocol(), "smtp");
    Assertions.assertFalse(emailPropertiesConfiguration.isAuthEnabled());
  }
}
