/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.diag.telemetry;

import com.vmware.taurus.base.EnableComponents;
import org.apache.commons.lang3.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.concurrent.CompletableFuture;

@Component
@org.springframework.boot.autoconfigure.condition.ConditionalOnProperty(
    value = EnableComponents.DIAGNOSTICS,
    havingValue = "true",
    matchIfMissing = true)
public class Telemetry implements ITelemetry {
  private static final Logger log = LoggerFactory.getLogger(Telemetry.class);

  public Telemetry(@Value("${datajobs.telemetry.webhook.endpoint:}") String telemetryEndpoint) {
    this.client = HttpClient.newHttpClient();
    this.telemetryEndpoint = telemetryEndpoint;
    if (StringUtils.isBlank(this.telemetryEndpoint)) {
      log.info("Telemetry endpoint is empty and sending telemetry is skipped");
    }
  }

  // TODO: add support for buffering, re-tries (with back-off)
  private final String telemetryEndpoint;
  private final HttpClient client;

  private static <T> CompletableFuture<HttpResponse<T>> handleResponseWithRetry(
      HttpClient client,
      HttpRequest request,
      HttpResponse.BodyHandler<T> handler,
      HttpResponse<T> response) {
    if (response == null || response.statusCode() >= 500) {
      return client
          .sendAsync(request, handler)
          .thenApplyAsync(
              (r) -> {
                if (r.statusCode() >= 400) {
                  log.warn(
                      "Failed to send telemetry after re-try:"
                          + "telemetry webhook returned HTTP client error: "
                          + r.statusCode()
                          + " and content: "
                          + r.body());
                }
                return r;
              });
    } else {
      if (response.statusCode() >= 400 && response.statusCode() < 500) {
        log.warn(
            "Failed to send telemetry: telemetry webhook returned HTTP client error: "
                + response.statusCode()
                + " and content: "
                + response.body());
      }
      return CompletableFuture.completedFuture(response);
    }
  }

  @Override
  public void sendAsync(String payload) {
    if (StringUtils.isBlank(this.telemetryEndpoint)) {
      return;
    }
    log.trace("Sending streaming telemetry to {}", telemetryEndpoint);
    HttpResponse.BodyHandler<String> handler = HttpResponse.BodyHandlers.ofString();

    HttpRequest request =
        HttpRequest.newBuilder()
            .setHeader("accept", "application/json")
            .setHeader("content-type", "application/json")
            .uri(URI.create(this.telemetryEndpoint))
            .POST(HttpRequest.BodyPublishers.ofString(payload))
            .build();
    // we re-try once. We assume that most errors are resolved on first re-try.
    // For better robustness though we should consider more sophisticated re-tries with back off
    client
        .sendAsync(request, handler)
        .thenComposeAsync(r -> handleResponseWithRetry(client, request, handler, r));
  }
}
