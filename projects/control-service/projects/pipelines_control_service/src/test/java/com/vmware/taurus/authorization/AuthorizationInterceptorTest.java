/*
 * Copyright 2023-2025 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.authorization;

import com.vmware.taurus.authorization.provider.AuthorizationProvider;
import com.vmware.taurus.authorization.webhook.AuthorizationWebHookProvider;
import com.vmware.taurus.base.FeatureFlags;
import com.vmware.taurus.secrets.service.JobSecretsService;
import com.vmware.taurus.secrets.service.vault.VaultTeamCredentials;
import com.vmware.taurus.security.SecurityConfiguration;
import com.vmware.taurus.service.repository.JobsRepository;
import com.vmware.taurus.service.diag.OperationContext;
import com.vmware.taurus.service.webhook.WebHookResult;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Answers;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.Mockito;
import org.mockito.junit.jupiter.MockitoExtension;
import org.mockito.junit.jupiter.MockitoSettings;
import org.mockito.quality.Strictness;
import org.springframework.http.HttpStatus;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.mock.web.MockHttpServletResponse;
import org.springframework.security.core.context.SecurityContext;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.oauth2.core.OAuth2TokenIntrospectionClaimNames;
import org.springframework.security.oauth2.server.resource.authentication.JwtAuthenticationToken;
import org.springframework.test.util.ReflectionTestUtils;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

import static org.mockito.Mockito.mock;

@ExtendWith(MockitoExtension.class)
public class AuthorizationInterceptorTest {

  @Mock private SecurityContextHolder securityContextHolder;

  @Mock private FeatureFlags featureFlags;

  @Mock private AuthorizationWebHookProvider webhookProvider;

  @Mock private JobsRepository jobsRepository;

  @Mock(answer = Answers.RETURNS_DEEP_STUBS)
  private AuthorizationProvider authorizationProvider;

  @Mock private JwtAuthenticationToken jwtAuthenticationToken;

  @Mock private OperationContext opCtx;

  @Mock private JobSecretsService secretsService;

  @InjectMocks private AuthorizationInterceptor authorizationInterceptor;

  @Test
  public void testAuthAndAuthzEnabledSuccessPOST() throws IOException {
    Mockito.when(featureFlags.isSecurityEnabled()).thenReturn(true);
    Mockito.when(featureFlags.isAuthorizationEnabled()).thenReturn(true);
    MockHttpServletRequest request = new MockHttpServletRequest();
    MockHttpServletResponse response = new MockHttpServletResponse();
    request.setMethod("post");
    Mockito.when(webhookProvider.invokeWebHook(Mockito.any()))
        .thenReturn(
            Optional.of(
                WebHookResult.builder().status(HttpStatus.OK).message("").success(true).build()));
    Mockito.when(jwtAuthenticationToken.isAuthenticated()).thenReturn(true);
    ReflectionTestUtils.setField(authorizationInterceptor, "usernameField", "usernameField");
    Map<String, Object> tokenAttributes = new HashMap<>();
    tokenAttributes.put("usernameField", "testUser");
    Mockito.when(jwtAuthenticationToken.getTokenAttributes()).thenReturn(tokenAttributes);
    SecurityContext securityContext = mock(SecurityContext.class);
    Mockito.when(securityContext.getAuthentication()).thenReturn(jwtAuthenticationToken);
    SecurityContextHolder.setContext(securityContext);

    var pass = authorizationInterceptor.preHandle(request, response, new Object());

    Assertions.assertEquals(true, pass);
    Assertions.assertEquals(HttpStatus.OK.value(), response.getStatus());
    Assertions.assertEquals("", response.getContentAsString());
  }

  @Test
  public void testAuthAndAuthzEnabledSuccessGET() throws IOException {
    Mockito.when(featureFlags.isSecurityEnabled()).thenReturn(true);
    Mockito.when(featureFlags.isAuthorizationEnabled()).thenReturn(true);
    MockHttpServletRequest request = new MockHttpServletRequest();
    MockHttpServletResponse response = new MockHttpServletResponse();
    request.setMethod("get");
    Mockito.when(webhookProvider.invokeWebHook(Mockito.any()))
        .thenReturn(
            Optional.of(
                WebHookResult.builder().status(HttpStatus.OK).message("").success(true).build()));
    Mockito.when(jwtAuthenticationToken.isAuthenticated()).thenReturn(true);
    ReflectionTestUtils.setField(authorizationInterceptor, "usernameField", "usernameField");
    Map<String, Object> tokenAttributes = new HashMap<>();
    tokenAttributes.put("usernameField", "testUser");
    Mockito.when(jwtAuthenticationToken.getTokenAttributes()).thenReturn(tokenAttributes);
    SecurityContext securityContext = mock(SecurityContext.class);
    Mockito.when(securityContext.getAuthentication()).thenReturn(jwtAuthenticationToken);
    SecurityContextHolder.setContext(securityContext);

    var pass = authorizationInterceptor.preHandle(request, response, new Object());

    Assertions.assertEquals(true, pass);
    Assertions.assertEquals(HttpStatus.OK.value(), response.getStatus());
    Assertions.assertEquals("", response.getContentAsString());
  }

  @Test
  public void testAuthAndAuthzEnabledSuccessPUT() throws IOException {
    Mockito.when(featureFlags.isSecurityEnabled()).thenReturn(true);
    Mockito.when(featureFlags.isAuthorizationEnabled()).thenReturn(true);
    MockHttpServletRequest request = new MockHttpServletRequest();
    MockHttpServletResponse response = new MockHttpServletResponse();
    request.setMethod("put");
    Mockito.when(jwtAuthenticationToken.isAuthenticated()).thenReturn(true);
    ReflectionTestUtils.setField(authorizationInterceptor, "usernameField", "usernameField");
    Map<String, Object> tokenAttributes = new HashMap<>();
    tokenAttributes.put("usernameField", "testUser");
    Mockito.when(jwtAuthenticationToken.getTokenAttributes()).thenReturn(tokenAttributes);
    SecurityContext securityContext = mock(SecurityContext.class);
    Mockito.when(webhookProvider.invokeWebHook(Mockito.any()))
        .thenReturn(
            Optional.of(
                WebHookResult.builder().status(HttpStatus.OK).message("").success(true).build()));
    Mockito.when(securityContext.getAuthentication()).thenReturn(jwtAuthenticationToken);
    SecurityContextHolder.setContext(securityContext);

    var pass = authorizationInterceptor.preHandle(request, response, new Object());

    Assertions.assertEquals(true, pass);
    Assertions.assertEquals(HttpStatus.OK.value(), response.getStatus());
    Assertions.assertEquals("", response.getContentAsString());
  }

  @Test
  public void testAuthAndAuthzEnabledUnauthorizedPUT() throws IOException {
    Mockito.when(featureFlags.isSecurityEnabled()).thenReturn(true);
    Mockito.when(featureFlags.isAuthorizationEnabled()).thenReturn(true);
    MockHttpServletRequest request = new MockHttpServletRequest();
    request.setMethod("put");
    MockHttpServletResponse response = new MockHttpServletResponse();
    Mockito.when(jwtAuthenticationToken.isAuthenticated()).thenReturn(true);
    ReflectionTestUtils.setField(authorizationInterceptor, "usernameField", "usernameField");
    Map<String, Object> tokenAttributes = new HashMap<>();
    tokenAttributes.put("usernameField", "testUser");
    Mockito.when(jwtAuthenticationToken.getTokenAttributes()).thenReturn(tokenAttributes);
    SecurityContext securityContext = mock(SecurityContext.class);
    Mockito.when(webhookProvider.invokeWebHook(Mockito.any()))
        .thenReturn(
            Optional.of(
                WebHookResult.builder()
                    .status(HttpStatus.UNAUTHORIZED)
                    .message("Missing team body")
                    .success(true)
                    .build()));
    Mockito.when(securityContext.getAuthentication()).thenReturn(jwtAuthenticationToken);
    SecurityContextHolder.setContext(securityContext);

    var pass = authorizationInterceptor.preHandle(request, response, new Object());

    Assertions.assertEquals(true, pass);
    Assertions.assertEquals(HttpStatus.UNAUTHORIZED.value(), response.getStatus());
    Assertions.assertEquals("Missing team body", response.getContentAsString());
  }

  @Test
  public void testAuthDisabled() throws IOException {
    Mockito.when(featureFlags.isSecurityEnabled()).thenReturn(false);
    MockHttpServletRequest request = new MockHttpServletRequest();
    MockHttpServletResponse response = new MockHttpServletResponse();

    var pass = authorizationInterceptor.preHandle(request, response, new Object());

    Assertions.assertEquals(true, pass);
    Assertions.assertEquals(HttpStatus.OK.value(), response.getStatus());
    Assertions.assertEquals("", response.getContentAsString());
  }

  @Test
  @MockitoSettings(strictness = Strictness.LENIENT)
  public void testAuthDisabledAuthzEnabled() throws IOException {
    Mockito.when(featureFlags.isSecurityEnabled()).thenReturn(true);
    Mockito.when(featureFlags.isAuthorizationEnabled()).thenReturn(false);
    MockHttpServletRequest request = new MockHttpServletRequest();
    MockHttpServletResponse response = new MockHttpServletResponse();
    Mockito.when(jwtAuthenticationToken.isAuthenticated()).thenReturn(true);
    ReflectionTestUtils.setField(authorizationInterceptor, "usernameField", "usernameField");
    Map<String, Object> tokenAttributes = new HashMap<>();
    tokenAttributes.put("usernameField", "testUser");
    Mockito.when(jwtAuthenticationToken.getTokenAttributes()).thenReturn(tokenAttributes);

    var pass = authorizationInterceptor.preHandle(request, response, new Object());

    Assertions.assertTrue(pass);
    Assertions.assertEquals(HttpStatus.OK.value(), response.getStatus());
    Assertions.assertEquals("", response.getContentAsString());
  }

  /**
   * The test shows that given the endpoints which does not have authentication enabled as per
   * {@link SecurityConfiguration} and are missing authentication token the preHandle method won't
   * throw an exception, but rather let the request pass due to the null authentication
   */
  @Test
  public void testAuthenticationNullForDisabledEndpoints() throws IOException {
    Mockito.when(featureFlags.isSecurityEnabled()).thenReturn(true);
    SecurityContext securityContext = mock(SecurityContext.class);
    Mockito.when(securityContext.getAuthentication()).thenReturn(null);
    SecurityContextHolder.setContext(securityContext);
    MockHttpServletRequest request = new MockHttpServletRequest();
    MockHttpServletResponse response = new MockHttpServletResponse();

    var pass = authorizationInterceptor.preHandle(request, response, new Object());

    Assertions.assertEquals(true, pass);
    Assertions.assertEquals(HttpStatus.OK.value(), response.getStatus());
    Assertions.assertEquals("", response.getContentAsString());
  }

  @Test
  void testPreHandle_OAuthApplicationToken_Success() throws IOException {
    Mockito.when(featureFlags.isSecurityEnabled()).thenReturn(true);
    Mockito.when(featureFlags.isAuthorizationEnabled()).thenReturn(true);
    MockHttpServletRequest request = new MockHttpServletRequest();
    MockHttpServletResponse response = new MockHttpServletResponse();
    SecurityContext securityContext = mock(SecurityContext.class);
    Mockito.when(securityContext.getAuthentication()).thenReturn(jwtAuthenticationToken);
    Mockito.when(jwtAuthenticationToken.isAuthenticated()).thenReturn(true);

    Map<String, Object> attributes = new HashMap<>();
    attributes.put(OAuth2TokenIntrospectionClaimNames.SUB, "client:testClientId");
    Mockito.when(jwtAuthenticationToken.getTokenAttributes()).thenReturn(attributes);

    Mockito.when(authorizationProvider.getJobTeam(request)).thenReturn("testTeam");

    VaultTeamCredentials mockCredentials =
        new VaultTeamCredentials("testTeam", "testClientId", "testSecret");
    Mockito.when(secretsService.readTeamOauthCredentials("testTeam")).thenReturn(mockCredentials);
    SecurityContextHolder.setContext(securityContext);

    Assertions.assertTrue(authorizationInterceptor.preHandle(request, response, new Object()));
  }

  @Test
  void testPreHandle_OAuthApplicationToken_Failure() throws IOException {
    Mockito.when(featureFlags.isSecurityEnabled()).thenReturn(true);
    Mockito.when(featureFlags.isAuthorizationEnabled()).thenReturn(true);
    MockHttpServletRequest request = new MockHttpServletRequest();
    MockHttpServletResponse response = new MockHttpServletResponse();
    SecurityContext securityContext = mock(SecurityContext.class);
    Mockito.when(securityContext.getAuthentication()).thenReturn(jwtAuthenticationToken);
    Mockito.when(jwtAuthenticationToken.isAuthenticated()).thenReturn(true);

    Map<String, Object> attributes = new HashMap<>();
    attributes.put(OAuth2TokenIntrospectionClaimNames.SUB, "client:testClientId");
    Mockito.when(jwtAuthenticationToken.getTokenAttributes()).thenReturn(attributes);

    Mockito.when(authorizationProvider.getJobTeam(request)).thenReturn("testTeam");

    VaultTeamCredentials mockCredentials =
        new VaultTeamCredentials("differentTeam", "testClientId", "testSecret");
    Mockito.when(secretsService.readTeamOauthCredentials("testTeam")).thenReturn(mockCredentials);
    SecurityContextHolder.setContext(securityContext);

    Assertions.assertTrue(authorizationInterceptor.preHandle(request, response, new Object()));
  }
}
