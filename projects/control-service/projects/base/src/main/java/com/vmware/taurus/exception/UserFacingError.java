package com.vmware.taurus.exception;

import org.springframework.http.HttpStatus;

public interface UserFacingError {
    /**
     * @return the HTTP status that user should see for this exception.
     */
    abstract public HttpStatus getHttpStatus();
}
