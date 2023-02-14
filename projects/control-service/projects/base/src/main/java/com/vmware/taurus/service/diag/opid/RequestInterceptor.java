/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.diag.opid;

import com.vmware.taurus.service.diag.OperationContext;
import org.jetbrains.annotations.NotNull;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.Ordered;
import org.springframework.core.annotation.Order;
import org.springframework.stereotype.Component;
import org.springframework.web.servlet.HandlerInterceptor;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

@Component
@Order(Ordered.HIGHEST_PRECEDENCE)
public class RequestInterceptor implements HandlerInterceptor {
  private final Logger log = LoggerFactory.getLogger(this.getClass());

  private OperationContext opCtx;

  @Autowired
  public RequestInterceptor(OperationContext opCtx) {
    this.opCtx = opCtx;
  }

  @Override
  public boolean preHandle(
      HttpServletRequest request, @NotNull HttpServletResponse response, @NotNull Object handler) {
    String opId = request.getHeader("X-OPID");
    if (null == opId) {
      opId = "0" + System.currentTimeMillis();
    }
    opCtx.setId(opId);
    log.debug(">>>>>> Entering {}", request.getRequestURI());
    opCtx.setHttpRequest(request);
    opCtx.setHttpResponse(response);
    return true;
  }

  @Override
  public void afterCompletion(
      HttpServletRequest request,
      @NotNull HttpServletResponse response,
      @NotNull Object handler,
      Exception ex) {
    log.debug("<<<<<<< Exiting {}", request.getRequestURI());
  }
}
