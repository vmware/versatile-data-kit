/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.exception;

import org.springframework.http.HttpStatus;

public class DataJobExecutionCannotBeCancelledException extends DomainError
    implements UserFacingError {

  private ExecutionCancellationFailureReason reason;

  public DataJobExecutionCannotBeCancelledException(
      String executionId, ExecutionCancellationFailureReason reason) {
    super(
        String.format("The Data Job execution '%s' cannot be cancelled.", executionId),
        getWhyMessage(reason),
        getConsequencesMessage(reason),
        getCounterMeasuresMessage(reason),
        null);
    this.reason = reason;
  }

  @Override
  public HttpStatus getHttpStatus() {

    if (this.reason == ExecutionCancellationFailureReason.DataJobNotFound
        || this.reason == ExecutionCancellationFailureReason.DataJobExecutionNotFound) {
      return HttpStatus.NOT_FOUND;
    }

    return HttpStatus.BAD_REQUEST;
  }

  private static String getWhyMessage(ExecutionCancellationFailureReason reason) {
    String message;

    if (reason == ExecutionCancellationFailureReason.DataJobNotFound) {
      message = "Specified Data Job for Team does not exist.";
    } else if (reason == ExecutionCancellationFailureReason.ExecutionNotRunning) {
      message = "Specified data job execution is not in running or submitted state.";
    } else if (reason == ExecutionCancellationFailureReason.DataJobExecutionNotFound) {
      message = "Specified data job execution does not exist.";
    } else {
      message = "Unknown cause.";
    }
    return message;
  }

  private static String getConsequencesMessage(ExecutionCancellationFailureReason reason) {
    // reason is here in case we need to expand this method in the future
    return "API request to cancel Data Job Execution failed.";
  }

  private static String getCounterMeasuresMessage(ExecutionCancellationFailureReason reason) {
    String message;

    if (reason == ExecutionCancellationFailureReason.DataJobNotFound) {
      message =
          "Specified Data Job for Team must exist and be deployed to cancel one of its running"
              + " executions. List data jobs that have been created in cloud and make sure you"
              + " specify a valid data job and team.";
    } else if (reason == ExecutionCancellationFailureReason.ExecutionNotRunning) {
      message =
          "List recent and/or current executions of the Data Job. "
              + "Make sure you specify a valid execution in running or submitted state.";
    } else if (reason == ExecutionCancellationFailureReason.DataJobExecutionNotFound) {
      message =
          "The provided data job execution does not exist. Make sure the provided execution id is"
              + " correct. List all data job executions of the data job and make sure you specify"
              + " one that exists.";
    } else {
      message =
          "Unknown failure reason. Please verify all specified parameters: data job, data job"
              + " execution and team are correct and try again. Should the problem persist please"
              + " contact support.";
    }

    return message;
  }
}
