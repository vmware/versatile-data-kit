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
public class DataJobDefaultConfigurationsTest {

  @Autowired
  private DataJobDefaultConfigurations dataJobDefaultConfigurations;

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

  @Test
  public void testKbConversion() {
    Assertions.assertEquals(2, K8SMemoryConversionUtils.getMemoryInMi("K", 2000));
  }

  @Test
  public void testKiConversion() {
    Assertions.assertEquals(2, K8SMemoryConversionUtils.getMemoryInMi("Ki", 2048));
  }

  @Test
  public void testGbConversion() {
    Assertions.assertEquals(2000, K8SMemoryConversionUtils.getMemoryInMi("G", 2));
  }

  @Test
  public void testGiConversion() {
    Assertions.assertEquals(2048, K8SMemoryConversionUtils.getMemoryInMi("Gi", 2));
  }

  @Test
  public void testTbConversion() {
    Assertions.assertEquals(2000000, K8SMemoryConversionUtils.getMemoryInMi("T", 2));
  }

  @Test
  public void testTiConversion() {
    Assertions.assertEquals(2097152, K8SMemoryConversionUtils.getMemoryInMi("Ti", 2));
  }
}
