/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.authorization.webhook;

import com.vmware.taurus.authorization.AuthorizationInterceptor;
import com.vmware.taurus.exception.AuthorizationError;
import com.vmware.taurus.exception.ExternalSystemError;
import com.vmware.taurus.service.webhook.WebHookRequestBody;
import com.vmware.taurus.service.webhook.WebHookResult;
import com.vmware.taurus.service.webhook.WebHookService;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

/**
 * AuthorizationWebhookProvider class which delegates authorization request to a third party webhook
 * authorization server.
 *
 * <p>Uses a single method {@link WebHookService#invokeWebHook(WebHookRequestBody)} which triggers a
 * webhook to the actual authorization server to determine whether a user is authorized or not by
 * creating {@link WebHookResult} which is then provided to {@link AuthorizationInterceptor}
 */
@Service
@Slf4j
public class AuthorizationWebHookProvider extends WebHookService<AuthorizationBody> {

  public AuthorizationWebHookProvider(
      @Value("${datajobs.authorization.webhook.endpoint}") String webHookEndpoint,
      @Value("${datajobs.authorization.webhook.internal.errors.retries:1}")
          int retriesOn5xxErrors) {
    super(webHookEndpoint, retriesOn5xxErrors, log);
  }

  @Override
  public void ensureConfigured() {
    if (StringUtils.isBlank(getWebHookEndpoint())) {
      throw new AuthorizationError(
          "Authorization webhook endpoint is not configured",
          "Cannot determine whether a user is authorized to do this request",
          "Configure the authorization webhook property or disable the feature altogether",
          null);
    }
  }

  @Override
  protected String getWebHookRequestURL(AuthorizationBody webHookRequestBody) {
    return getWebHookEndpoint();
  }

  @Override
  public ExternalSystemError.MainExternalSystem getExternalSystemType() {
    return ExternalSystemError.MainExternalSystem.AUTHORIZATION_SERVER;
  }
}
