/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus;

import com.vmware.taurus.exception.Bug;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

public class ExceptionCausedByTest {

  @Test
  public void exceptionCausedByTest() {
    String expectedMessage = "foobarbaz";
    Exception cause = new Exception(expectedMessage);
    Bug bug = new Bug("why", cause);
    Assertions.assertEquals(expectedMessage, bug.getCause().getMessage());
  }
}
