/*
 * Copyright 2023-2025 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.credentials.webhook;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.vmware.taurus.authorization.AuthorizationInterceptor;
import com.vmware.taurus.authorization.provider.AuthorizationProvider;
import com.vmware.taurus.base.FeatureFlags;
import com.vmware.taurus.exception.AuthorizationError;
import com.vmware.taurus.exception.ExternalSystemError;
import com.vmware.taurus.service.webhook.WebHookRequestBody;
import com.vmware.taurus.service.webhook.WebHookResult;
import com.vmware.taurus.service.webhook.WebHookService;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

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
public class CreateOAuthAppWebHookProvider extends WebHookService<CreateOAuthAppBody> {

  public CreateOAuthAppWebHookProvider(
      @Value("${datajobs.create.oauth.app.webhook.endpoint}") String webHookEndpoint,
      @Value("${datajobs.create.oauth.app.webhook.internal.errors.retries:1}")
          int retriesOn5xxErrors,
      @Value("${datajobs.create.oauth.app.webhook.authentication.enabled:false}")
          boolean authenticationEnabled,
      @Value("${datajobs.create.oauth.app.webhook.authorization.server.endpoint:''}")
          String authorizationServerEndpoint,
      @Value("${datajobs.create.oauth.app.webhook.authorization.refresh.token:''}")
          String refreshToken,
      RestTemplate restTemplate,
      FeatureFlags featureFlags,
      AuthorizationProvider authorizationProvider) {
    super(
        webHookEndpoint,
        retriesOn5xxErrors,
        authenticationEnabled,
        authorizationServerEndpoint,
        refreshToken,
        log,
        restTemplate,
        featureFlags,
        authorizationProvider);
  }

  @Override
  public void ensureConfigured() {
    if (StringUtils.isBlank(webHookEndpoint)) {
      throw new AuthorizationError(
          "Authorization webhook endpoint is not configured",
          "Cannot determine whether a user is authorized to do this request",
          "Configure the authorization webhook property or disable the feature altogether",
          null);
    }
  }

  @Override
  protected String getWebHookRequestURL(CreateOAuthAppBody webHookRequestBody) {
    return webHookEndpoint;
  }

  @Override
  public ExternalSystemError.MainExternalSystem getExternalSystemType() {
    return ExternalSystemError.MainExternalSystem.AUTHORIZATION_SERVER;
  }

  @Override
  protected CreateOAuthAppWebHookResult provideSuccessMessage(ResponseEntity responseEntity) {
    try {
      Object responseBody = responseEntity.getBody();

      // Deserialize the response body into a CreateOAuthAppResponse object
      CreateOAuthAppResponse createOAuthAppResponse = null;
      if (responseBody instanceof String responseBodyString) {
        // If the response body is a String, use ObjectMapper to deserialize it
        ObjectMapper mapper = new ObjectMapper();
        createOAuthAppResponse = mapper.readValue(responseBodyString, CreateOAuthAppResponse.class);
      } else if (responseBody instanceof CreateOAuthAppResponse createOAuthApp) {
        createOAuthAppResponse = createOAuthApp;
      }

      if (createOAuthAppResponse == null) {
        throw new AuthorizationError(
            "Unable to unmarshal team credentials from oauth webhook service response",
            "Cannot create team secret",
            "Check logs of oAuth webhook server",
            null);
      }
      // Access the clientId and clientSecret
      String clientId = createOAuthAppResponse.getClientId();
      String clientSecret = createOAuthAppResponse.getClientSecret();

      return new CreateOAuthAppWebHookResult(
          responseEntity.getStatusCode(), "", true, clientId, clientSecret);
    } catch (Exception e) {
      throw new AuthorizationError(
          "Response from webhook Server doesn't contain needed team credentials",
          "Cannot create team secret",
          "Check logs of oAuth webhook server",
          e);
    }
  }
}
