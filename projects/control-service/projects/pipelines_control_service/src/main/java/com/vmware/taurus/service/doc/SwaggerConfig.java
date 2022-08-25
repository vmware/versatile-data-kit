/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.doc;

import io.swagger.annotations.ApiOperation;
import org.openapitools.configuration.OpenAPIDocumentationConfig;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.annotation.Order;
import org.springframework.stereotype.Controller;
import org.springframework.web.servlet.config.annotation.ResourceHandlerRegistry;
import org.springframework.web.servlet.config.annotation.ViewControllerRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;
import springfox.documentation.builders.PathSelectors;
import springfox.documentation.builders.RequestHandlerSelectors;
import springfox.documentation.service.ApiKey;
import springfox.documentation.service.AuthorizationScope;
import springfox.documentation.service.SecurityReference;
import springfox.documentation.service.Tag;
import springfox.documentation.spi.service.contexts.SecurityContext;
import springfox.documentation.spring.web.plugins.Docket;
import springfox.documentation.swagger.web.SecurityConfiguration;
import springfox.documentation.swagger.web.SecurityConfigurationBuilder;
import springfox.documentation.swagger2.annotations.EnableSwagger2;

import javax.servlet.ServletContext;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;

/**
 * Swagger Configuration for Versatile Data Kit Control Service. It relies on OpenApiGenerator to
 * generate both API interfaces (APIOperation annotaiton) And OpenAPIDocumentationConfig which
 * contains info part of swagger doc
 */
@Configuration
@EnableSwagger2
@Controller
public class SwaggerConfig implements WebMvcConfigurer {
  private static final String PATH = "/data-jobs";
  private static final String AUTHORIZE_KEY_NAME =
      "Authorization Header (put 'Bearer access_token')";

  @Bean
  @Order(1)
  public Docket swaggerSpringMvcPlugin(ServletContext context) {
    return new OpenAPIDocumentationConfig()
        .customImplementation(context, "")
        .securitySchemes(Arrays.asList(apiKey()))
        .securityContexts(Collections.singletonList(securityContext()))
        .select()
        .apis(RequestHandlerSelectors.withMethodAnnotation(ApiOperation.class))
        .build()
        .tags(
            new Tag("Data Jobs Execution", "(Experimental)"),
            new Tag("Data Jobs", "(Stable)"),
            new Tag("Data Jobs Deployment", "(Stable)"),
            new Tag("Data Jobs Service", "(Stable)"),
            new Tag("Data Jobs Sources", "(Stable)"));
  }

  @Override
  public void addViewControllers(ViewControllerRegistry registry) {
    final var apiDocs = "/v2/api-docs";
    final var configUi = "/swagger-resources/configuration/ui";
    final var configSecurity = "/swagger-resources/configuration/security";
    final var resources = "/swagger-resources";

    registry.addViewController(PATH + apiDocs).setViewName("forward:" + apiDocs);
    registry.addViewController(PATH + configUi).setViewName("forward:" + configUi);
    registry.addViewController(PATH + configSecurity).setViewName("forward:" + configSecurity);
    registry.addViewController(PATH + resources).setViewName("forward:" + resources);
  }

  @Override
  public void addResourceHandlers(ResourceHandlerRegistry registry) {
    registry
        .addResourceHandler(PATH + "/**")
        .addResourceLocations("classpath:/META-INF/resources/");
  }

  // springfox does not support Bearer Token Auth from api.yaml so we hack it manually
  // TODO: there must be cleaner way. We may consider switch to other library also.
  private ApiKey apiKey() {
    return new ApiKey(AUTHORIZE_KEY_NAME, "Authorization", "header");
  }

  private List<SecurityReference> defaultAuth() {
    AuthorizationScope authorizationScope = new AuthorizationScope("global", "accessEverything");
    AuthorizationScope[] authorizationScopes = new AuthorizationScope[1];
    authorizationScopes[0] = authorizationScope;
    return Collections.singletonList(
        new SecurityReference(AUTHORIZE_KEY_NAME, authorizationScopes));
  }

  private SecurityContext securityContext() {
    return SecurityContext.builder()
        .securityReferences(defaultAuth())
        .forPaths(PathSelectors.any())
        .build();
  }

  @Bean
  public SecurityConfiguration security() {
    return SecurityConfigurationBuilder.builder()
        .scopeSeparator(",")
        .additionalQueryStringParams(null)
        .useBasicAuthenticationWithAccessCodeGrant(false)
        .build();
  }
}
