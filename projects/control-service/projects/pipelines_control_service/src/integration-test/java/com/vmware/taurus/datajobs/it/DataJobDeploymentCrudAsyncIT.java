/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs.it;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.controlplane.model.data.DataJobDeploymentStatus;
import com.vmware.taurus.controlplane.model.data.DataJobMode;
import com.vmware.taurus.controlplane.model.data.DataJobVersion;
import com.vmware.taurus.datajobs.it.common.BaseIT;
import com.vmware.taurus.service.deploy.JobImageDeployer;
import com.vmware.taurus.service.model.JobDeploymentStatus;
import io.kubernetes.client.openapi.ApiException;
import org.apache.commons.io.IOUtils;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.platform.commons.util.StringUtils;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.test.context.TestPropertySource;
import org.springframework.test.web.servlet.MvcResult;
import org.springframework.test.web.servlet.ResultActions;

import java.time.format.DateTimeFormatter;
import java.util.Optional;
import java.util.concurrent.Callable;
import java.util.concurrent.TimeUnit;

import static com.vmware.taurus.datajobs.it.common.WebHookServerMockExtension.TEST_TEAM_NAME;
import static com.vmware.taurus.datajobs.it.common.WebHookServerMockExtension.TEST_TEAM_WRONG_NAME;
import static org.awaitility.Awaitility.await;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.user;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@TestPropertySource(
    properties = {
      "datajobs.control.k8s.k8sSupportsV1CronJob=true",
      "datajobs.deployment.configuration.persistence.writeTos=DB",
      "datajobs.deployment.configuration.synchronization.task.enabled=true",
      "datajobs.deployment.configuration.synchronization.task.interval.ms=1000",
      "datajobs.deployment.configuration.synchronization.task.initial.delay.ms=0"
    })
@SpringBootTest(
    webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT,
    classes = ControlplaneApplication.class)
public class DataJobDeploymentCrudAsyncIT extends BaseDataJobDeploymentCrudIT {
  @Override
  protected void beforeDeploymentDeletion() {
  }
}
