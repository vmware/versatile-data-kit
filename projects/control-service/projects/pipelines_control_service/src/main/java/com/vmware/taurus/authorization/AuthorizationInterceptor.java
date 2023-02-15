/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.authorization;

import com.vmware.taurus.authorization.provider.AuthorizationProvider;
import com.vmware.taurus.authorization.webhook.AuthorizationBody;
import com.vmware.taurus.authorization.webhook.AuthorizationWebHookProvider;
import com.vmware.taurus.base.FeatureFlags;
import com.vmware.taurus.service.diag.OperationContext;
import com.vmware.taurus.service.webhook.WebHookResult;
import lombok.RequiredArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;
import org.springframework.web.servlet.HandlerInterceptor;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;

/**
 * Intercept before any method invocation.
 *
 * <p>If a service does not need authorization it can be disabled with feature flag:
 * featureflag.authorization.disabled=true 1. If the HTTP method is GET - allowed if the user is
 * authenticated 2. Other methods create {@link AuthorizationBody} and delegate authorization
 * decision to {@link AuthorizationWebHookProvider}
 */
@Component
@RequiredArgsConstructor
public class AuthorizationInterceptor implements HandlerInterceptor {

  private static Logger log = LoggerFactory.getLogger(AuthorizationInterceptor.class);

  private final FeatureFlags featureFlags;

  private final AuthorizationWebHookProvider webhookProvider;

  private final AuthorizationProvider authorizationProvider;

  private final OperationContext opCtx;

  @Override
  public boolean preHandle(
      final HttpServletRequest request, final HttpServletResponse response, final Object handler)
      throws IOException {
    if (featureFlags.isSecurityEnabled()) {
      Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
      if (authentication != null && authentication.isAuthenticated()) {
        AuthorizationBody body =
            authorizationProvider.createAuthorizationBody(request, authentication);
        updateOperationContext(body);
        if (featureFlags.isAuthorizationEnabled()) {
          return isRequestAuthorized(request, response, body);
        }
      }
      // If we are at this stage - either we are authenticated or authentication is disabled for
      // that endpoint
      return true;
    }
    return true;
  }

  private boolean isRequestAuthorized(
      HttpServletRequest request, HttpServletResponse response, AuthorizationBody body)
      throws IOException {
    WebHookResult decision = this.webhookProvider.invokeWebHook(body).get();
    response.setStatus(decision.getStatus().value());
    if (!decision.getMessage().isBlank()) {
      response.getWriter().write(decision.getMessage());
    }
    return decision.isSuccess();
  }

  private void updateOperationContext(AuthorizationBody body) {
    opCtx.setUser(body.getRequesterUserId());
    opCtx.setTeam(body.getRequestedResourceTeam());
  }
}
