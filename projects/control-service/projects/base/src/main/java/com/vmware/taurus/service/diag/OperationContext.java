/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.diag;

import com.vmware.taurus.service.diag.opid.OpIdSupplier;
import org.aspectj.lang.JoinPoint;
import org.slf4j.MDC;
import org.springframework.stereotype.Component;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.util.UUID;

/** OperationContext - component to set get and remove OpId for a given thread. */
@Component
public class OperationContext implements OpIdSupplier {
  private ThreadLocal<String> id = new InheritableThreadLocal<>();
  private ThreadLocal<String> workflowId = new InheritableThreadLocal<>();
  private ThreadLocal<String> retryAction = new InheritableThreadLocal<>();
  private ThreadLocal<UUID> taskId = new InheritableThreadLocal<>();
  private ThreadLocal<HttpServletRequest> refToRequest = new InheritableThreadLocal<>();
  private ThreadLocal<HttpServletResponse> refToResponse = new InheritableThreadLocal<>();
  private ThreadLocal<JoinPoint> refToJoinPoint = new InheritableThreadLocal<>();
  private ThreadLocal<String> refToUser = new InheritableThreadLocal<>();
  private ThreadLocal<String> refToTeam = new InheritableThreadLocal<>();

  /*
   * initId Intialize with new opId and register with MDC.
   */
  public void initId() {
    String id;
    synchronized (OperationContext.class) {
      id = OperationContext.class.getCanonicalName() + System.nanoTime();
    }
    MDC.put("OpId", id);
    setId(id);
  }

  /*
   * initId Intialize with passed in opId and register with MDC.
   */
  public void initId(UUID workflowId) {
    initId();
    setWorkflowId(workflowId.toString());
  }

  public void setId(String id) {
    this.id.set(id);
    MDC.put("OpId", id);
  }

  @Override
  public String getOpId() {
    return id.get();
  }

  /*
   * removeId Remove all traces from this thread.
   */
  public void removeId() {
    id.remove();
    MDC.remove("OpId");
  }

  public void setTaskId(UUID taskId) {
    this.taskId.set(taskId);
  }

  public UUID getTaskId() {
    return taskId.get();
  }

  public void removeTaskId() {
    taskId.remove();
  }

  /*
   * Set the workflowId.
   */
  public void setWorkflowId(String workflowId) {
    this.workflowId.set(workflowId);
  }

  /*
   * Gets the workflowId.
   */
  public String getWorkflowId() {
    return workflowId.get();
  }

  /*
   * Removes the workflowId from the threadLocal and MDC.
   */
  public void removeWorkflowId() {
    workflowId.remove();
  }

  /*
   * Set the workflowId.
   */
  public void setRetryAction(String retryAction) {
    this.retryAction.set(retryAction);
  }

  /*
   * Gets the retryAction value.
   */
  public String getRetryAction() {
    if (retryAction == null) {
      return Boolean.FALSE.toString();
    }
    return retryAction.get();
  }

  /*
   * Removes the retryAction from the threadLocal and MDC.
   */
  public void removeRetryAction() {
    retryAction.remove();
  }

  /*
   * Removes the workflowId from the threadLocal and MDC.
   */
  public void removeAll() {
    removeId();
    removeTaskId();
    removeWorkflowId();
  }

  public String toString() {
    return super.toString() + "[" + "opId:" + getOpId() + "]";
  }

  public void setHttpRequest(HttpServletRequest request) {
    this.refToRequest.set(request);
  }

  public HttpServletRequest getRequest() {
    return refToRequest.get();
  }

  public HttpServletResponse getResponse() {
    return refToResponse.get();
  }

  public void setHttpResponse(HttpServletResponse response) {
    this.refToResponse.set(response);
  }

  public JoinPoint getJoinPoint() {
    return refToJoinPoint.get();
  }

  public void setJoinPoint(JoinPoint joinPoint) {
    this.refToJoinPoint.set(joinPoint);
  }

  public void setUser(String user) {
    this.refToUser.set(user);
  }

  public String getUser() {
    return refToUser.get();
  }

  public void setTeam(String team) {
    this.refToTeam.set(team);
  }

  public String getTeam() {
    return refToTeam.get();
  }
}
