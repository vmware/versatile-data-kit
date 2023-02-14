/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs;

import com.vmware.taurus.service.diag.telemetry.ITelemetry;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Primary;
import org.springframework.context.annotation.Profile;

import java.util.ArrayList;
import java.util.List;

@Profile("MockTelemetry")
@Configuration
public class MockTelemetry {

  public static List<String> payloads = new ArrayList<>();

  @Bean
  @Primary
  public ITelemetry telemetryClient() {
    return new ITelemetry() {
      @Override
      public void sendAsync(String payload) {
        payloads.add(payload);
      }
    };
  }
}
