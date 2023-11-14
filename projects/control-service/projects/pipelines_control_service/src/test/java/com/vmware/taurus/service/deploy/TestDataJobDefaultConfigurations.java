/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.deploy;

import com.vmware.taurus.ControlplaneApplication;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

@SpringBootTest(classes = ControlplaneApplication.class)
public class TestDataJobDefaultConfigurations {

  @Autowired private DataJobDefaultConfigurations dataJobDefaultConfigurations;

  @Test
  public void testDefaultMemoryRequest() throws Exception {
    Assertions.assertEquals(500, dataJobDefaultConfigurations.getMemoryRequests());
  }

  @Test
  public void testDefaultMemoryLimit() throws Exception {
    Assertions.assertEquals(1000, dataJobDefaultConfigurations.getMemoryLimits());
  }

  @Test
  public void testDefaultCpuRequest() throws Exception {
    Assertions.assertEquals(1000, dataJobDefaultConfigurations.getCpuRequests());
  }

  @Test
  public void testDefaultCpuLimit() throws Exception {
    Assertions.assertEquals(2000, dataJobDefaultConfigurations.getCpuLimits());
  }
}
