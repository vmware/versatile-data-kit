/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus;

/**
 * Spring properties that can be overridden as per
 * https://docs.spring.io/spring-boot/docs/current/reference/html/spring-boot-features.html#boot-features-external-config
 */
public class SpringAppPropNames {
  // Sorted alphabetically

  // https://github.com/spring-projects/spring-boot/blob/2.2.x/spring-boot-project/spring-boot-actuator/src/main/java/org/springframework/boot/actuate/trace/http/Include.java
  public static final String HTTPTRACE_INCLUDE = "management.trace.include";
  public static final String HTTPTRACES_TO_KEEP = "taurus.diag.httptrace.max-traces-in-memory";
  public static final String MANAGEMENT_ENDPOINTS_WEB_BASE_PATH =
      "management.endpoints.web.base-path";
  public static final String MANAGEMENT_ENDPOINTS_WEB_EXPOSURE_INCLUDE =
      "management.endpoints.web.exposure.include";
  public static final String MANAGEMENT_ENDPOINT_HEALTH_SHOW_DETAILS =
      "management.endpoint.health.show-details";
  public static final String SVC_NAME = "taurus.svc.name";
}
