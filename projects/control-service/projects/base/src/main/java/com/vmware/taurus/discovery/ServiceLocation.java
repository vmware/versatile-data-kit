/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.discovery;

import org.springframework.boot.web.client.RestTemplateBuilder;

// When updating or adding ports for services, these changes must be made in many places:
// 1) In each of the values.yml files at /k8s/envs/*/values.yml
// 2) In each service's application.properties at /services/*/src/main/resources/application.*
// 3) In base's service discovery enum at /libraries/base/src/main/java/com/vmware/taurus/discovery/ServiceLocation.java
// TODO: Remove this
public enum ServiceLocation {
   API(8084),
   AUTH_BRIDGE(8080),
   COLLECTOR(8094),
   CSP(8086),
   DAP(8088),
   DATA_JOBS(8092),
   DATABASE(8096),
   TEAM(8090),
   INGESTION_DEBUG_SERVICE(8098),
   SCHEMA_MANAGEMENT(8082),
   UI(80);

   static final String PROTOCOL = "http";
   static final String DEFAULT_HOST = "localhost";
   static final String HOST_SUFFIX = "_SERVICE_SERVICE_HOST";
   static final String PORT_SUFFIX = "_SERVICE_SERVICE_PORT";

   /*
   The port for the current service could be retrieved from ApplicationContext's server.port value; however, this would
   have limited value as we would still need the default ports for other services and there are limited usecases where
   a services needs to call itself via http.
    */
   final int defaultPort;

   public final String rootUri;

   ServiceLocation(int defaultPort) {
      this.defaultPort = defaultPort;
      rootUri = buildRootUri();
   }

   public RestTemplateBuilder restTemplateBuilder() {
      return new RestTemplateBuilder()
         .rootUri(rootUri);
   }

   String buildRootUri() {
      /*
       As this is an enum. There's no easy way to get Spring's ApplicationContext.

       This class could be refactored to a service which accepts enums as arguments to methods that return the
       rootUri or restTemplateBuilder. This isn't desired as there are no expected use cases of host and port being
       set by something other than an environmental variable. The hypothetical refactored class would need to
       calculate (or memoize) rootUri on each invocation.

       Current usage:
       import static com.vmware.taurus.discoverby.ServiceLocation.*;
       RestTemplate restTemplate = Team.restTemplateBuilder().foo('bar').baz(biz).build();

       Alternative usage leveraging Spring Context:
       import static com.vmware.taurus.discoverby.ServiceLocation.Service.*;
       import com.vmware.taurus.discoverby.ServiceLocation;
       @Autowired
       ServiceLocation serviceLocation;
       RestTemplate restTemplate = serviceLocation.getRestTemplateBuilder(TEAM).foo('bar').baz(biz).build();
       */
      String host = System.getenv(name() + HOST_SUFFIX);
      String port = System.getenv(name() + PORT_SUFFIX);
      if (host != null && port != null) {
         return PROTOCOL + "://" + host + ":" + port;
      }

      return PROTOCOL + "://" + DEFAULT_HOST + ":" + defaultPort;
   }
}
