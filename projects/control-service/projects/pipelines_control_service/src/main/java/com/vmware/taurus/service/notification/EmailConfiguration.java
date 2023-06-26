/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.notification;

import java.util.HashMap;
import java.util.Map;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class EmailConfiguration {

  private final String MAIL_SMTP_PASSWORD = "mail.smtp.password";
  private final String MAIL_SMTP_USER = "mail.smtp.user";
  private final String MAIL_SMTP_AUTH = "mail.smtp.auth";
  private final String TRANSPORT_PROTOCOL = "transport.protocol";

  @Bean
  @ConfigurationProperties(prefix = "mail")
  Map<String, String> mail() {
    return new HashMap<>();
  }

  public Map<String, String> smtpWithPrefix() {
    Map<String, String> result = new HashMap<>();
    var props = this.mail();
    props.forEach(
        ((key, value) -> {
          if (key.startsWith("smtp")) {
            result.put("mail." + key, value);
          }
        }));
    return result;
  }

  public String getUsername() {
    return smtpWithPrefix().get(MAIL_SMTP_USER);
  }

  public String getPassword() {
    return smtpWithPrefix().get(MAIL_SMTP_PASSWORD);
  }

  public boolean isAuthEnabled() {
    return Boolean.parseBoolean(smtpWithPrefix().get(MAIL_SMTP_AUTH));
  }

  /**
   * Transport protocol to be used to send email messages e.g smtp, pop, imap. Defined in
   * application.properties
   *
   * @return
   */
  public String getTransportProtocol() {
    return mail().get(TRANSPORT_PROTOCOL);
  }
}
