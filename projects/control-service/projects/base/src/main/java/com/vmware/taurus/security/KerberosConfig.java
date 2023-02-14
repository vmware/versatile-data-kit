/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.security;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.kerberos.authentication.sun.GlobalSunJaasKerberosConfig;

@Configuration
@ConditionalOnProperty(value = "datajobs.security.kerberos.enabled")
public class KerberosConfig {

  @Value("${datajobs.security.kerberos.krb5ConfigLocation}")
  private String krb5ConfigLocation;

  @Bean
  public GlobalSunJaasKerberosConfig globalSunJaasKerberosConfig() {
    var config = new GlobalSunJaasKerberosConfig();
    config.setDebug(true);
    config.setKrbConfLocation(krb5ConfigLocation);
    return config;
  }
}
