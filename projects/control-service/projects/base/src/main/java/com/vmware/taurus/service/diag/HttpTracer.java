/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.diag;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import com.vmware.taurus.SpringAppPropNames;
import com.vmware.taurus.service.diag.telemetry.ITelemetry;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.actuate.trace.http.HttpTrace;
import org.springframework.core.env.Environment;
import org.springframework.stereotype.Component;
import org.springframework.web.servlet.HandlerMapping;

import javax.servlet.http.HttpServletRequest;
import java.util.Deque;
import java.util.LinkedList;
import java.util.List;

@Component
@Slf4j
public class HttpTracer implements org.springframework.boot.actuate.trace.http.HttpTraceRepository {

  @Autowired
  public HttpTracer(
      @Value("${" + SpringAppPropNames.HTTPTRACES_TO_KEEP + ":3}") int numberOfTracesToKeep,
      OperationContext operationContext,
      ITelemetry telemetryClient,
      Environment env) {
    if (numberOfTracesToKeep < 1) {
      throw new RuntimeException("Invalid Configuration");
    }
    this.numberOfTracesToKeep = numberOfTracesToKeep;
    this.operationContext = operationContext;
    this.telemetryClient = telemetryClient;
    this.environment = env;
  }

  private final Deque<HttpTrace> deque = new LinkedList<>();
  private final int numberOfTracesToKeep;
  private final Environment environment;
  private final OperationContext operationContext;
  private final ITelemetry telemetryClient;

  @Override
  public List<HttpTrace> findAll() {
    synchronized (deque) {
      return new LinkedList<>(deque);
    }
  }

  @Override
  public void add(HttpTrace trace) {
    if (null != trace) {
      synchronized (deque) {
        deque.addFirst(trace);
        while (deque.size() > this.numberOfTracesToKeep) {
          deque.removeLast();
        }
      }
      logTheTrace(trace);
      sendTelemetry(trace);
    }
  }

  private void logTheTrace(HttpTrace trace) {
    // We have many requests coming to /prometheus /liveness /readiness that would flood the log
    if (isSystemCall(trace)) {
      log.trace(
          "[user:{}] {} {} -> {}",
          trace.getPrincipal() != null ? trace.getPrincipal().getName() : "anonymous",
          trace.getRequest().getMethod(),
          trace.getRequest().getUri(),
          trace.getResponse().getStatus());
    } else {
      log.info(
          "[user:{}] {} {} -> {}",
          trace.getPrincipal() != null ? trace.getPrincipal().getName() : "anonymous",
          trace.getRequest().getMethod(),
          trace.getRequest().getUri(),
          trace.getResponse().getStatus());
      if (log.isDebugEnabled()) {
        try {
          ObjectMapper mapper = new ObjectMapper();
          mapper.registerModule(new JavaTimeModule());
          String jsonString = mapper.writerWithDefaultPrettyPrinter().writeValueAsString(trace);
          log.debug(jsonString);
        } catch (Exception e) {
          log.warn("Failed to log the HttpTrace object.", e);
        }
      }
    }
  }

  private boolean isSystemCall(HttpTrace trace) {
    String path = trace.getRequest().getUri().getPath();
    if (path.endsWith("/debug/prometheus")
        || path.endsWith("/debug/health/liveness")
        || path.endsWith("/debug/health/readiness")) {
      return true;
    }
    return false;
  }

  void sendTelemetry(HttpTrace trace) {
    // there are many request for monitoring purposes and there is no point sending telemetry for
    // them
    if (isSystemCall(trace)) {
      return;
    }
    ObjectMapper mapper = new ObjectMapper();
    mapper.registerModule(new JavaTimeModule());
    ObjectNode node = mapper.convertValue(trace, ObjectNode.class);
    node.put("@type", "taurus_httptrace");
    node.put("deployment_mode", String.join(",", environment.getActiveProfiles()));
    String opId = operationContext.getOpId();
    if (null != opId) {
      node.put("@id", opId);
    }
    HttpServletRequest request = operationContext.getRequest();
    if (null != request) { // methods from the actuator don't have the request set
      String requestMapping =
          "" + request.getAttribute(HandlerMapping.BEST_MATCHING_PATTERN_ATTRIBUTE);
      node.put("request_mapping", requestMapping);
    }
    String user = operationContext.getUser();
    if (null != user) {
      node.put("user", user);
    }
    String team = operationContext.getTeam();
    if (null != team) {
      node.put("team", team);
    }
    String json = node.toPrettyString();
    this.telemetryClient.sendAsync(json);
  }
}
