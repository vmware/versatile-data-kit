/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service;

import lombok.extern.slf4j.Slf4j;
import org.springframework.aop.framework.Advised;
import org.springframework.beans.BeansException;
import org.springframework.beans.factory.config.BeanPostProcessor;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.Ordered;
import org.springframework.lang.Nullable;
import org.springframework.retry.interceptor.RetryInterceptorBuilder;
import org.springframework.retry.interceptor.RetryOperationsInterceptor;

@Slf4j
@Configuration
public class RepositoryRetryOperationsConfiguration {

  @Bean
  public RepositoryRetryOperationsInterceptor repositoryRetryOperationsInterceptor() {
    return new RepositoryRetryOperationsInterceptor();
  }

  class RepositoryRetryOperationsInterceptor implements BeanPostProcessor, Ordered {

    @Override
    public int getOrder() {
      return Integer.MAX_VALUE;
    }

    @Override
    @Nullable
    public Object postProcessAfterInitialization(Object bean, String beanName)
        throws BeansException {
      if (bean instanceof JobsRepository || bean instanceof JobExecutionRepository) {
        Advised advised = (Advised) bean;
        RetryOperationsInterceptor interceptor =
            RetryInterceptorBuilder.stateless()
                .maxAttempts(3)
                .backOffOptions(1000, 2.0, 3000)
                .recoverer(
                    (args, cause) -> {
                      log.error("The query retries has been exhausted: " + cause.getMessage());
                      throw (RuntimeException) cause;
                    })
                .build();
        advised.addAdvice(0, interceptor);
      }

      return bean;
    }
  }
}
