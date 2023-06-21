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
public class EmailPropertiesConfiguration {

  private final String PASSWORD_PROPERTY_KEY = "mail.smtp.password";
  private final String USER_PROPERTY_KEY = "mail.smtp.user";
  private final String AUTH_ENABLE_PROPERTY_KEY = "mail.smtp.auth";

  @Bean
  @ConfigurationProperties(prefix = "mail.smtp")
  public Map<String, String> smtp() {
    return new HashMap<>();
  }

  public Map<String, String> smtpWithPrefix() {
    Map<String, String> result = new HashMap<>();
    var props = this.smtp();
    props.forEach(((key, value) -> result.put("mail.smtp." + key, value)));
    return result;
  }

  public String getUsername() {
    return smtpWithPrefix().get(USER_PROPERTY_KEY);
  }

  public String getPassword() {
    return smtpWithPrefix().get(PASSWORD_PROPERTY_KEY);
  }

  public boolean isAuthEnabled() {
    return Boolean.parseBoolean(smtpWithPrefix().get(AUTH_ENABLE_PROPERTY_KEY));
  }
}
