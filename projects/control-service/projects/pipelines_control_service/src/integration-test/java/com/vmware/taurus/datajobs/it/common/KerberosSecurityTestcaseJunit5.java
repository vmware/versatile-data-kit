/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs.it.common;

import org.apache.kerby.kerberos.kerb.KrbException;
import org.apache.kerby.kerberos.kerb.server.SimpleKdcServer;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;

public class KerberosSecurityTestcaseJunit5 {
  SimpleKdcServer simpleKdcServer;
  // TODO we should think about moving away from MiniKDC as it's not maintained.
  @BeforeEach
  public void startMiniKdc() throws Exception {
    simpleKdcServer = new SimpleKdcServer();
    simpleKdcServer.start();
  }

  @AfterEach
  public void stopMiniKdc() throws KrbException {
    simpleKdcServer.stop();
  }
}
