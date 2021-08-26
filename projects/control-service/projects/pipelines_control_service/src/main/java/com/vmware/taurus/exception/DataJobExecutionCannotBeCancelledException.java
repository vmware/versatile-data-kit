package com.vmware.taurus.exception;

import org.springframework.http.HttpStatus;

public class DataJobExecutionCannotBeCancelledException extends DomainError implements UserFacingError {

    public DataJobExecutionCannotBeCancelledException(String executionId) {
        super(String.format("The Data Job execution '%s' cannot be cancelled.", executionId),
                "Likely the Data Job execution is not running or submitted.",
                "The cancel call to the API will have no consequences on the execution.",
                "Provide a Data Job execution that can be cancelled and try again.",
                null);
    }

    @Override
    public HttpStatus getHttpStatus() {
        return HttpStatus.BAD_REQUEST;
    }

}
