/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.diag.methodintercept;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.vmware.taurus.SpringAppPropNames;
import com.vmware.taurus.base.EnableComponents;
import com.vmware.taurus.base.SCCPProperties;
import com.vmware.taurus.service.diag.Metrics;
import com.vmware.taurus.service.diag.telemetry.ITelemetry;
import org.aspectj.lang.reflect.MethodSignature;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Component;

import java.io.PrintWriter;
import java.io.StringWriter;
import java.util.Map;
import java.util.TreeMap;
import java.util.function.Consumer;

@Component
@org.springframework.boot.autoconfigure.condition.ConditionalOnProperty(
    value = EnableComponents.DIAGNOSTICS_INTERCEPTOR,
    havingValue = "true",
    matchIfMissing = true)
public class DiagnosticsPublisher implements Consumer<DiagnosticsContext> {
  private final Logger log = LoggerFactory.getLogger(this.getClass());

  @Autowired
  public DiagnosticsPublisher(ITelemetry telemetryClient, SCCPProperties properties) {
    this.telemetryClient = telemetryClient;
    this.properties = properties;
    this.helper = new MetricsHelper();
  }

  private final ITelemetry telemetryClient;
  private final SCCPProperties properties;
  private final MetricsHelper helper;

  @Override
  public void accept(DiagnosticsContext context) {
    Map<Metrics, Object> metrics = contextToMetrics(context);
    String opId = "" + metrics.get(Metrics.op_id);
    try {
      // this modifies the metrics
      if (metrics.containsKey(Metrics.method_result)) {
        String result = "" + metrics.get(Metrics.method_result);
        String resAsStr = result.substring(0, Math.min(666, result.length()));
        metrics.put(Metrics.method_result, resAsStr);
      }
      if (metrics.containsKey(Metrics.error_class)) {
        String asStr = ("" + metrics.get(Metrics.error_class));
        metrics.put(Metrics.method_result, asStr);
      }
      metrics.put(Metrics.cp_svc_name, properties.getSpringProperty(SpringAppPropNames.SVC_NAME));

      ObjectMapper mapper = new ObjectMapper();
      ObjectNode node = mapper.convertValue(metrics, ObjectNode.class);
      node.put("@table", "taurus_api_call");
      node.put("@id", opId);
      String json = node.toPrettyString();
      log.trace("Sending telemetry: {}", json);
      this.telemetryClient.sendAsync(json);
    } catch (Exception e) {
      log.warn("Could not send telemetry.\n" + "Data was " + metrics, e);
    }
  }

  public Map<Metrics, Object> contextToMetrics(DiagnosticsContext context) {
    Map<Metrics, Object> metrics = new TreeMap<>();
    MethodSignature signature = (MethodSignature) context.joinPoint.getSignature();
    helper.signatureToMetricsAboutJavaMethod(signature, metrics);
    helper.joinPointToMetricsAboutMeasurable(context.joinPoint, metrics);
    diagContextToMetricsAboutExecution(context, metrics);
    return metrics;
  }

  public void diagContextToMetricsAboutExecution(
      DiagnosticsContext context, Map<Metrics, Object> metrics) {
    metrics.put(Metrics.op_id, context.opId);
    metrics.put(Metrics.method_execution_time_nanos, context.stopWatch.getTotalTimeNanos());
    metrics.put(Metrics.method_execution_end_timestamp, System.currentTimeMillis());
    boolean hasError = null != context.error;
    metrics.put(Metrics.call_failed, hasError);
    if (hasError) {
      metrics.put(Metrics.error_class, context.error.getClass());
      metrics.put(Metrics.error_message, context.error.getMessage());
      StringWriter sw = new StringWriter();
      PrintWriter pw = new PrintWriter(sw);
      context.error.printStackTrace(pw);
      metrics.put(Metrics.error_stacktrace, sw.toString());
    } else if (context != context.methodResult) {
      metrics.put(Metrics.method_result, context.methodResult);
      if (context.methodResult instanceof ResponseEntity) {
        ResponseEntity r = (ResponseEntity) context.methodResult;
        metrics.put(Metrics.http_code, r.getStatusCodeValue());
        Object body = r.getBody();
        if (null != body) metrics.put(Metrics.http_body_type, body.getClass().getName());
      }
    }
  }
}
