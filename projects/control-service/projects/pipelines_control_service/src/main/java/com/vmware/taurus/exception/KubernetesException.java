/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.exception;

import io.kubernetes.client.openapi.ApiException;

/** Wrapper over Kubernetes Exception printing more details from ApiException */
public class KubernetesException extends ExternalSystemError {

  public KubernetesException(String errorDescription, Throwable cause) {
    super(MainExternalSystem.KUBERNETES.name(), errorDescription + getDetails(cause), cause);
  }

  private static String getDetails(Throwable cause) {
    if (cause instanceof ApiException) {
      return getDetails((ApiException) cause);
    }
    return cause != null ? cause.getMessage() : "";
  }

  private static String getDetails(ApiException cause) {
    StringBuilder sb = new StringBuilder();
    sb.append("\nKubernetes API Exception Details: \n");
    sb.append("response body: ").append(cause.getResponseBody()).append("\n");
    sb.append("response headers: ").append(cause.getResponseHeaders());
    return sb.toString();
  }
}
