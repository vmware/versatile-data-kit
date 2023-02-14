/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs.it.common;

import org.apache.kerby.kerberos.kerb.KrbException;
import org.apache.kerby.kerberos.kerb.server.SimpleKdcServer;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class KdcServerConfiguration {

  @Bean(destroyMethod = "stop")
  SimpleKdcServer simpleKdcServer() throws KrbException {
    var simpleKdcServer = new SimpleKdcServer();
    simpleKdcServer.init();
    simpleKdcServer.start();
    return simpleKdcServer;
  }
}
