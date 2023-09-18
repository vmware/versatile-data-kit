/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.authorization.provider;

import com.vmware.taurus.authorization.webhook.AuthorizationBody;
import com.vmware.taurus.service.model.JobConfig;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.Mockito;
import org.mockito.MockitoAnnotations;
import org.mockito.junit.jupiter.MockitoExtension;
import org.mockito.junit.jupiter.MockitoSettings;
import org.mockito.quality.Strictness;
import org.springframework.security.oauth2.server.resource.authentication.JwtAuthenticationToken;
import org.springframework.test.util.ReflectionTestUtils;
import org.springframework.web.client.RestTemplate;

import javax.servlet.http.HttpServletRequest;
import java.util.Map;

import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.mock;

@ExtendWith(MockitoExtension.class)
@MockitoSettings(strictness = Strictness.LENIENT)
public class AuthorizationProviderTest {

  @Mock private RestTemplate restTemplate;

  @InjectMocks private AuthorizationProvider provider;

  @BeforeEach
  public void setUp() {
    ReflectionTestUtils.setField(provider, "usernameField", "username");
    JobConfig config = new JobConfig();
    config.setTeam("job-repo-example-team");
    MockitoAnnotations.initMocks(this);
  }

  @Test
  public void testParsePropertyFromURI() {
    var provider = new AuthorizationProvider(restTemplate);
    String createJob =
        provider.parsePropertyFromURI("", "/data-jobs/for-team/example-team/jobs", 5);
    String createJobSlash =
        provider.parsePropertyFromURI("", "/data-jobs/for-team/example-team/jobs/", 5);
    String jobNameService =
        provider.parsePropertyFromURI("", "/data-jobs/for-team/example-team/jobs/example", 5);
    String jobNameDeploy =
        provider.parsePropertyFromURI(
            "", "/data-jobs/for-team/example-team/jobs/example/deployments", 5);
    String jobNameServiceSlash =
        provider.parsePropertyFromURI("", "/data-jobs/for-team/example-team/jobs/example/", 5);

    String newTeamName =
        provider.parsePropertyFromURI(
            "", "/data-jobs/for-team/example-team/jobs/example/team/new-example-team", 7);
    String newTeamNameSlash =
        provider.parsePropertyFromURI(
            "", "/data-jobs/for-team/example-team/jobs/example/team/new-example-team/", 7);
    String newTeamNameMissing =
        provider.parsePropertyFromURI("", "/data-jobs/for-team/example-team/jobs", 7);

    String teamName = provider.parsePropertyFromURI("", "/data-jobs/for-team/example-team/jobs", 3);
    String teamNameSlash =
        provider.parsePropertyFromURI("", "/data-jobs/for-team/example-team/jobs/", 3);
    String teamNameMissing = provider.parsePropertyFromURI("", "/data-jobs/for-team/", 3);

    Assertions.assertEquals("", createJob);
    Assertions.assertEquals("", createJobSlash);
    Assertions.assertEquals("example", jobNameService);
    Assertions.assertEquals("example", jobNameDeploy);
    Assertions.assertEquals("example", jobNameServiceSlash);

    Assertions.assertEquals("new-example-team", newTeamName);
    Assertions.assertEquals("new-example-team", newTeamNameSlash);
    Assertions.assertEquals("", newTeamNameMissing);

    Assertions.assertEquals("example-team", teamName);
    Assertions.assertEquals("example-team", teamNameSlash);
    Assertions.assertEquals("", teamNameMissing);
  }

  @Test
  public void testParseJobNameFromURIContext() {
    var provider = new AuthorizationProvider(restTemplate);
    String createJob =
        provider.parsePropertyFromURI("/api/v1", "/data-jobs/for-team/example-team/jobs", 5);
    String createJobSlash =
        provider.parsePropertyFromURI("/api/v1", "/data-jobs/for-team/example-team/jobs/", 5);
    String jobNameService =
        provider.parsePropertyFromURI(
            "/api/v1", "/data-jobs/for-team/example-team/jobs/example", 5);
    String jobNameDeploy =
        provider.parsePropertyFromURI(
            "/api/v1", "/data-jobs/for-team/example-team/jobs/example/deployments", 5);
    String jobNameServiceSlash =
        provider.parsePropertyFromURI(
            "/api/v1", "/data-jobs/for-team/example-team/jobs/example/", 5);

    String newTeamName =
        provider.parsePropertyFromURI(
            "/api/v1", "/data-jobs/for-team/example-team/jobs/example/team/new-example-team", 7);
    String newTeamNameSlash =
        provider.parsePropertyFromURI(
            "/api/v1", "/data-jobs/for-team/example-team/jobs/example/team/new-example-team/", 7);
    String newTeamNameMissing =
        provider.parsePropertyFromURI("/api/v1", "/data-jobs/for-team/example-team/jobs", 7);

    String teamName =
        provider.parsePropertyFromURI("/api/v1", "/data-jobs/for-team/example-team/jobs", 3);
    String teamNameSlash =
        provider.parsePropertyFromURI("/api/v1", "/data-jobs/for-team/example-team/jobs/", 3);
    String teamNameMissing = provider.parsePropertyFromURI("/api/v1", "/data-jobs/for-team/", 3);

    Assertions.assertEquals("", createJob);
    Assertions.assertEquals("", createJobSlash);
    Assertions.assertEquals("example", jobNameService);
    Assertions.assertEquals("example", jobNameDeploy);
    Assertions.assertEquals("example", jobNameServiceSlash);

    Assertions.assertEquals("new-example-team", newTeamName);
    Assertions.assertEquals("new-example-team", newTeamNameSlash);
    Assertions.assertEquals("", newTeamNameMissing);

    Assertions.assertEquals("example-team", teamName);
    Assertions.assertEquals("example-team", teamNameSlash);
    Assertions.assertEquals("", teamNameMissing);
  }

  @Test
  public void testJobCreateWithParameters() {
    HttpServletRequest request = mock(HttpServletRequest.class);
    JwtAuthenticationToken authentication = mock(JwtAuthenticationToken.class);
    Mockito.when(authentication.getTokenAttributes()).thenReturn(Map.of("username", "auserov"));
    Mockito.when(request.getMethod()).thenReturn("post");
    Mockito.when(request.getRequestURI()).thenReturn("/data-jobs/for-team/example-team/jobs");
    Mockito.when(request.getParameter("name")).thenReturn("example");

    AuthorizationBody actualBody = provider.createAuthorizationBody(request, authentication);
    AuthorizationBody expectedBody = new AuthorizationBody();
    expectedBody.setRequestedResourceName("data-job");
    expectedBody.setRequestedResourceTeam("example-team");
    expectedBody.setRequesterUserId("auserov");
    expectedBody.setRequestedResourceId("example");
    expectedBody.setRequestedPermission("write");
    expectedBody.setRequestedHttpPath("/data-jobs/for-team/example-team/jobs");
    expectedBody.setRequestedHttpVerb("POST");
    expectedBody.setRequestedResourceNewTeam("example-team");

    Assertions.assertEquals(actualBody, expectedBody);
  }

  @Test
  public void testJobCreateWithoutParameters() {
    HttpServletRequest request = mock(HttpServletRequest.class);
    JwtAuthenticationToken authentication = mock(JwtAuthenticationToken.class);
    Mockito.when(authentication.getTokenAttributes()).thenReturn(Map.of("username", "auserov"));
    Mockito.when(request.getMethod()).thenReturn("post");
    Mockito.when(request.getRequestURI()).thenReturn("/data-jobs/for-team/example-team/jobs");

    AuthorizationBody actualBody = provider.createAuthorizationBody(request, authentication);
    AuthorizationBody expectedBody = new AuthorizationBody();
    expectedBody.setRequestedResourceName("data-job");
    expectedBody.setRequestedResourceTeam("example-team");
    expectedBody.setRequesterUserId("auserov");
    expectedBody.setRequestedResourceId("");
    expectedBody.setRequestedPermission("write");
    expectedBody.setRequestedHttpPath("/data-jobs/for-team/example-team/jobs");
    expectedBody.setRequestedHttpVerb("POST");
    expectedBody.setRequestedResourceNewTeam("example-team");

    Assertions.assertEquals(actualBody, expectedBody);
  }

  @Test
  public void testJobPut() {
    HttpServletRequest request = mock(HttpServletRequest.class);
    JwtAuthenticationToken authentication = mock(JwtAuthenticationToken.class);
    Mockito.when(authentication.getTokenAttributes()).thenReturn(Map.of("username", "auserov"));
    Mockito.when(request.getMethod()).thenReturn("put");
    Mockito.when(request.getRequestURI())
        .thenReturn("/data-jobs/for-team/example-team/jobs/example/deployments");

    AuthorizationBody actualBody = provider.createAuthorizationBody(request, authentication);
    AuthorizationBody expectedBody = new AuthorizationBody();
    expectedBody.setRequestedResourceName("data-job");
    expectedBody.setRequestedResourceTeam("example-team");
    expectedBody.setRequesterUserId("auserov");
    expectedBody.setRequestedResourceId("example");
    expectedBody.setRequestedPermission("write");
    expectedBody.setRequestedHttpPath("/data-jobs/for-team/example-team/jobs/example/deployments");
    expectedBody.setRequestedHttpVerb("PUT");
    expectedBody.setRequestedResourceNewTeam("example-team");

    Assertions.assertEquals(actualBody, expectedBody);
  }

  @Test
  public void testJobWithContextPath() {
    HttpServletRequest request = mock(HttpServletRequest.class);
    JwtAuthenticationToken authentication = mock(JwtAuthenticationToken.class);
    Mockito.when(authentication.getTokenAttributes()).thenReturn(Map.of("username", "auserov"));
    Mockito.when(request.getMethod()).thenReturn("put");
    Mockito.when(request.getRequestURI())
        .thenReturn("/api/v1/data-jobs/for-team/example-team/jobs/example/deployments");
    Mockito.when(request.getContextPath()).thenReturn("/api/v1");

    AuthorizationBody actualBody = provider.createAuthorizationBody(request, authentication);
    AuthorizationBody expectedBody = new AuthorizationBody();
    expectedBody.setRequestedResourceName("data-job");
    expectedBody.setRequestedResourceTeam("example-team");
    expectedBody.setRequesterUserId("auserov");
    expectedBody.setRequestedResourceId("example");
    expectedBody.setRequestedPermission("write");
    expectedBody.setRequestedHttpPath(
        "/api/v1/data-jobs/for-team/example-team/jobs/example/deployments");
    expectedBody.setRequestedHttpVerb("PUT");
    expectedBody.setRequestedResourceNewTeam("example-team");

    Assertions.assertEquals(actualBody, expectedBody);
  }

  @Test
  public void testJobTeamPutWithTeamWithSpaces() {
    HttpServletRequest request = mock(HttpServletRequest.class);
    JwtAuthenticationToken authentication = mock(JwtAuthenticationToken.class);
    Mockito.when(authentication.getTokenAttributes()).thenReturn(Map.of("username", "auserov"));
    Mockito.when(request.getMethod()).thenReturn("put");
    // TODO: the job "example" has team "job-repo-example-team" in the db so we don't parse the
    // job's team from the URI
    Mockito.when(request.getRequestURI())
        .thenReturn("/data-jobs/for-team/example+team/jobs/example/team/new+example+team");

    AuthorizationBody actualBody = provider.createAuthorizationBody(request, authentication);
    AuthorizationBody expectedBody = new AuthorizationBody();
    expectedBody.setRequestedResourceName("data-job");
    expectedBody.setRequestedResourceTeam("example team");
    expectedBody.setRequesterUserId("auserov");
    expectedBody.setRequestedResourceId("example");
    expectedBody.setRequestedPermission("write");
    expectedBody.setRequestedHttpPath(
        "/data-jobs/for-team/example+team/jobs/example/team/new+example+team");
    expectedBody.setRequestedHttpVerb("PUT");
    expectedBody.setRequestedResourceNewTeam("new example team");

    Assertions.assertEquals(actualBody, expectedBody);
  }

  @Test
  @Deprecated
  public void testJobGetWithTeamWithSpaces() {
    HttpServletRequest request = mock(HttpServletRequest.class);
    JwtAuthenticationToken authentication = mock(JwtAuthenticationToken.class);
    Mockito.when(authentication.getTokenAttributes()).thenReturn(Map.of("username", "auserov"));
    Mockito.when(request.getMethod()).thenReturn("get");
    Mockito.when(request.getRequestURI()).thenReturn("/data-jobs/for-team/example%20team");

    AuthorizationBody actualBody = provider.createAuthorizationBody(request, authentication);
    AuthorizationBody expectedBody = new AuthorizationBody();
    expectedBody.setRequestedResourceName("data-job");
    expectedBody.setRequestedResourceTeam("example team");
    expectedBody.setRequesterUserId("auserov");
    expectedBody.setRequestedResourceId("");
    expectedBody.setRequestedPermission("read");
    expectedBody.setRequestedHttpPath("/data-jobs/for-team/example%20team");
    expectedBody.setRequestedHttpVerb("GET");
    expectedBody.setRequestedResourceNewTeam("example team");

    Assertions.assertEquals(actualBody, expectedBody);
  }

  @Test
  public void testGetAccessToken_withAuthEndpointAndRefreshToken_shouldUseObtainedAccessToken() {
    String obtainedAccessToken = "obtainedAccessToken";
    String receivedAccessToken = "receivedAccessToken";
    String authorizationServerEndpoint = "authorizationServerEndpoint";
    String refreshToken = "refreshToken";

    AuthorizationProvider authorizationProvider = mock(AuthorizationProvider.class);
    Mockito.when(
            authorizationProvider.obtainAccessToken(
                eq(authorizationServerEndpoint), eq(refreshToken)))
        .thenReturn(obtainedAccessToken);
    Mockito.when(authorizationProvider.getAccessTokenReceived()).thenReturn(receivedAccessToken);

    Mockito.when(
            authorizationProvider.getAccessToken(eq(authorizationServerEndpoint), eq(refreshToken)))
        .thenCallRealMethod();

    String actualAccessToken =
        authorizationProvider.getAccessToken(authorizationServerEndpoint, refreshToken);

    Assertions.assertEquals(obtainedAccessToken, actualAccessToken);
  }

  @Test
  public void testGetAccessToken_withAuthEndpointAndRefreshToken_shouldUseReceivedAccessToken() {
    String obtainedAccessToken = "obtainedAccessToken";
    String receivedAccessToken = "receivedAccessToken";
    String authorizationServerEndpoint = "";
    String refreshToken = "";

    AuthorizationProvider authorizationProvider = mock(AuthorizationProvider.class);
    Mockito.when(
            authorizationProvider.obtainAccessToken(
                eq(authorizationServerEndpoint), eq(refreshToken)))
        .thenReturn(obtainedAccessToken);
    Mockito.when(authorizationProvider.getAccessTokenReceived()).thenReturn(receivedAccessToken);

    Mockito.when(
            authorizationProvider.getAccessToken(eq(authorizationServerEndpoint), eq(refreshToken)))
        .thenCallRealMethod();

    String actualAccessToken =
        authorizationProvider.getAccessToken(authorizationServerEndpoint, refreshToken);

    Assertions.assertEquals(receivedAccessToken, actualAccessToken);
  }
}
