/*
 * Copyright (c) 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus;

import com.vmware.taurus.exception.Bug;
import org.junit.Test;

import static org.junit.Assert.assertEquals;

public class ExceptionCausedByTest {
   @Test()
   public void exceptionCausedByTest() {
      String expectedMessage = "foobarbaz";
      Exception cause = new Exception(expectedMessage);
      Bug bug = new Bug("why", cause);
      assertEquals(expectedMessage, bug.getCause().getMessage());
   }
}
