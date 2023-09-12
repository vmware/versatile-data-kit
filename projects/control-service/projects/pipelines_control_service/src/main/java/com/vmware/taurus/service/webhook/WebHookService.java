/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.webhook;

import com.vmware.taurus.authorization.provider.AuthorizationProvider;
import com.vmware.taurus.base.FeatureFlags;
import com.vmware.taurus.exception.ExternalSystemError;
import lombok.RequiredArgsConstructor;
import org.apache.commons.lang3.StringUtils;
import org.slf4j.Logger;
import org.springframework.beans.factory.InitializingBean;
import org.springframework.http.*;
import org.springframework.web.client.RestClientResponseException;
import org.springframework.web.client.RestTemplate;

import java.util.Optional;

/**
 * WebHook Provider abstraction that provides a template for the invocation of a WebHook. It is not
 * expected to use this service directly (hence abstract), instead provide a specific implementation
 * that provides the webHookEndpoint, retriesOn5xxErrors and possibly other details in the future.
 *
 * <p>For examples of the existing implementations:
 *
 * @see com.vmware.taurus.datajobs.webhook.PostDeleteWebHookProvider
 * @see com.vmware.taurus.datajobs.webhook.PostCreateWebHookProvider
 * @see com.vmware.taurus.authorization.webhook.AuthorizationWebHookProvider
 */
@RequiredArgsConstructor
public abstract class WebHookService<T extends WebHookRequestBody> implements InitializingBean {

  protected final String webHookEndpoint;

  private final int retriesOn5xxErrors;

  private final boolean authenticationEnabled;

  private final String authorizationServerEndpoint;

  private final String refreshToken;

  private final Logger log;

  private final RestTemplate restTemplate;

  private final FeatureFlags featureFlags;

  private final AuthorizationProvider authorizationProvider;

  public Optional<WebHookResult> invokeWebHook(T webHookRequestBody) {
    ensureConfigured();

    if (StringUtils.isBlank(webHookEndpoint)) {
      log.debug("The webHook Endpoint is not configured. Requests will not be send ...");
      return Optional.empty();
    }

    ResponseEntity responseEntity = sendRequest(webHookRequestBody);

    if (responseEntity.getStatusCode().is5xxServerError()) {
      log.debug("The WebHook invocation {} returns 5xxServerError ...", webHookEndpoint);
      responseEntity = retry5xxWebHookRequest(webHookRequestBody, responseEntity);
    }
    if (responseEntity.getStatusCode().is4xxClientError()) {
      log.debug("The WebHook invocation {} returns 4xxClientError ...", webHookEndpoint);
      return Optional.of(provideClientErrorMessage(responseEntity));
    }
    if (responseEntity.getStatusCode().is2xxSuccessful()) {
      log.debug("The WebHook invocation {} is successful ...", webHookEndpoint);
      return Optional.of(provideSuccessMessage(responseEntity));
    }

    log.debug(
        "The WebHook invocation {} returns unhandled status code:  {}",
        webHookEndpoint,
        responseEntity.getStatusCode().value());
    ExternalSystemError.MainExternalSystem mainExternalSystem = getExternalSystemType();
    throw new ExternalSystemError(
        mainExternalSystem,
        String.format(
            "Webhook server returned non successful status code: %d",
            responseEntity.getStatusCode().value()));
  }

  private ResponseEntity retry5xxWebHookRequest(
      T webHookRequestBody, ResponseEntity responseEntity) {
    int current5xxServerRetry = 0;
    while (responseEntity.getStatusCode().is5xxServerError()
        && current5xxServerRetry < retriesOn5xxErrors) {
      current5xxServerRetry++;

      log.debug("WebHook retry #{} for the 5xxServerError ...", current5xxServerRetry);
      responseEntity = sendRequest(webHookRequestBody);
    }

    if (current5xxServerRetry == 0) {
      log.debug(
          "No WebHook reties are attempted for the 5xxServerError ...", current5xxServerRetry);
    }
    return responseEntity;
  }

  private ResponseEntity sendRequest(T webHookRequestBody) {
    // TODO: possibly implement custom ResponseErrorHandler and add it to the restTemplate if
    // necessary
    log.info("WebHook body: {}", webHookRequestBody.toString());
    try {
      HttpEntity<WebHookRequestBody> request = createHttpRequest(webHookRequestBody);

      return restTemplate.exchange(
          getWebHookRequestURL(webHookRequestBody), HttpMethod.POST, request, String.class);
    } catch (RestClientResponseException responseException) {
      return new ResponseEntity<>(
          responseException.getResponseBodyAsString(),
          responseException.getResponseHeaders(),
          HttpStatus.resolve(responseException.getRawStatusCode()));
    }
  }

  @Override
  public void afterPropertiesSet() {}

  /**
   * Callback invoked before the execution of the requests to the WebHook server. <br>
   * By default, the service is considered as configured, however this is a good place to throw an
   * exception to break the execution flow. <br>
   * Note: If the webHookEndpoint is not configured, the service will skip the invocation anyway.
   */
  protected void ensureConfigured() {}

  /**
   * Callback that allows the implementations to construct specific Request URL for each request
   * sent to the WebHook server.
   *
   * @param webHookRequestBody the request body that gives the context of the execution
   * @return a valid URL
   */
  protected String getWebHookRequestURL(T webHookRequestBody) {
    return webHookEndpoint + webHookRequestBody.getRequestedHttpPath();
  }

  /**
   * Instruct the system what is the external system type of the webhook server.<br>
   * By default, the external system type is considered as the generic WEBHOOK_SERVER.
   *
   * @return the Main External System Type
   */
  protected ExternalSystemError.MainExternalSystem getExternalSystemType() {
    return ExternalSystemError.MainExternalSystem.WEBHOOK_SERVER;
  }

  /**
   * Construct the Client Error Message based on the response Entity(4xx Response Code) that is
   * returned by the request.
   *
   * @param responseEntity the 4xx response entity of the request
   * @return the Client Error Message
   */
  protected WebHookResult provideClientErrorMessage(ResponseEntity responseEntity) {
    return WebHookResult.builder()
        .status(responseEntity.getStatusCode())
        .message(responseEntity.getBody().toString())
        .success(false)
        .build();
  }

  /**
   * Construct the Success Message based on the response Entity(2xx Response Code) that is returned
   * by the request.
   *
   * @param responseEntity the 2xx response entity of the request
   * @return the Success Message
   */
  protected WebHookResult provideSuccessMessage(ResponseEntity responseEntity) {
    return WebHookResult.builder()
        .status(responseEntity.getStatusCode())
        .message("")
        .success(true)
        .build();
  }

  private HttpEntity<WebHookRequestBody> createHttpRequest(T webHookRequestBody) {
    HttpEntity<WebHookRequestBody> request = null;

    if (featureFlags.isSecurityEnabled() && authenticationEnabled) {
      String accessToken = authorizationProvider.getAccessToken(authorizationServerEndpoint, refreshToken);

      if (StringUtils.isNotEmpty(accessToken)) {
        HttpHeaders httpHeaders = new HttpHeaders();
        httpHeaders.setBearerAuth(accessToken);

        request = new HttpEntity<>(webHookRequestBody, httpHeaders);
      }
    }

    return request != null ? request : new HttpEntity<>(webHookRequestBody);
  }
}
