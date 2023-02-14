/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.webhook;

import com.vmware.taurus.authorization.provider.AuthorizationProvider;
import com.vmware.taurus.service.model.DataJob;
import lombok.AllArgsConstructor;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Service;

/**
 * Helper service which provide useful methods to construct various types of WebHookRequestBody
 * instances.
 */
@Service
@AllArgsConstructor
public class WebHookRequestBodyProvider {
  private static final String CREATE_OPERATION_PATH = "/data-jobs/for-team/%s/jobs";
  private static final String DELETE_OPERATION_PATH = CREATE_OPERATION_PATH + "/%s";

  private final AuthorizationProvider authorizationProvider;

  public WebHookRequestBody constructPostDeleteBody(DataJob jobInfo) {
    WebHookRequestBody body = constructWebHookRequestBody(jobInfo);
    body.setRequestedHttpPath(
        String.format(DELETE_OPERATION_PATH, jobInfo.getJobConfig().getTeam(), jobInfo.getName()));
    body.setRequestedHttpVerb("DELETE");
    return body;
  }

  public WebHookRequestBody constructPostCreateBody(DataJob jobInfo) {
    WebHookRequestBody body = constructWebHookRequestBody(jobInfo);
    body.setRequestedHttpPath(
        String.format(CREATE_OPERATION_PATH, jobInfo.getJobConfig().getTeam()));
    body.setRequestedHttpVerb("POST");
    return body;
  }

  private WebHookRequestBody constructWebHookRequestBody(DataJob jobInfo) {
    WebHookRequestBody body = new WebHookRequestBody();
    body.setRequesterUserId(
        authorizationProvider.getUserId(SecurityContextHolder.getContext().getAuthentication()));
    body.setRequestedResourceTeam(jobInfo.getJobConfig().getTeam());
    body.setRequestedResourceName("data-job");
    body.setRequestedResourceId(jobInfo.getName());
    return body;
  }
}
