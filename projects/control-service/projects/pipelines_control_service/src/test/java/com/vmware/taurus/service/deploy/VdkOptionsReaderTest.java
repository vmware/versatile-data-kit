/*
 * Copyright 2021-2024 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.deploy;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

import java.util.Map;

public class VdkOptionsReaderTest {

  private static final String VDK_REDSHIFT_HOST_KEY = "VDK_REDSHIFT_HOST";
  private static final String VDK_REDSHIFT_NAME_KEY = "VDK_REDSHIFT_NAME";
  private static final String VDK_RESOURCE_LIMIT_MEMORY_MB_KEY = "VDK_RESOURCE_LIMIT_MEMORY_MB";
  private static final String VDK_RESOURCE_LIMIT_DISK_MB_KEY = "VDK_RESOURCE_LIMIT_DISK_MB";

  private VdkOptionsReader vdkOptionsReader =
      new VdkOptionsReader("src/test/resources/vdk_options/test_vdk_options.ini");

  @Test
  public void readVdkOptions_defaultOptions() {
    Map<String, String> vdkOptions = vdkOptionsReader.readVdkOptions("unconfigured-job-name");

    Assertions.assertEquals(2, vdkOptions.size());
    Assertions.assertEquals("rs-host", vdkOptions.get(VDK_REDSHIFT_HOST_KEY));
    Assertions.assertEquals("rs-name", vdkOptions.get(VDK_REDSHIFT_NAME_KEY));
  }

  @Test
  public void readVdkOptions_customJobOptions() {
    Map<String, String> vdkOptions = vdkOptionsReader.readVdkOptions("example");

    Assertions.assertEquals(4, vdkOptions.size());
    Assertions.assertEquals("rs-host", vdkOptions.get(VDK_REDSHIFT_HOST_KEY));
    Assertions.assertEquals("rs-name", vdkOptions.get(VDK_REDSHIFT_NAME_KEY));
    Assertions.assertEquals("10000", vdkOptions.get(VDK_RESOURCE_LIMIT_MEMORY_MB_KEY));
    Assertions.assertEquals("5000", vdkOptions.get(VDK_RESOURCE_LIMIT_DISK_MB_KEY));
  }
}
