/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs.webhook;

import com.vmware.taurus.authorization.provider.AuthorizationProvider;
import com.vmware.taurus.base.FeatureFlags;
import com.vmware.taurus.service.webhook.WebHookRequestBody;
import com.vmware.taurus.service.webhook.WebHookService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

/**
 * PostCreateWebHookProvider class which delegates custom post data job creation operations via a
 * request to a third party webhook server.
 *
 * <p>Uses a single method {@link PostCreateWebHookProvider#invokeWebHook(WebHookRequestBody)} which
 * triggers a webhook to a server to execute various Post Create Data Jobs operations.
 */
@Service
@Slf4j
public class PostCreateWebHookProvider extends WebHookService<WebHookRequestBody> {

  public PostCreateWebHookProvider(
      @Value("${datajobs.post.create.webhook.endpoint}") String webHookEndpoint,
      @Value("${datajobs.post.create.webhook.internal.errors.retries:-1}") int retriesOn5xxErrors,
      @Value("${datajobs.post.create.webhook.authentication.enabled:false}") boolean authenticationEnabled,
      RestTemplate restTemplate,
      FeatureFlags featureFlags,
      AuthorizationProvider authorizationProvider) {
    super(webHookEndpoint, retriesOn5xxErrors, authenticationEnabled, log, restTemplate, featureFlags, authorizationProvider);
  }
}
