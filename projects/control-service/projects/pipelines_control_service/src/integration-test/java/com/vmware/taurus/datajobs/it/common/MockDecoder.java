/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs.it.common;


import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Primary;
import org.springframework.context.annotation.Profile;
import org.springframework.security.oauth2.core.oidc.IdTokenClaimNames;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.security.oauth2.jwt.JwtDecoder;

import java.time.Instant;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.Map;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

/**
 * Registers a bean with {@link JwtDecoder} mock in order to escape the exception due
 * to missing jwt endpoint. We can potentially have very basic mock, but left the
 * configurations since we might need proper example of how decoder is properly mocked
 */
@Profile("MockDecoder")
@Configuration
public class MockDecoder {

//    @Bean
//    @Primary
//    public JwtDecoder jwtDecoder() {
//        Map<String, Object> claims = new HashMap<>();
//        claims.put(IdTokenClaimNames.SUB, "sub123");
//        claims.put(IdTokenClaimNames.ISS, "http://localhost/iss");
//        claims.put(IdTokenClaimNames.AUD, Arrays.asList("clientId", "a", "u", "d"));
//        claims.put(IdTokenClaimNames.AZP, "clientId");
//        Jwt jwt = new Jwt("token123", Instant.now(), Instant.now().plusSeconds(3600),
//                Collections.singletonMap("header1", "value1"), claims);
//        JwtDecoder jwtDecoder = mock(JwtDecoder.class);
//        when(jwtDecoder.decode(any())).thenReturn(jwt);
//        return jwtDecoder;
//    }
}
