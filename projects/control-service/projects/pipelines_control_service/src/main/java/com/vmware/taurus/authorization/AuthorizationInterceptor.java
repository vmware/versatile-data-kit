/*
 * Copyright 2023-2025 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.authorization;

import com.vmware.taurus.authorization.provider.AuthorizationProvider;
import com.vmware.taurus.authorization.webhook.AuthorizationBody;
import com.vmware.taurus.authorization.webhook.AuthorizationWebHookProvider;
import com.vmware.taurus.base.FeatureFlags;
import com.vmware.taurus.secrets.service.JobSecretsService;
import com.vmware.taurus.secrets.service.vault.VaultTeamCredentials;
import com.vmware.taurus.service.diag.OperationContext;
import com.vmware.taurus.service.webhook.WebHookResult;
import lombok.RequiredArgsConstructor;
import org.apache.commons.lang3.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.lang.Nullable;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.oauth2.core.OAuth2TokenIntrospectionClaimNames;
import org.springframework.security.oauth2.server.resource.authentication.JwtAuthenticationToken;
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

  @Value("${datajobs.authorization.jwt.claim.username}")
  private String usernameField;

  private static Logger log = LoggerFactory.getLogger(AuthorizationInterceptor.class);

  private final FeatureFlags featureFlags;

  private final AuthorizationWebHookProvider webhookProvider;

  private final AuthorizationProvider authorizationProvider;

  private final OperationContext opCtx;

  @Nullable private final JobSecretsService secretsService;

  @Override
  public boolean preHandle(
      final HttpServletRequest request, final HttpServletResponse response, final Object handler)
      throws IOException {
    // Is security enabled at all?
    if (!featureFlags.isSecurityEnabled()) {
      return true;
    }

    // Is authorization enabled? Did we get a token?
    // This logic is somewhat scatchy, but I've kept the old behavior
    Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
    if (!featureFlags.isAuthorizationEnabled()
        || authentication == null
        || !authentication.isAuthenticated()) {
      return true;
    }

    // This logic is somewhat scatchy, but I've kept the old behavior
    if (!(authentication instanceof JwtAuthenticationToken jwtToken)) {
      return true;
    }

    if (jwtToken.getTokenAttributes().get(usernameField) != null) {
      return handleVmwCspToken(request, response, jwtToken);
    } else if (secretsService != null) {
      return handleOAuthApplicationToken(request, jwtToken);
    }

    return true;
  }

  private boolean handleVmwCspToken(
      HttpServletRequest request, HttpServletResponse response, JwtAuthenticationToken token)
      throws IOException {
    AuthorizationBody body = authorizationProvider.createAuthorizationBody(request, token);
    updateOperationContext(body);
    return isRequestAuthorized(request, response, body);
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

  private boolean handleOAuthApplicationToken(
      HttpServletRequest request, JwtAuthenticationToken token) {
    Object tokenSubject = token.getTokenAttributes().get(OAuth2TokenIntrospectionClaimNames.SUB);
    if (!(tokenSubject instanceof String subject)) {
      return false;
    }

    String teamClientId = StringUtils.substringAfter(subject, ":");
    String teamName = authorizationProvider.getJobTeam(request);

    VaultTeamCredentials teamCredentials = secretsService.readTeamOauthCredentials(teamName);
    return teamCredentials != null && teamClientId.equals(teamCredentials.getClientId());
  }
}
