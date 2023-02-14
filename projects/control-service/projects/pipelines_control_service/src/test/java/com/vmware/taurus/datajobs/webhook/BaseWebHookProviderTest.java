/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs.webhook;

import com.vmware.taurus.exception.ExternalSystemError;
import com.vmware.taurus.service.webhook.WebHookRequestBody;
import com.vmware.taurus.service.webhook.WebHookResult;
import com.vmware.taurus.service.webhook.WebHookService;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.Mockito;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.test.util.ReflectionTestUtils;
import org.springframework.web.client.RestClientResponseException;
import org.springframework.web.client.RestTemplate;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;

@ExtendWith(MockitoExtension.class)
public abstract class BaseWebHookProviderTest {

  private static final int ONE_RETRY = 1;
  private static final int INVOCATION_PLUS_ONE_RETRY_COUNT = 2;
  private static final int SINGLE_INVOCATION_COUNT = 1;

  @Mock RestTemplate restTemplate;

  WebHookRequestBody requestBody;

  abstract WebHookService<WebHookRequestBody> getWebHookProvider();

  @BeforeEach
  public void setUp() {
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
    ReflectionTestUtils.setField(getWebHookProvider(), "webHookEndpoint", "http://localhost:4444");
    ResponseEntity re =
        new ResponseEntity<>(
            "Bad request: The post create action needs more parameters",
            null,
            HttpStatus.BAD_REQUEST);
    Mockito.when(
            restTemplate.exchange(
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
    ReflectionTestUtils.setField(getWebHookProvider(), "webHookEndpoint", "http://localhost:4444");
    ResponseEntity re = new ResponseEntity<>("Good request", null, HttpStatus.ACCEPTED);
    Mockito.when(
            restTemplate.exchange(
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
    ReflectionTestUtils.setField(getWebHookProvider(), "webHookEndpoint", "http://localhost:4444");
    Mockito.when(
            restTemplate.exchange(
                Mockito.anyString(),
                Mockito.any(HttpMethod.class),
                Mockito.any(),
                Mockito.<Class<String>>any()))
        .thenThrow(
            new RestClientResponseException(
                "Bad request",
                HttpStatus.BAD_REQUEST.value(),
                anyString(),
                Mockito.any(HttpHeaders.class),
                any(),
                any()));

    WebHookResult webHookResult = getWebHookProvider().invokeWebHook(requestBody).get();
    Assertions.assertEquals("", webHookResult.getMessage());
    Assertions.assertEquals(HttpStatus.BAD_REQUEST, webHookResult.getStatus());
    Assertions.assertEquals(false, webHookResult.isSuccess());
  }

  @Test
  public void testInformationalStatusCode() {
    ReflectionTestUtils.setField(getWebHookProvider(), "webHookEndpoint", "http://localhost:4444");
    ResponseEntity re = new ResponseEntity<>("User authorized", null, HttpStatus.CONTINUE);
    Mockito.when(
            restTemplate.exchange(
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
    ReflectionTestUtils.setField(getWebHookProvider(), "webHookEndpoint", "http://localhost:4444");
    ResponseEntity re = new ResponseEntity<>("User authorized", null, HttpStatus.MOVED_PERMANENTLY);
    Mockito.when(
            restTemplate.exchange(
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
    ReflectionTestUtils.setField(getWebHookProvider(), "webHookEndpoint", "http://localhost:4444");
    ReflectionTestUtils.setField(getWebHookProvider(), "retriesOn5xxErrors", ONE_RETRY);
    ResponseEntity re =
        new ResponseEntity<>("Service unavailable", null, HttpStatus.SERVICE_UNAVAILABLE);
    Mockito.when(
            restTemplate.exchange(
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
    ReflectionTestUtils.setField(getWebHookProvider(), "webHookEndpoint", "http://localhost:4444");
    ResponseEntity re =
        new ResponseEntity<>("Internal Server error", null, HttpStatus.INTERNAL_SERVER_ERROR);
    Mockito.when(
            restTemplate.exchange(
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
}
