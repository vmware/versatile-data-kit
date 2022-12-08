/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus;

import io.swagger.v3.oas.models.Components;
import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.info.License;
import io.swagger.v3.oas.models.security.SecurityScheme;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
import org.springframework.scheduling.annotation.EnableAsync;
import org.springframework.web.client.RestTemplate;

/** Utility class for easier application startup from Intellij Idea */
@EnableAsync
@SpringBootApplication
public class ServiceApp {

  @Bean
  public RestTemplate restTemplate() {
    return new RestTemplate();
  }

  @Bean
  OpenAPI apiInfo() {
    return (new OpenAPI())
        .info(
            (new Info()
                    .title("Versatile Data Kit Control Service API")
                    .description(
                        "The Data Jobs API of Versatile Data Kit Control Service. Data Jobs allows"
                            + " Data Engineers to implement automated pull ingestion (E in ELT) and"
                            + " batch data transformation into a database (T in ELT). See also"
                            + " https://github.com/vmware/versatile-data-kit/wiki/Introduction The"
                            + " API has resource-oriented URLs, JSON-encoded responses, and uses"
                            + " standard HTTP response codes, authentication, and verbs. The API"
                            + " enables creating, deploying, managing and executing Data Jobs in"
                            + " the runtime environment.<br> <br>"
                            + " ![](https://github.com/vmware/versatile-data-kit/wiki/vdk-data-job-lifecycle-state-diagram.png)"
                            + " <br> The API reflects the usual Data Job Development lifecycle:<br>"
                            + " <li> Create a new data job (webhook to further configure the job,"
                            + " e.g authorize its creation, setup permissions, etc). <li> Download"
                            + " keytab. Develop and run the data job locally. <li> Deploy the data"
                            + " job in cloud runtime environment to run on a scheduled basis."
                            + " <br><br> If Authentication is enabled, pass OAuth2 access token in"
                            + " HTTP header 'Authorization: Bearer [access-token-here]'"
                            + " (https://datatracker.ietf.org/doc/html/rfc6750). <br The API"
                            + " promotes some best practices (inspired by https://12factor.net):"
                            + " <li> Explicitly declare and isolate dependencies. <li> Strict"
                            + " separation of configurations from code. Configurations vary"
                            + " substantially across deploys, code does not. <li> Separation"
                            + " between the build, release/deploy, and run stages. <li> Data Jobs"
                            + " are stateless and share-nothing processes. Any data that needs to"
                            + " be persisted must be stored in a stateful backing service (e.g"
                            + " IProperties). <li> Implementation is assumed to be atomic and"
                            + " idempotent - should be OK for a job to fail somewhere in the"
                            + " middle; subsequent restart should not cause data corruption. <li>"
                            + " Keep development, staging, and production as similar as possible."
                            + " <br><br> <b>API Evolution</b><br> In the following sections, there"
                            + " are some terms that have a special meaning in the context of the"
                            + " APIs. <br><br> <li> <i>Stable</i> - The implementation of the API"
                            + " has been battle-tested (has been in production for some time). The"
                            + " API is a subject to semantic versioning model and will follow"
                            + " deprecation policy. <li> <i>Experimental</i> - May disappear"
                            + " without notice and is not a subject to semantic versioning."
                            + " Implementation of the API is not considered stable nor well tested."
                            + " Generally this is given to clients to experiment within testing"
                            + " environment. Must not be used in production. <li> <i>Deprecated</i>"
                            + " - API is expected to be removed within next one or two major"
                            + " version upgrade. The deprecation notice/comment will say when the"
                            + " API will be removed and what alternatives should be used instead."))
                .license(
                    (new License())
                        .name("Apache 2.0")
                        .url("https://www.apache.org/licenses/LICENSE-2.0.html"))
                .version("1.0"))
        .components(
            (new Components())
                .addSecuritySchemes(
                    "bearerAuth",
                    (new SecurityScheme())
                        .type(SecurityScheme.Type.HTTP)
                        .scheme("bearer")
                        .bearerFormat("JWT")));
  }

  public static void main(String[] args) {
    ControlplaneApplication.main(args);
  }
}
