/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.exception;

import org.springframework.http.HttpStatus;

public class KubernetesJobDefinitionException extends SystemError implements UserFacingError {
  public KubernetesJobDefinitionException(String jobName) {
    super(
        String.format(
            "A configuration error with the current kubernetes job: '%s' definition was found.",
            jobName),
        "Likely due to recent changes in the internal implementation.",
        "The current call will not be processed.",
        "Please open a new GitHub issue with the details of this error.",
        null);
  }

  @Override
  public HttpStatus getHttpStatus() {
    return HttpStatus.INTERNAL_SERVER_ERROR;
  }
}
