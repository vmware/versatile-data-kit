/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.authorization.webhook;

import com.vmware.taurus.exception.AuthorizationError;
import com.vmware.taurus.exception.ExternalSystemError;
import com.vmware.taurus.service.webhook.WebHookResult;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.Mockito;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.http.*;
import org.springframework.test.util.ReflectionTestUtils;
import org.springframework.web.client.RestClientResponseException;
import org.springframework.web.client.RestTemplate;

import java.io.UnsupportedEncodingException;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;

@ExtendWith(MockitoExtension.class)
public class AuthorizationWebHookProviderTest {

  @Mock private RestTemplate restTemplate;

  @InjectMocks
  private AuthorizationWebHookProvider webhookProvider = new AuthorizationWebHookProvider("", 1);

  private AuthorizationBody authzBody;

  private static String EXPECTED_JSON_BODY =
      "{\"requester_user_id\":\"auserov\","
          + "\"requested_resource_team\":\"\","
          + "\"requested_resource_name\":\"data-job\","
          + "\"requested_resource_id\":\"\","
          + "\"requested_http_path\":\"/data-jobs\","
          + "\"requested_http_verb\":\"POST\","
          + "\"requested_resource_new_team\":\"\","
          + "\"requested_permission\":\"write\"}";

  @BeforeEach
  public void setUp() {
    authzBody = new AuthorizationBody();
    authzBody.setRequestedHttpPath("/data-jobs");
    authzBody.setRequestedHttpVerb("POST");
    authzBody.setRequestedPermission("write");
    authzBody.setRequestedResourceId("");
    authzBody.setRequesterUserId("auserov");
    authzBody.setRequestedResourceTeam("");
    authzBody.setRequestedResourceName("data-job");
    authzBody.setRequestedResourceNewTeam("");
  }

  @Test
  public void testUnauthorizedStatus() throws UnsupportedEncodingException {
    ReflectionTestUtils.setField(webhookProvider, "webHookEndpoint", "http://localhost:4444");
    ResponseEntity re =
        new ResponseEntity<>(
            "Authorization response: User does not have team", null, HttpStatus.UNAUTHORIZED);
    Mockito.when(
            restTemplate.exchange(
                Mockito.anyString(),
                Mockito.any(HttpMethod.class),
                Mockito.any(),
                Mockito.<Class<String>>any()))
        .thenReturn(re);

    WebHookResult decision = webhookProvider.invokeWebHook(authzBody).get();
    Assertions.assertEquals(
        "Authorization response: User does not have team", decision.getMessage());
    Assertions.assertEquals(HttpStatus.UNAUTHORIZED, decision.getStatus());
    Assertions.assertEquals(false, decision.isSuccess());
  }

  @Test
  public void testWebhookAuthorizationSuccess() {
    ReflectionTestUtils.setField(webhookProvider, "webHookEndpoint", "http://localhost:4444");
    ResponseEntity re = new ResponseEntity<>("User authorized", null, HttpStatus.OK);
    Mockito.when(
            restTemplate.exchange(
                Mockito.anyString(),
                Mockito.any(HttpMethod.class),
                Mockito.any(),
                Mockito.<Class<String>>any()))
        .thenReturn(re);

    WebHookResult decision = webhookProvider.invokeWebHook(authzBody).get();
    Assertions.assertEquals("", decision.getMessage());
    Assertions.assertEquals(HttpStatus.OK, decision.getStatus());
    Assertions.assertEquals(true, decision.isSuccess());
  }

  @Test
  public void testRestClientResponseExceptionHandling() {
    ReflectionTestUtils.setField(webhookProvider, "webHookEndpoint", "http://localhost:4444");
    Mockito.when(
            restTemplate.exchange(
                Mockito.anyString(),
                Mockito.any(HttpMethod.class),
                Mockito.any(),
                Mockito.<Class<String>>any()))
        .thenThrow(
            new RestClientResponseException(
                "Server down",
                HttpStatus.UNAUTHORIZED.value(),
                anyString(),
                Mockito.any(HttpHeaders.class),
                any(),
                any()));

    WebHookResult decision = webhookProvider.invokeWebHook(authzBody).get();
    Assertions.assertEquals("", decision.getMessage());
    Assertions.assertEquals(HttpStatus.UNAUTHORIZED, decision.getStatus());
    Assertions.assertEquals(false, decision.isSuccess());
  }

  @Test
  public void testInformationalStatusCode() {
    ReflectionTestUtils.setField(webhookProvider, "webHookEndpoint", "http://localhost:4444");
    ResponseEntity re = new ResponseEntity<>("User authorized", null, HttpStatus.CONTINUE);
    Mockito.when(
            restTemplate.exchange(
                Mockito.anyString(),
                Mockito.any(HttpMethod.class),
                Mockito.any(),
                Mockito.<Class<String>>any()))
        .thenReturn(re);

    Assertions.assertThrows(
        ExternalSystemError.class, () -> webhookProvider.invokeWebHook(authzBody));
  }

  @Test
  public void testRedirectionStatusCode() {
    ReflectionTestUtils.setField(webhookProvider, "webHookEndpoint", "http://localhost:4444");
    ResponseEntity re = new ResponseEntity<>("User authorized", null, HttpStatus.MOVED_PERMANENTLY);
    Mockito.when(
            restTemplate.exchange(
                Mockito.anyString(),
                Mockito.any(HttpMethod.class),
                Mockito.any(),
                Mockito.<Class<String>>any()))
        .thenReturn(re);

    Assertions.assertThrows(
        ExternalSystemError.class, () -> webhookProvider.invokeWebHook(authzBody));
  }

  @Test
  public void testServiceUnavailable() {
    ReflectionTestUtils.setField(webhookProvider, "webHookEndpoint", "http://localhost:4444");
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
        ExternalSystemError.class, () -> webhookProvider.invokeWebHook(authzBody));
  }

  @Test
  public void testWebhookEndpointMissing() {
    ReflectionTestUtils.setField(webhookProvider, "webHookEndpoint", "");

    Assertions.assertThrows(
        AuthorizationError.class, () -> webhookProvider.invokeWebHook(authzBody));
  }

  @Test
  public void testExchangeCalledWithValid() {
    // TODO: probably we should add that argument validation test logic to other tests
    ReflectionTestUtils.setField(webhookProvider, "webHookEndpoint", "http://localhost:4444");

    ResponseEntity re = new ResponseEntity<>("User authorized", null, HttpStatus.OK);

    ArgumentCaptor<String> urlArgument = ArgumentCaptor.forClass(String.class);
    ArgumentCaptor<HttpMethod> httpMethodArgument = ArgumentCaptor.forClass(HttpMethod.class);
    ArgumentCaptor<HttpEntity> httpEntityArgument = ArgumentCaptor.forClass(HttpEntity.class);
    ArgumentCaptor<Class> classArgument = ArgumentCaptor.forClass(Class.class);
    Mockito.when(
            restTemplate.exchange(
                urlArgument.capture(),
                httpMethodArgument.capture(),
                httpEntityArgument.capture(),
                classArgument.capture()))
        .thenReturn(re);

    webhookProvider.invokeWebHook(authzBody);

    String actualUrlArgument = urlArgument.getValue();
    HttpMethod actualMethodArgument = httpMethodArgument.getValue();
    HttpEntity actualEntityArgument = httpEntityArgument.getValue();
    Class actualClassArgument = classArgument.getValue();

    Assertions.assertEquals("http://localhost:4444", actualUrlArgument);
    Assertions.assertEquals(HttpMethod.POST, actualMethodArgument);
    Assertions.assertEquals(EXPECTED_JSON_BODY, actualEntityArgument.getBody().toString());
    Assertions.assertEquals(String.class, actualClassArgument);
  }
}
