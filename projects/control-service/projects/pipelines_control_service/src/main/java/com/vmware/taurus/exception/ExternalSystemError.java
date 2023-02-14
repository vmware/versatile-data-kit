/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.exception;

import org.springframework.http.HttpStatus;

import java.io.IOException;

/**
 * User-facing error caused by systems or layers that Taurus depends upon and are provided by the
 * team that operates the deployment
 *
 * <p>Common systems are documented in {@link MainExternalSystem}
 */
public class ExternalSystemError extends SystemError implements UserFacingError {

  /** External systems that may fail along with the name which appears in user-facing messages */
  public enum MainExternalSystem {

    /**
     * The Kubernetes cluster on which jobs and/or Taurus itself are deployed.
     *
     * <p>Typical intermittent issues are outages of components like etcd. Typical permanent issues
     * are bad permissions.
     */
    KUBERNETES("Kubernetes cluster"),

    /**
     * The backend database of the current Taurus component e.g. CockroachDB for Versatile Data Kit.
     */
    DATABASE("Database"),

    /**
     * The OCI or Docker container that hosts the component that failed
     *
     * <p>Typical intermittent issues are {@link IOException} when accessing local storage or
     * volumes.
     */
    HOST_CONTAINER("Host container"),

    /** The Kerberos KDC that manages service accounts for user workloads managed by Taurus */
    KERBEROS("Kerberos"),

    /** The webhook server to which we delegate authorization */
    AUTHORIZATION_SERVER("Authorization server"),

    /** The webhook server to which we delegate default operations */
    WEBHOOK_SERVER("Webhook server"),

    /** The Git repository that contains the data job code */
    GIT("Git");

    private final String userFacingName;

    MainExternalSystem(String userFacingName) {
      this.userFacingName = userFacingName;
    }
  }

  public ExternalSystemError(MainExternalSystem externalSystem, Throwable cause) {
    this(
        externalSystem.userFacingName,
        cause.toString(),
        cause); // cause must not be null to use this constructor
  }

  public ExternalSystemError(MainExternalSystem externalSystem, String errorDescription) {
    this(externalSystem.userFacingName, errorDescription, null);
  }

  public ExternalSystemError(
      MainExternalSystem externalSystem, String errorDescription, Throwable cause) {
    this(externalSystem.userFacingName, errorDescription, cause);
  }

  public ExternalSystemError(String externalSystemName, String errorDescription, Throwable cause) {
    super(
        String.format("%s encountered an error: %s.", externalSystemName, errorDescription),
        "The external system may be experiencing intermittent issues or there might be permanent"
            + " misconfiguration or outage.",
        "The current API operation failed.",
        "Try the operation again in a few minutes and open a ticket to the SRE team if the problem"
            + " persists.",
        cause);
  }

  @Override
  public HttpStatus getHttpStatus() {
    // Discussion here makes sense
    // https://stackoverflow.com/questions/25398364/http-status-code-for-external-dependency-error
    return HttpStatus.SERVICE_UNAVAILABLE;
  }
}
