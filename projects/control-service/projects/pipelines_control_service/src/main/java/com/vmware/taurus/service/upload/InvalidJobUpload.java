/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.upload;

import com.vmware.taurus.exception.DomainError;
import com.vmware.taurus.exception.UserFacingError;
import org.springframework.http.HttpStatus;

public class InvalidJobUpload extends DomainError implements UserFacingError {
  public InvalidJobUpload(String jobName, String why, String countermeasures) {
    super(
        String.format("The Data Job '%s' upload is invalid .", jobName),
        "Data Job content validation failed because " + why,
        "The Data Job will not be uploaded. ",
        countermeasures,
        null);
  }

  @Override
  public HttpStatus getHttpStatus() {
    return HttpStatus.BAD_REQUEST;
  }
}
