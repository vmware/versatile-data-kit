/*
 * Copyright (c) 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.diag.telemetry;

import com.github.tomakehurst.wiremock.junit.WireMockRule;
import org.junit.Rule;
import org.junit.Test;

import java.util.concurrent.TimeUnit;

import static com.github.tomakehurst.wiremock.client.WireMock.*;
import static com.github.tomakehurst.wiremock.core.WireMockConfiguration.wireMockConfig;
import static com.github.tomakehurst.wiremock.stubbing.Scenario.STARTED;
import static org.awaitility.Awaitility.await;

public class TelemetryTest {

    @Rule
    public WireMockRule wireMockRule = new WireMockRule(wireMockConfig().dynamicPort());

    @Test
    public void test_telemetry_being_send() {
        stubFor(post(urlEqualTo("/test")).willReturn(aResponse().withBody("OK")));

        var telemetry = new Telemetry(wireMockRule.url("/test"));
        telemetry.sendAsync("{'key': 'value'}");

        await().atMost(5, TimeUnit.SECONDS)
                .with().pollInterval(1, TimeUnit.SECONDS)
                .untilAsserted(() -> verify(postRequestedFor(urlEqualTo("/test"))
                        .withRequestBody(containing("{'key': 'value'}"))));
    }

    @Test
    public void test_telemetry_being_send_single_retry() {
        // http://wiremock.org/docs/stateful-behaviour/
        stubFor(post(urlEqualTo("/test"))
                .inScenario("retry")
                .whenScenarioStateIs(STARTED)
                .willReturn(aResponse().withStatus(500))
                .willSetStateTo("request succeeds")
        );
        stubFor(post(urlEqualTo("/test"))
                .inScenario("retry")
                .whenScenarioStateIs("request succeeds")
                .willReturn(aResponse().withStatus(500))
        );

        var telemetry = new Telemetry(wireMockRule.url("/test"));
        telemetry.sendAsync("{'key': 'value'}");

        await().atMost(5, TimeUnit.SECONDS)
                .with().pollInterval(1, TimeUnit.SECONDS)
                .untilAsserted(() -> verify(exactly(2), postRequestedFor(urlEqualTo("/test"))
                        .withRequestBody(containing("{'key': 'value'}"))));
    }

    @Test
    public void test_telemetry_being_send_failed_client_error() {
        stubFor(post(urlEqualTo("/test")).willReturn(aResponse().withStatus(401)));

        var telemetry = new Telemetry(wireMockRule.url("/test"));
        telemetry.sendAsync("{'key': 'value'}");

        await().atMost(5, TimeUnit.SECONDS)
                .with().pollInterval(1, TimeUnit.SECONDS)
                .untilAsserted(() -> verify(postRequestedFor(urlEqualTo("/test"))
                        .withRequestBody(containing("{'key': 'value'}"))));
    }

}
