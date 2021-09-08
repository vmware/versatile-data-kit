/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.discovery;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.junit4.SpringRunner;

import static org.junit.Assert.assertEquals;

@RunWith(SpringRunner.class)
@SpringBootTest
public class ServiceLocationTest {
   @Test
   public void teamRootUriTest() {
      String expected = "http://localhost:8090";
      String actual = ServiceLocation.TEAM.rootUri;
      assertEquals(expected, actual);
   }
}
