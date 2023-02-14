/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.diag;

import com.vmware.taurus.SpringAppPropNames;
import com.vmware.taurus.service.diag.methodintercept.Measurable;
import com.vmware.taurus.service.diag.telemetry.ITelemetry;
import io.swagger.v3.oas.annotations.Hidden;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RestController;

import java.time.Instant;

@RestController
@RequiredArgsConstructor
@Slf4j
@Tag(name = "Data Jobs Diagnostics")
@Hidden
public class DiagnosticsController {
  // ${svc.url.prefix} is read from application.properties (overridden in other services, so e.g.
  // Team service has /team/debug/servertime)

  private final ITelemetry telemetryClient;

  @Measurable
  @RequestMapping("/${" + SpringAppPropNames.SVC_NAME + "}/debug/servertime-millis")
  public long timeMillis() {
    return System.currentTimeMillis();
  }

  @Operation(summary = "Get system clock in UTC")
  @RequestMapping(
      value = "/${" + SpringAppPropNames.SVC_NAME + "}/debug/servertime",
      method = RequestMethod.GET)
  public Instant timeUTC() {
    return Instant.now();
  }

  @RequestMapping("/${" + SpringAppPropNames.SVC_NAME + "}/debug/throw")
  public void throwException() {
    throw new RuntimeException("Just throwing.");
  }

  @RequestMapping({"/${" + SpringAppPropNames.SVC_NAME + "}/debug/echo/{msg}"})
  public ResponseEntity<String> echo(String msg) {
    return new ResponseEntity<String>(msg, HttpStatus.OK);
  }

  @RequestMapping({"/${" + SpringAppPropNames.SVC_NAME + "}/debug/report/{message}"})
  public ResponseEntity<Void> report(String msg) {
    log.trace(msg);
    telemetryClient.sendAsync(msg);
    return ResponseEntity.accepted().build();
  }
}
