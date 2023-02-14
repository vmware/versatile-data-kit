/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.exception;

import org.apache.commons.lang3.StringUtils;

/**
 * A class that makes it easier to follow error handling standards.
 *
 * @see SystemError
 * @see DomainError
 */
public abstract class TaurusExceptionBase extends RuntimeException {

  private final ErrorMessage errorMessage;

  /**
   * @param msg
   * @param cause can be null
   */
  TaurusExceptionBase(ErrorMessage msg, Throwable cause) {
    super(
        msg.toString(),
        cause); // do not guard against NullPointerException. We want to always fail if msg is not
    // filled in
    this.errorMessage = msg;
    if (!validateMessage()) {
      throw new Bug("An error without complete description was defined or thrown.", this);
    }
  }

  TaurusExceptionBase(
      String what, String why, String consequences, String countermeasures, Throwable cause) {
    this(new ErrorMessage(what, why, consequences, countermeasures), cause);
  }

  public ErrorMessage getErrorMessage() {
    return errorMessage;
  }

  protected boolean validateMessage() {
    if (null == errorMessage) {
      return false;
    }
    if (StringUtils.isBlank(errorMessage.getConsequences())) {
      return false;
    }
    if (StringUtils.isBlank(errorMessage.getCountermeasures())) {
      return false;
    }
    if (StringUtils.isBlank(errorMessage.getWhat())) {
      return false;
    }
    if (StringUtils.isBlank(errorMessage.getWhy())) {
      return false;
    }
    return true;
  }
}
