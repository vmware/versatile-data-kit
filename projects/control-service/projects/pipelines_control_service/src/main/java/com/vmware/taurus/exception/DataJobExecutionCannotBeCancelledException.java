package com.vmware.taurus.exception;

import org.springframework.http.HttpStatus;

public class DataJobExecutionCannotBeCancelledException extends DomainError implements UserFacingError {

    private ExecutionCancellationFailureReason reason;

    public DataJobExecutionCannotBeCancelledException(String executionId, ExecutionCancellationFailureReason reason) {
        super(String.format("The Data Job execution '%s' cannot be cancelled.", executionId),
                getWhyMessage(reason),
                getConsequencesMessage(reason),
                getCounterMeasuresMessage(reason),
                null);
        this.reason = reason;
    }

    @Override
    public HttpStatus getHttpStatus() {

        if (this.reason == ExecutionCancellationFailureReason.DataJobNotFound ||
                this.reason == ExecutionCancellationFailureReason.DataJobExecutionNotFound) {
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
        String message;

        if (reason == ExecutionCancellationFailureReason.DataJobNotFound ||
                reason == ExecutionCancellationFailureReason.ExecutionNotRunning ||
                reason == ExecutionCancellationFailureReason.DataJobExecutionNotFound) {

            message = "Data job execution will not be cancelled. No changes to the DB will be made.";
        } else {
            message = "Unknown consequences.";
        }

        return message;
    }

    private static String getCounterMeasuresMessage(ExecutionCancellationFailureReason reason) {
        String message;

        if (reason == ExecutionCancellationFailureReason.DataJobNotFound) {
            message = "Specified Data Job for Team must exist and be deployed to cancel one of its running executions. " +
                    "You can use 'vdkcli list' to list Data jobs that have been created in cloud.";
        } else if (reason == ExecutionCancellationFailureReason.ExecutionNotRunning) {
            message = "Make sure you are attempting to cancel an execution in Running or Submitted state. " +
                    "You can use 'vdkcli execute --list' to show all executions currently stored in the database.";
        } else if (reason == ExecutionCancellationFailureReason.DataJobExecutionNotFound) {
            message = "The provided data job execution does not exist. Make sure the provided execution id is correct. " +
                    "You can use 'vdkcli execute --list' to show all executions currently stored in the database.";
        } else {
            message = "Unknown countermeasures.";
        }

        return message;
    }

}

