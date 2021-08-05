/*
 * Copyright (c) 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.security;

import com.vmware.taurus.base.FeatureFlags;
import io.swagger.models.HttpMethod;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.builders.WebSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.annotation.web.configuration.WebSecurityConfigurerAdapter;

/**
 * Authentication and Authorization configuration.
 * <br>
 * If security is enabled (see FeatureFlags) then:
 * <br>
 * <li>Only JWK-signed JWTs is supported and following property must be set:
 *     spring.security.oauth2.resourceserver.jwt.jwk-set-uri
 */
@EnableWebSecurity
@RequiredArgsConstructor
@Slf4j
@Configuration
public class SecurityConfiguration extends WebSecurityConfigurerAdapter {

   private final FeatureFlags featureFlags;

   @Value("${spring.security.oauth2.resourceserver.jwt.jwk-set-uri:}")
   private String jwksUri;

   @Override
   protected void configure(HttpSecurity http) throws Exception {
      if (featureFlags.isSecurityEnabled()) {
         enableSecurity(http);
      } else {
         log.info("Security is disabled.");
         http
                 .csrf().disable()
                 .authorizeRequests()
                 .anyRequest().anonymous();
      }
   }

   @Override
   public void configure(WebSecurity web) throws Exception {
      web.ignoring().antMatchers(
               "/",  "/v2/api-docs",  "/configuration/ui",
              "/swagger-resources/**", "/configuration/**",
              "/swagger-ui.html",  "/webjars/**",
              // There should not be sensitive data in prometheus
              // and it makes integration with monitoring system easier if no auth is necessary.
              "/data-jobs/debug/prometheus",
              // TODO: likely /data-jobs/debug is too permissive
              // but until we can expose them in swagger they are very hard to use with Auth.
              "/data-jobs/debug/**");
   }


   private void enableSecurity(HttpSecurity http) throws Exception {
      log.info("Security is enabled with OAuth2. JWT Key URI: {}", jwksUri);
      http
              .anonymous().disable()
              .csrf().disable()
              .authorizeRequests(authorizeRequests ->
                      authorizeRequests // TODO authorization ...
                              .antMatchers(String.valueOf(HttpMethod.POST), "/foo/**").hasAuthority("SCOPE_message:write")
                              .anyRequest().authenticated()
              )
              .oauth2ResourceServer().jwt();
   }


}
