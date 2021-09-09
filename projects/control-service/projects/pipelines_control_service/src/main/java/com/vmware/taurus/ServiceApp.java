/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus;

import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
import org.springframework.scheduling.annotation.EnableAsync;
import org.springframework.web.client.RestTemplate;

/**
 * Utility class for easier application startup from Intellij Idea
 */
@EnableAsync
@SpringBootApplication
public class ServiceApp {

   @Bean
   public RestTemplate restTemplate() {
      return new RestTemplate();
   }

   public static void main(String[] args) {
      ControlplaneApplication.main(args);
   }
}
