/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus;

import io.micrometer.prometheus.PrometheusMeterRegistry;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.actuate.autoconfigure.metrics.MeterRegistryCustomizer;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
import org.springframework.core.env.Environment;

import java.util.Map;
import java.util.Set;
import java.util.TreeMap;
import java.util.stream.Collectors;

@SpringBootApplication
public class ControlplaneApplication {
  static Logger log = LoggerFactory.getLogger(ControlplaneApplication.class);

  @Autowired private Environment env;

  @Bean
  MeterRegistryCustomizer<PrometheusMeterRegistry> metricsCommonTag() {
    String serviceName = env.getProperty(SpringAppPropNames.SVC_NAME);
    return registry -> registry.config().commonTags("service", serviceName);
  }

  public static void main(String[] args) {
    log.info(
        "Starting {} with args:\n{}",
        ControlplaneApplication.class.getSimpleName(),
        String.join(",\n", args));
    log.debug("Environment variables:\n{}", prettyEntrySet(System.getenv().entrySet()));
    log.debug("Java properties:\n{}", prettyEntrySet(System.getProperties().entrySet()));
    SpringApplication app = new SpringApplication(ControlplaneApplication.class);

    // Base service has hardcoded all Spring properties in its main() method, so that other services
    // can partially override them in their application*.properties files
    // See Spring Boot PropertySource order at
    // https://docs.spring.io/spring-boot/docs/current/reference/html/spring-boot-features.html#boot-features-external-config
    // Another reason for having those properties here is to have default values for local
    // development. This allows developers to simply type
    // gradlew run
    // and have their service up and running (no need to set environment variables beforehand)
    Map<String, Object> props = new TreeMap<>();
    props.put(
        SpringAppPropNames.HTTPTRACE_INCLUDE,
        "USER_PRINCIPAL,errors,parameters,context_path,remote_address,path_info,path_translated,session_id");
    props.put(
        SpringAppPropNames.MANAGEMENT_ENDPOINTS_WEB_EXPOSURE_INCLUDE,
        "*"); // Spring Actuator config
    props.put(
        SpringAppPropNames.MANAGEMENT_ENDPOINT_HEALTH_SHOW_DETAILS,
        "always"); // Spring Actuator config

    ////////////////////////////////////////////////////////
    // Properties below must be overridden in all services
    // Properties above may be overridden in services
    ////////////////////////////////////////////////////////

    final String svcName = "base";
    // Used for log file name
    props.put(SpringAppPropNames.SVC_NAME, svcName); // mandatory for logback-spring.xml
    props.put(
        SpringAppPropNames.MANAGEMENT_ENDPOINTS_WEB_BASE_PATH,
        "/" + svcName + "/debug"); // Spring Actuator. http://localhost:8080/${svc.url.prefix}/debug

    app.setDefaultProperties(props);
    app.run(args);
  }

  private static String prettyEntrySet(Set<? extends Map.Entry<?, ?>> entrySet) {
    return entrySet.stream()
        .map(e -> String.format("%s: %s", e.getKey(), e.getValue()))
        .sorted()
        .collect(Collectors.joining(",\n"));
  }
}
