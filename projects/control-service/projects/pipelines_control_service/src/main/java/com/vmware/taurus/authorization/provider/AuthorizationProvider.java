/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.authorization.provider;

import com.vmware.taurus.authorization.AuthorizationInterceptor;
import com.vmware.taurus.authorization.webhook.AuthorizationBody;
import com.vmware.taurus.authorization.webhook.AuthorizationWebHookProvider;
import com.vmware.taurus.service.JobsRepository;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.oauth2.core.AbstractOAuth2Token;
import org.springframework.security.oauth2.server.resource.authentication.JwtAuthenticationToken;
import org.springframework.stereotype.Component;

import javax.servlet.http.HttpServletRequest;
import java.net.URLDecoder;
import java.nio.charset.Charset;
import java.util.Optional;

/**
 * AuthorizationProvider class used in {@link AuthorizationInterceptor} responsible for handling of
 * the creation of {@link AuthorizationBody} for the {@link AuthorizationWebHookProvider}
 */
@Component
public class AuthorizationProvider {

  // TODO: instead of using those indexes to split path, introduce regex utility class
  private static final int JOB_NAME_INDEX = 5;

  private static final int NEW_TEAM_NAME_INDEX = 7;

  private static final int TEAM_NAME_INDEX = 3;

  @Value("${datajobs.authorization.jwt.claim.username}")
  private String usernameField;

  private static final String TEAM_PARAMETER_NAME = "team";

  private static final String JOB_NAME_PARAMETER = "name";

  private final JobsRepository jobsRepository;

  @Autowired
  public AuthorizationProvider(JobsRepository jobsRepository) {
    this.jobsRepository = jobsRepository;
  }

  /**
   * Extracts necessary information out of HTTP Request and currently authenticated users and return
   * AuthorizationBody which can be used to make Authorization decisions.
   */
  public AuthorizationBody createAuthorizationBody(
      HttpServletRequest request, Authentication authentication) {
    AuthorizationBody body = new AuthorizationBody();
    var jobTeam = getJobTeam(request);
    var jobNewTeam = getJobNewTeam(request, jobTeam);
    body.setRequesterUserId(getUserId(authentication));
    body.setRequestedResourceTeam(jobTeam);
    body.setRequestedResourceName("data-job");
    body.setRequestedResourceId(getJobName(request));
    body.setRequestedPermission(request.getMethod().equalsIgnoreCase("GET") ? "read" : "write");
    body.setRequestedHttpPath(request.getRequestURI());
    body.setRequestedHttpVerb(request.getMethod().toUpperCase());
    body.setRequestedResourceNewTeam(jobNewTeam);

    return body;
  }

  public String getUserId(Authentication authentication) {
    if (authentication instanceof JwtAuthenticationToken) {
      JwtAuthenticationToken oauthToken = (JwtAuthenticationToken) authentication;
      return oauthToken.getTokenAttributes().get(usernameField).toString();
    } else {
      var principal = authentication.getPrincipal();
      if (principal instanceof UserDetails) {
        return ((UserDetails) principal).getUsername();
      } else {
        return principal.toString();
      }
    }
  }

  public String getAccessToken() {
    Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
    String accessToken = null;

    if (authentication instanceof JwtAuthenticationToken) {
      JwtAuthenticationToken oauthToken = (JwtAuthenticationToken) authentication;
      accessToken =
          Optional.ofNullable(oauthToken.getToken())
              .map(AbstractOAuth2Token::getTokenValue)
              .orElse(null);
    }

    return accessToken;
  }

  String parsePropertyFromURI(String contextPath, String fullPath, int index) {
    String uri = URLDecoder.decode(fullPath, Charset.defaultCharset());
    if (!StringUtils.isBlank(contextPath)) {
      uri = fullPath.replaceFirst("^" + contextPath, "");
    }
    var paths = uri.split("/");
    try {
      var newTeamName = paths[index];
      return newTeamName;
    } catch (ArrayIndexOutOfBoundsException e) {
      return "";
    }
  }

  String getJobTeam(HttpServletRequest request) {
    return this.parsePropertyFromURI(
        request.getContextPath(), request.getRequestURI(), TEAM_NAME_INDEX);
  }

  String getJobNewTeam(HttpServletRequest request, String existingTeam) {
    String jobNewTeam =
        this.parsePropertyFromURI(
            request.getContextPath(), request.getRequestURI(), NEW_TEAM_NAME_INDEX);
    if (jobNewTeam.isBlank()) {
      return existingTeam;
    }
    return jobNewTeam;
  }

  String getJobName(HttpServletRequest request) {
    var jobName = request.getParameter(JOB_NAME_PARAMETER);
    if (jobName != null) {
      return jobName;
    }
    jobName =
        this.parsePropertyFromURI(
            request.getContextPath(), request.getRequestURI(), JOB_NAME_INDEX);
    if (!jobName.isBlank()) {
      return jobName;
    }
    return "";
  }
}
