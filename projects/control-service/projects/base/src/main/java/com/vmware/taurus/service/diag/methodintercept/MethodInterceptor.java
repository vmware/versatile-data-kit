/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.diag.methodintercept;

import com.vmware.taurus.base.EnableComponents;
import com.vmware.taurus.service.diag.OperationContext;
import org.aspectj.lang.ProceedingJoinPoint;
import org.aspectj.lang.annotation.Around;
import org.aspectj.lang.annotation.Aspect;
import org.aspectj.lang.annotation.Pointcut;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;
import org.springframework.util.StopWatch;

import java.util.concurrent.Executor;
import java.util.concurrent.Executors;
import java.util.function.Consumer;

/**
 * An aspect to intercept method invocations and record diagnostics information regarding method
 * calls. The intention is to record all method calls annotated with Measurable. Data is sent both
 * to PH as well as logged as metrics to OI.
 *
 * <p>About AOP: the instrumentation/injection (weaving) is done at runtime using proxies (Spring
 * AOP).
 */
@Aspect
@Component
@org.springframework.boot.autoconfigure.condition.ConditionalOnProperty(
    value = EnableComponents.DIAGNOSTICS_INTERCEPTOR,
    havingValue = "true",
    matchIfMissing = true)
public class MethodInterceptor {
  private Logger log = LoggerFactory.getLogger(this.getClass());

  @Autowired
  public MethodInterceptor(
      OperationContext operationContext, Consumer<DiagnosticsContext> diagsConsumer) {
    this.diagnosticsExecutor = Executors.newFixedThreadPool(5);
    // this.phUtil = phoneHomeUtil;
    this.operationContext = operationContext;
    this.diagsConsumer = diagsConsumer;
  }

  private final OperationContext operationContext;
  private final Consumer<DiagnosticsContext> diagsConsumer;

  private Executor diagnosticsExecutor;

  @Pointcut("within(@com.vmware.taurus.service.diag.methodintercept.Measurable *)")
  public void beanAnnotatedWithMeasurable() {}

  @Pointcut("within(@com.vmware.taurus.service.diag.methodintercept.MeasurableContainer *)")
  public void beanAnnotatedWithMeasurableContainer() {}

  @Pointcut("execution(@com.vmware.taurus.service.diag.methodintercept.Measurable * *(..))")
  public void methodAnnotatedWithMeasurable() {}

  @Pointcut(
      "execution(@com.vmware.taurus.service.diag.methodintercept.MeasurableContainer * *(..))")
  public void methodAnnotatedWithMeasurableContainer() {}

  /**
   * Around advice for all methods annotated with Measurable.
   *
   * @param pjp ProceedingJoinPoint
   * @return Object output from targeted method invocation
   * @throws Throwable if there's any error on target method invocation
   */
  @Around(
      "methodAnnotatedWithMeasurable() || beanAnnotatedWithMeasurable() "
          + "|| methodAnnotatedWithMeasurableContainer() || beanAnnotatedWithMeasurableContainer()")
  public Object aroundMethod(final ProceedingJoinPoint pjp) throws Throwable {
    Object res;
    DiagnosticsContext diagContext = new DiagnosticsContext();
    diagContext.methodResult = diagContext;
    try {
      diagContext.joinPoint = pjp;
      diagContext.stopWatch = new StopWatch();
      diagContext.stopWatch.start();
      diagContext.methodResult = res = pjp.proceed();
    } catch (Exception e) {
      diagContext.error = e;
      throw e;
    } finally {
      after(diagContext);
    }
    return res;
  }

  private void after(DiagnosticsContext diagnosticsContext) {
    try {
      diagnosticsContext.stopWatch.stop();
      diagnosticsContext.opId = this.operationContext.getOpId();
      operationContext.setJoinPoint(diagnosticsContext.joinPoint);
      this.diagsConsumer.accept(diagnosticsContext);
    } catch (Exception e) { // do not fail business logic because of diagnostics
      log.warn("Failed gathering metrics. Continuing.", e);
    }
  }
}
