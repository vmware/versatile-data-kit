/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs.it.common;

import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.springframework.security.kerberos.test.KerberosSecurityTestcase;

public class KerberosSecurityTestcaseJunit5 extends KerberosSecurityTestcase {
  // TODO we should think about moving away from MiniKDC as it's not maintained.
  @BeforeEach
  @Override
  public void startMiniKdc() throws Exception {
    super.startMiniKdc();
  }

  @AfterEach
  @Override
  public void stopMiniKdc() {
    super.stopMiniKdc();
  }
}
