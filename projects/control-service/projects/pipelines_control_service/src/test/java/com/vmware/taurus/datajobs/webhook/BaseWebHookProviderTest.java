/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs.webhook;

import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.authorization.provider.AuthorizationProvider;
import com.vmware.taurus.base.FeatureFlags;
import com.vmware.taurus.exception.ExternalSystemError;
import com.vmware.taurus.service.webhook.WebHookRequestBody;
import com.vmware.taurus.service.webhook.WebHookResult;
import com.vmware.taurus.service.webhook.WebHookService;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.Mockito;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.*;
import org.springframework.test.context.TestPropertySource;
import org.springframework.test.context.junit.jupiter.SpringExtension;
import org.springframework.test.util.ReflectionTestUtils;
import org.springframework.web.client.HttpClientErrorException;
import org.springframework.web.client.RestTemplate;

import java.util.List;

import static org.mockito.Mockito.when;

@ExtendWith(SpringExtension.class)
@SpringBootTest(
    webEnvironment = SpringBootTest.WebEnvironment.MOCK,
    classes = ControlplaneApplication.class)
@TestPropertySource(properties = {"featureflag.security.enabled=false"})
public abstract class BaseWebHookProviderTest {

  private static final int ONE_RETRY = 1;
  private static final int INVOCATION_PLUS_ONE_RETRY_COUNT = 2;
  private static final int SINGLE_INVOCATION_COUNT = 1;

  WebHookRequestBody requestBody;

  @MockBean private RestTemplate restTemplate;

  @MockBean private FeatureFlags featureFlags;

  @MockBean private AuthorizationProvider authorizationProvider;

  abstract WebHookService<WebHookRequestBody> getWebHookProvider();

  @BeforeEach
  public void setUp() {
    ReflectionTestUtils.setField(getWebHookProvider(), "webHookEndpoint", "http://localhost:4444");
    requestBody = new WebHookRequestBody();
    requestBody.setRequestedHttpPath("/data-jobs");
    requestBody.setRequestedHttpVerb("SOME");
    requestBody.setRequestedResourceId(null);
    requestBody.setRequesterUserId("auserov");
    requestBody.setRequestedResourceTeam(null);
    requestBody.setRequestedResourceName("data-job");
  }

  @Test
  public void testBadRequestStatus() {
    ResponseEntity re =
        new ResponseEntity<>(
            "Bad request: The post create action needs more parameters",
            null,
            HttpStatus.BAD_REQUEST);
    when(restTemplate.exchange(
            Mockito.anyString(),
            Mockito.any(HttpMethod.class),
            Mockito.any(),
            Mockito.<Class<String>>any()))
        .thenReturn(re);

    WebHookResult webHookResult = getWebHookProvider().invokeWebHook(requestBody).get();
    Assertions.assertEquals(
        "Bad request: The post create action needs more parameters", webHookResult.getMessage());
    Assertions.assertEquals(HttpStatus.BAD_REQUEST, webHookResult.getStatus());
    Assertions.assertEquals(false, webHookResult.isSuccess());
  }

  @Test
  public void testWebHookSuccess() {
    ResponseEntity re = new ResponseEntity<>("Good request", null, HttpStatus.ACCEPTED);
    when(restTemplate.exchange(
            Mockito.anyString(),
            Mockito.any(HttpMethod.class),
            Mockito.any(),
            Mockito.<Class<String>>any()))
        .thenReturn(re);

    WebHookResult webHookResult = getWebHookProvider().invokeWebHook(requestBody).get();
    Assertions.assertEquals("", webHookResult.getMessage());
    Assertions.assertEquals(HttpStatus.ACCEPTED, webHookResult.getStatus());
    Assertions.assertEquals(true, webHookResult.isSuccess());
  }

  @Test
  public void testRestClientResponseExceptionHandling() {
    when(restTemplate.exchange(
            Mockito.anyString(),
            Mockito.any(HttpMethod.class),
            Mockito.any(),
            Mockito.<Class<String>>any()))
        .thenThrow(HttpClientErrorException.create(HttpStatus.BAD_REQUEST, "", null, null, null));

    WebHookResult webHookResult = getWebHookProvider().invokeWebHook(requestBody).get();
    Assertions.assertEquals("", webHookResult.getMessage());
    Assertions.assertEquals(HttpStatus.BAD_REQUEST, webHookResult.getStatus());
    Assertions.assertEquals(false, webHookResult.isSuccess());
  }

  @Test
  public void testInformationalStatusCode() {
    ResponseEntity re = new ResponseEntity<>("User authorized", null, HttpStatus.CONTINUE);
    when(restTemplate.exchange(
            Mockito.anyString(),
            Mockito.any(HttpMethod.class),
            Mockito.any(),
            Mockito.<Class<String>>any()))
        .thenReturn(re);

    Assertions.assertThrows(
        ExternalSystemError.class, () -> getWebHookProvider().invokeWebHook(requestBody));
  }

  @Test
  public void testRedirectionStatusCode() {
    ResponseEntity re = new ResponseEntity<>("User authorized", null, HttpStatus.MOVED_PERMANENTLY);
    when(restTemplate.exchange(
            Mockito.anyString(),
            Mockito.any(HttpMethod.class),
            Mockito.any(),
            Mockito.<Class<String>>any()))
        .thenReturn(re);

    Assertions.assertThrows(
        ExternalSystemError.class, () -> getWebHookProvider().invokeWebHook(requestBody));
  }

  @Test
  public void testServiceUnavailableWithRetry() {
    ReflectionTestUtils.setField(getWebHookProvider(), "retriesOn5xxErrors", ONE_RETRY);
    ResponseEntity re =
        new ResponseEntity<>("Service unavailable", null, HttpStatus.SERVICE_UNAVAILABLE);
    when(restTemplate.exchange(
            Mockito.anyString(),
            Mockito.any(HttpMethod.class),
            Mockito.any(),
            Mockito.<Class<String>>any()))
        .thenReturn(re);

    Assertions.assertThrows(
        ExternalSystemError.class, () -> getWebHookProvider().invokeWebHook(requestBody));
    Mockito.verify(restTemplate, Mockito.times(INVOCATION_PLUS_ONE_RETRY_COUNT))
        .exchange(
            Mockito.anyString(),
            Mockito.any(HttpMethod.class),
            Mockito.any(),
            Mockito.<Class<String>>any());
  }

  @Test
  public void testInternalErrorDefaultNoRetry() {
    ResponseEntity re =
        new ResponseEntity<>("Internal Server error", null, HttpStatus.INTERNAL_SERVER_ERROR);
    when(restTemplate.exchange(
            Mockito.anyString(),
            Mockito.any(HttpMethod.class),
            Mockito.any(),
            Mockito.<Class<String>>any()))
        .thenReturn(re);

    Assertions.assertThrows(
        ExternalSystemError.class, () -> getWebHookProvider().invokeWebHook(requestBody));
    Mockito.verify(restTemplate, Mockito.times(SINGLE_INVOCATION_COUNT))
        .exchange(
            Mockito.anyString(),
            Mockito.any(HttpMethod.class),
            Mockito.any(),
            Mockito.<Class<String>>any());
  }

  @Test
  public void testWebHookEndpointNotConfigured() {
    ReflectionTestUtils.setField(getWebHookProvider(), "webHookEndpoint", "");

    Assertions.assertTrue(getWebHookProvider().invokeWebHook(requestBody).isEmpty());
  }

  @Test
  public void testInvokeWebHook_withAuthenticationEnabled_shouldContainAuthorizationHttpHeader() {
    String expectedAccessToken = "testAccessToken";

    ReflectionTestUtils.setField(getWebHookProvider(), "authenticationEnabled", true);
    when(featureFlags.isSecurityEnabled()).thenReturn(true);
    when(authorizationProvider.getAccessToken()).thenReturn(expectedAccessToken);

    ResponseEntity re = new ResponseEntity<>("Good request", null, HttpStatus.ACCEPTED);
    when(restTemplate.exchange(
            Mockito.anyString(),
            Mockito.any(HttpMethod.class),
            Mockito.any(),
            Mockito.<Class<String>>any()))
        .thenReturn(re);

    getWebHookProvider().invokeWebHook(requestBody);

    ArgumentCaptor<HttpEntity> httpEntityCaptor = ArgumentCaptor.forClass(HttpEntity.class);
    Mockito.verify(restTemplate, Mockito.times(SINGLE_INVOCATION_COUNT))
        .exchange(
            Mockito.anyString(),
            Mockito.any(HttpMethod.class),
            httpEntityCaptor.capture(),
            Mockito.<Class<String>>any());

    List<String> authorizationHttpHeader =
        httpEntityCaptor.getValue().getHeaders().get(HttpHeaders.AUTHORIZATION);
    Assertions.assertNotNull(authorizationHttpHeader);
    Assertions.assertEquals(1, authorizationHttpHeader.size());
    Assertions.assertEquals("Bearer " + expectedAccessToken, authorizationHttpHeader.get(0));
  }

  @Test
  public void
      testInvokeWebHook_withAuthenticationDisabled_shouldNotContainAuthorizationHttpHeader() {
    String expectedAccessToken = "testAccessToken";

    ReflectionTestUtils.setField(getWebHookProvider(), "authenticationEnabled", false);
    when(featureFlags.isSecurityEnabled()).thenReturn(true);
    when(authorizationProvider.getAccessToken()).thenReturn(expectedAccessToken);

    ResponseEntity re = new ResponseEntity<>("Good request", null, HttpStatus.ACCEPTED);
    when(restTemplate.exchange(
            Mockito.anyString(),
            Mockito.any(HttpMethod.class),
            Mockito.any(),
            Mockito.<Class<String>>any()))
        .thenReturn(re);

    getWebHookProvider().invokeWebHook(requestBody);

    ArgumentCaptor<HttpEntity> httpEntityCaptor = ArgumentCaptor.forClass(HttpEntity.class);
    Mockito.verify(restTemplate, Mockito.times(SINGLE_INVOCATION_COUNT))
        .exchange(
            Mockito.anyString(),
            Mockito.any(HttpMethod.class),
            httpEntityCaptor.capture(),
            Mockito.<Class<String>>any());

    List<String> authorizationHttpHeader =
        httpEntityCaptor.getValue().getHeaders().get(HttpHeaders.AUTHORIZATION);
    Assertions.assertNull(authorizationHttpHeader);
  }
}
