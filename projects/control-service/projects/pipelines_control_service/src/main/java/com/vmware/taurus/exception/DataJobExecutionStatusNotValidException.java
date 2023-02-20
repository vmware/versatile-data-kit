/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.exception;

import com.vmware.taurus.controlplane.model.data.DataJobExecution;
import org.springframework.http.HttpStatus;

import java.util.Arrays;
import java.util.stream.Collectors;

public class DataJobExecutionStatusNotValidException extends DomainError
    implements UserFacingError {

  public DataJobExecutionStatusNotValidException(String jobName) {
    super(
        String.format("The Execution Status '%s' is not valid.", jobName),
        "The Execution Status must be valid.",
        "The Data Job Execution(s) will not be returned.",
        "Provide a valid Execution Status. Valid statuses are: "
            + Arrays.stream(DataJobExecution.StatusEnum.values())
                .map(statusEnum -> statusEnum.getValue())
                .collect(Collectors.joining(", ", "[", "].")),
        null);
  }

  @Override
  public HttpStatus getHttpStatus() {
    return HttpStatus.NOT_FOUND;
  }
}
