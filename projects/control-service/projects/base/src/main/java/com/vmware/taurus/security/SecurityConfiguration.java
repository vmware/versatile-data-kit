/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.security;

import com.vmware.taurus.base.FeatureFlags;
import io.swagger.models.HttpMethod;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.condition.ConditionalOnExpression;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Conditional;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.builders.WebSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.annotation.web.configuration.WebSecurityConfigurerAdapter;
import org.springframework.security.oauth2.core.DelegatingOAuth2TokenValidator;
import org.springframework.security.oauth2.core.OAuth2TokenValidator;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.security.oauth2.jwt.JwtDecoder;
import org.springframework.security.oauth2.jwt.JwtDecoders;
import org.springframework.security.oauth2.jwt.JwtValidators;
import org.springframework.security.oauth2.jwt.NimbusJwtDecoder;
import org.springframework.security.oauth2.server.resource.authentication.JwtAuthenticationConverter;
import org.springframework.security.oauth2.server.resource.authentication.JwtGrantedAuthoritiesConverter;

import java.util.Arrays;
import java.util.Collections;
import java.util.Set;
import java.util.stream.Collectors;

/**
 * Authentication and Authorization configuration.
 * <br>
 * If security is enabled (see FeatureFlags) then:
 * <br>
 * <ul>
 * <li>Only JWK-signed JWTs is supported and following property must be set:
 *     spring.security.oauth2.resourceserver.jwt.jwk-set-uri</li></ul>
 */
@EnableWebSecurity
@Slf4j
@Configuration
public class SecurityConfiguration extends WebSecurityConfigurerAdapter {

    private static final String AUTHORITY_PREFIX = "SCOPE_";

    private final FeatureFlags featureFlags;

    private final String jwksUri;
    private final String issuer;
    private final String authoritiesClaimName;
    private final String customClaimName;
    private final Set<String> authorizedCustomClaimValues;
    private final Set<String> authorizedRoles;
    public static final String[] ENDPOINTS_TO_IGNORE = {
          "/",
          "/data-jobs/v2/api-docs",
          "/data-jobs/swagger-resources/**",
//        "/data-jobs/configuration/**",
          "/data-jobs/swagger-ui.html",
          "/data-jobs/webjars/**",
          // There should not be sensitive data in prometheus, and it makes
          // integration with the monitoring system easier if no auth is necessary.
          "/data-jobs/debug/prometheus",
          // TODO: likely /data-jobs/debug is too permissive
          // but until we can expose them in swagger they are very hard to use with Auth.
          "/data-jobs/debug/**"};

    @Autowired
    public SecurityConfiguration(
            FeatureFlags featureFlags,
            @Value("${spring.security.oauth2.resourceserver.jwt.jwk-set-uri:}") String jwksUri,
            @Value("${spring.security.oauth2.resourceserver.jwt.issuer-uri:}") String issuer,
            @Value("${datajobs.authorization.authorities-claim-name:}") String authoritiesClaimName,
            @Value("${datajobs.authorization.custom-claim-name:}") String customClaimName,
            @Value("${datajobs.authorization.authorized-custom-claim-values:}") String authorizedCustomClaimValues,
            @Value("${datajobs.authorization.authorized-roles:}") String authorizedRoles) {
        this.featureFlags = featureFlags;
        this.jwksUri = jwksUri;
        this.issuer = issuer;
        this.authoritiesClaimName = authoritiesClaimName;
        this.customClaimName = customClaimName;
        this.authorizedCustomClaimValues = parseOrgIds(authorizedCustomClaimValues);
        this.authorizedRoles = parseRoles(authorizedRoles);
    }

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
    public void configure(WebSecurity web) {
        web.ignoring().antMatchers(ENDPOINTS_TO_IGNORE);
    }

    private void enableSecurity(HttpSecurity http) throws Exception {
        log.info("Security is enabled with OAuth2. JWT Key URI: {}", jwksUri);
        http
                .anonymous().disable()
                .csrf().disable()
                .authorizeRequests(authorizeRequests -> {
                    if (!authorizedRoles.isEmpty()) {
                        authorizeRequests
                                .antMatchers("/**")
                                .hasAnyAuthority(authorizedRoles.toArray(String[]::new));
                    }
                    authorizeRequests.anyRequest().authenticated();
                })
                .oauth2ResourceServer().jwt()
                .jwtAuthenticationConverter(jwtAuthenticationConverter());
    }

    @Bean
    public JwtAuthenticationConverter jwtAuthenticationConverter() {
        JwtAuthenticationConverter jwtAuthenticationConverter = new JwtAuthenticationConverter();
        jwtAuthenticationConverter.setJwtGrantedAuthoritiesConverter(jwtGrantedAuthoritiesConverter());

        return jwtAuthenticationConverter;
    }

    @Bean
    public JwtGrantedAuthoritiesConverter jwtGrantedAuthoritiesConverter() {
        JwtGrantedAuthoritiesConverter grantedAuthoritiesConverter = new JwtGrantedAuthoritiesConverter();
        // The Authority Prefix cannot be empty
        grantedAuthoritiesConverter.setAuthorityPrefix(AUTHORITY_PREFIX);
        if (!authoritiesClaimName.isEmpty()) {
            grantedAuthoritiesConverter.setAuthoritiesClaimName(authoritiesClaimName);
        }

        return grantedAuthoritiesConverter;
    }

    /**
     * Instantiate the jwtDecoder bean only when security is enabled to avoid having to specify the
     * required issuer property with disabled authorization.
     */
    @Bean
    @ConditionalOnExpression("not '${spring.security.oauth2.resourceserver.jwt.issuer-uri:}'.equals('')")
    public JwtDecoder jwtDecoder() {
        OAuth2TokenValidator<Jwt> defaultValidators = JwtValidators.createDefaultWithIssuer(issuer);
        OAuth2TokenValidator<Jwt> customTokenValidator = new CustomClaimTokenValidator(customClaimName, authorizedCustomClaimValues);
        OAuth2TokenValidator<Jwt> validator = new DelegatingOAuth2TokenValidator<>(customTokenValidator, defaultValidators);

        NimbusJwtDecoder jwtDecoder = JwtDecoders.fromOidcIssuerLocation(issuer);
        jwtDecoder.setJwtValidator(validator);
        return jwtDecoder;
    }

    private Set<String> parseOrgIds(String orgIds) {
        if (!StringUtils.isBlank(orgIds)) {
            return Arrays.stream(orgIds.split(","))
                    .filter(id -> !id.isBlank())
                    .collect(Collectors.toSet());
        }
        return Collections.emptySet();
    }

    private Set<String> parseRoles(String roles) {
        if (!StringUtils.isBlank(roles)) {
            return Arrays.stream(roles.split(","))
                    .filter(role -> !role.isBlank())
                    .map(role -> AUTHORITY_PREFIX + role)
                    .collect(Collectors.toSet());
        }
        return Collections.emptySet();
    }
}
