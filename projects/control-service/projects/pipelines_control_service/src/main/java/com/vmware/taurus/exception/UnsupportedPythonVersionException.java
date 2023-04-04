/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.exception;

import org.springframework.http.HttpStatus;


import java.util.Set;

public class UnsupportedPythonVersionException extends DomainError implements UserFacingError{
    public UnsupportedPythonVersionException(String pythonVersion, Set<String> supportedPythonVersions) {
        super(
                String.format("Not supported python version: '%s'", pythonVersion),
                "The selected python version is not supported by the platform.",
                "The deployment of the data job will not proceed. ",
                String.format("To deploy the data job, please set the python_version property to one of the supported versions: '%s'.", supportedPythonVersions.toString()),
                null);
    }

  @Override
  public HttpStatus getHttpStatus() {
    return HttpStatus.CONFLICT;
  }
}
