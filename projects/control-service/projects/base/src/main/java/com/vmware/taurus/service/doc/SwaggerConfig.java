/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.doc;

import com.vmware.taurus.SpringAppPropNames;
import io.swagger.annotations.ApiOperation;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.Ordered;
import org.springframework.core.annotation.Order;
import org.springframework.stereotype.Controller;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;
import springfox.documentation.builders.PathSelectors;
import springfox.documentation.builders.RequestHandlerSelectors;
import springfox.documentation.spi.DocumentationType;
import springfox.documentation.spring.web.plugins.Docket;
import springfox.documentation.swagger2.annotations.EnableSwagger2;

/**
 * TODO: currently swagger doc is accessed via http://localhost:8080/swagger-ui.html
 * We need it to become http://localhost:8080/svcname/swagger-ui.html and this is not supported by Swagger, so probably some URL rewriting need be in place (redirects don't work in k8s environment)
 */
@Configuration
@EnableSwagger2
@Controller
public class SwaggerConfig implements WebMvcConfigurer {

    public SwaggerConfig(@Value("${" + SpringAppPropNames.SVC_NAME + ":base}") String svcName) {
        this.svcName = svcName;
    }

    private final String svcName;

    @Bean
    @Order(Ordered.LOWEST_PRECEDENCE)
    public Docket swaggerSpringMvcPlugin() {
        return new Docket(DocumentationType.SWAGGER_2)
//                .pathMapping("a") //this causes swagger to show methods as: GET /a/teams/name
                .select()
                //Every API (/libraries/model) method is annotated with ApiOperation
                .apis(RequestHandlerSelectors.withMethodAnnotation(ApiOperation.class))
                //services are expected to have 2 types of paths: /<team>/* and /<team>s/*.
                .paths(PathSelectors.ant("/" + svcName + "*/**"))
                .build()
                ;
    }
}
