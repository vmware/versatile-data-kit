/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.exception;

import org.junit.jupiter.api.Test;
import org.springframework.http.HttpStatus;

import static org.junit.jupiter.api.Assertions.assertThrows;

public class SystemErrorTest {

  private static class InvalidSystemError extends SystemError implements UserFacingError {
    InvalidSystemError() {
      super("bla", "bla", "bla", "bla", null);
    }

    @Override
    public HttpStatus getHttpStatus() {
      return HttpStatus.OK;
    }
  }

  @Test
  public void testValidation() {
    assertThrows(Bug.class, InvalidSystemError::new);
  }
}
