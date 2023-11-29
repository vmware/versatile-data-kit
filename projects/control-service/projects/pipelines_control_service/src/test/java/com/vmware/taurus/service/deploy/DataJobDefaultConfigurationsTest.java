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

  @Autowired private DataJobDefaultConfigurations dataJobDefaultConfigurations;

  @Test
  public void testDefaultMemoryRequest() throws Exception {
    Assertions.assertEquals(500, K8SMemoryConversionUtils.getMemoryInMi(dataJobDefaultConfigurations.dataJobRequests().getMemory()));
  }

  @Test
  public void testDefaultMemoryLimit() throws Exception {
    Assertions.assertEquals(1000, K8SMemoryConversionUtils.getMemoryInMi(dataJobDefaultConfigurations.dataJobLimits().getMemory()));
  }

  @Test
  public void testDefaultCpuRequest() throws Exception {
    Assertions.assertEquals(1000, K8SMemoryConversionUtils.getCpuInFloat(dataJobDefaultConfigurations.dataJobRequests().getCpu()));
  }

  @Test
  public void testDefaultCpuLimit() throws Exception {
    Assertions.assertEquals(2000, K8SMemoryConversionUtils.getCpuInFloat(dataJobDefaultConfigurations.dataJobLimits().getCpu()));
  }

  @Test
  public void testKbConversion() {
    Assertions.assertEquals(2, K8SMemoryConversionUtils.getMemoryInMi( 2000, "K"));
  }

  @Test
  public void testKiConversion() {
    Assertions.assertEquals(2, K8SMemoryConversionUtils.getMemoryInMi( 2048, "Ki"));
  }

  @Test
  public void testGbConversion() {
    Assertions.assertEquals(2000, K8SMemoryConversionUtils.getMemoryInMi( 2, "G"));
  }

  @Test
  public void testGiConversion() {
    Assertions.assertEquals(2048, K8SMemoryConversionUtils.getMemoryInMi( 2, "Gi"));
  }

  @Test
  public void testTbConversion() {
    Assertions.assertEquals(2000000, K8SMemoryConversionUtils.getMemoryInMi( 2, "T"));
  }

  @Test
  public void testTiConversion() {
    Assertions.assertEquals(2097152, K8SMemoryConversionUtils.getMemoryInMi( 2, "Ti"));
  }
}
