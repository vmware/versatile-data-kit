/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.deploy;

import org.junit.Assert;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.mockito.junit.MockitoJUnitRunner;

import java.util.Map;

@RunWith(MockitoJUnitRunner.class)
public class VdkOptionsReaderTest {

   private static final String VDK_INFLUX_DB_PASSWORD_KEY = "VDK_INFLUX_DB_PASSWORD";
   private static final String VDK_REDSHIFT_HOST_KEY = "VDK_REDSHIFT_HOST";
   private static final String VDK_REDSHIFT_NAME_KEY = "VDK_REDSHIFT_NAME";
   private static final String VDK_RESOURCE_LIMIT_MEMORY_MB_KEY = "VDK_RESOURCE_LIMIT_MEMORY_MB";
   private static final String VDK_RESOURCE_LIMIT_DISK_MB_KEY = "VDK_RESOURCE_LIMIT_DISK_MB";

   private VdkOptionsReader vdkOptionsReader = new VdkOptionsReader("src/test/resources/vdk_options/test_vdk_options.ini");

   @Test
   public void readVdkOptions_defaultOptions() {
      Map<String, String> vdkOptions = vdkOptionsReader.readVdkOptions("unconfigured-job-name");

      Assert.assertEquals(3, vdkOptions.size());
      Assert.assertEquals("influx-db-pass", vdkOptions.get(VDK_INFLUX_DB_PASSWORD_KEY));
      Assert.assertEquals("rs-host", vdkOptions.get(VDK_REDSHIFT_HOST_KEY));
      Assert.assertEquals("rs-name", vdkOptions.get(VDK_REDSHIFT_NAME_KEY));
   }

   @Test
   public void readVdkOptions_customJobOptions() {
      Map<String, String> vdkOptions = vdkOptionsReader.readVdkOptions("example");

      Assert.assertEquals(5, vdkOptions.size());
      Assert.assertEquals("influx-db-pass", vdkOptions.get(VDK_INFLUX_DB_PASSWORD_KEY));
      Assert.assertEquals("rs-host", vdkOptions.get(VDK_REDSHIFT_HOST_KEY));
      Assert.assertEquals("rs-name", vdkOptions.get(VDK_REDSHIFT_NAME_KEY));
      Assert.assertEquals("10000", vdkOptions.get(VDK_RESOURCE_LIMIT_MEMORY_MB_KEY));
      Assert.assertEquals("5000", vdkOptions.get(VDK_RESOURCE_LIMIT_DISK_MB_KEY));
   }
}
