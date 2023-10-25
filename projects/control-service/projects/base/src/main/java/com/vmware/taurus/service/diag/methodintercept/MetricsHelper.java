/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.diag.methodintercept;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.vmware.taurus.service.diag.Metrics;
import lombok.extern.slf4j.Slf4j;
import org.aspectj.lang.JoinPoint;
import org.aspectj.lang.reflect.MethodSignature;

import java.util.*;

@Slf4j
public class MetricsHelper {

  private static final ObjectMapper mapper = new ObjectMapper();

  public void signatureToMetricsAboutJavaMethod(
      MethodSignature signature, Map<Metrics, Object> metrics) {
    String classNameCanonical = signature.getDeclaringType().getCanonicalName();
    String classNameSimple = signature.getDeclaringType().getSimpleName();
    String methodName = signature.getName();
    metrics.put(Metrics.method_name, methodName);
    metrics.put(Metrics.class_name_short, classNameSimple);
    metrics.put(Metrics.class_name_full, classNameCanonical);
  }

  public void joinPointToMetricsAboutMeasurable(JoinPoint joinPoint, Map<Metrics, Object> metrics) {
    MethodSignature signature = (MethodSignature) joinPoint.getSignature();
    List<Measurable> measurables = getMeasurables(signature);
    if (!measurables.isEmpty()) {
      Map<String, Object> measurableArgs = new LinkedHashMap();
      Set<String> tags = new LinkedHashSet<>();
      for (Measurable measurable : measurables) {
        Object arg = joinPoint.getArgs()[measurable.includeArg()];
        measurableArgs.put(measurable.argName(), arg);
        tags.addAll(Arrays.asList(measurable.tags()));
      }
      if (measurableArgs.size() > 0) {
        metrics.put(Metrics.measurable_args, serializeObject(measurableArgs));
      }
      if (tags.size() > 0) {
        String measurableTags = "" + tags;
        metrics.put(Metrics.measurable_tags, measurableTags);
      }
    }
  }

  private static List<Measurable> getMeasurables(MethodSignature signature) {
    MeasurableContainer measurableContainer =
        signature.getMethod().getAnnotation(MeasurableContainer.class);
    Measurable measurableAnnotation = signature.getMethod().getAnnotation(Measurable.class);
    List<Measurable> measurables = Collections.emptyList();
    if (null != measurableContainer) {
      measurables = Arrays.asList(measurableContainer.value());
    } else if (null != measurableAnnotation) {
      measurables = Collections.singletonList(measurableAnnotation);
    }
    return measurables;
  }

  /** Tries to convert it to json and if it fails falls back to "toString()" */
  private static String serializeObject(Object obj) {
    if (obj == null) {
      return null;
    }
    String result = "";
    try {
      mapper.setSerializationInclusion(JsonInclude.Include.NON_NULL);
      result = mapper.writeValueAsString(obj);
    } catch (JsonProcessingException e) {
      log.trace("Failed to convert object to json: {}: {}", obj.getClass(), e.getMessage());
      result = "" + obj;
    }
    return result;
  }
}
