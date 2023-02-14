/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.diag.opid;

import com.vmware.taurus.service.diag.OperationContext;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.MethodParameter;
import org.springframework.http.MediaType;
import org.springframework.http.converter.HttpMessageConverter;
import org.springframework.http.server.ServerHttpRequest;
import org.springframework.http.server.ServerHttpResponse;
import org.springframework.web.bind.annotation.ControllerAdvice;
import org.springframework.web.servlet.mvc.method.annotation.ResponseBodyAdvice;

/** This class applies header response of opID across all controllers. */
@ControllerAdvice
public class ResponseOpIdSetterAdvice implements ResponseBodyAdvice<Object> {
  private final Logger log = LoggerFactory.getLogger(this.getClass());
  private OperationContext opCtx;

  @Autowired
  public ResponseOpIdSetterAdvice(OperationContext opCtx) {
    this.opCtx = opCtx;
  }

  @Override
  public boolean supports(
      MethodParameter returnType, Class<? extends HttpMessageConverter<?>> converterType) {
    return true;
  }

  @Override
  public Object beforeBodyWrite(
      Object body,
      MethodParameter returnType,
      MediaType selectedContentType,
      Class<? extends HttpMessageConverter<?>> selectedConverterType,
      ServerHttpRequest request,
      ServerHttpResponse response) {
    String opId = opCtx.getOpId();
    log.trace("Setting 'X-OPID:{}' header in response", opId);
    response.getHeaders().add("X-OPID", opId);
    return body;
  }
}
