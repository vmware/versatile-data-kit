/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs.it.common;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.vmware.taurus.controlplane.model.data.DataJobConfig;
import com.vmware.taurus.controlplane.model.data.DataJobDeployment;
import com.vmware.taurus.controlplane.model.data.DataJobMode;
import com.vmware.taurus.controlplane.model.data.DataJobResources;
import com.vmware.taurus.controlplane.model.data.DataJobSchedule;
import com.vmware.taurus.datajobs.it.DataJobDeploymentCrudIT;
import com.vmware.taurus.service.kubernetes.ControlKubernetesService;
import com.vmware.taurus.service.kubernetes.DataJobsKubernetesService;
import com.vmware.taurus.service.model.JobConfig;
import io.kubernetes.client.openapi.ApiException;
import org.hamcrest.BaseMatcher;
import org.hamcrest.Description;
import org.hamcrest.Matcher;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.extension.ExtendWith;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.context.annotation.Import;
import org.springframework.test.annotation.DirtiesContext;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import org.springframework.web.context.WebApplicationContext;

import java.time.OffsetDateTime;
import java.util.function.Predicate;

import static org.springframework.security.test.web.servlet.setup.SecurityMockMvcConfigurers.springSecurity;

@AutoConfigureMockMvc
@ActiveProfiles({"test"})
@Import({KdcServerConfiguration.class})
@DirtiesContext(classMode = DirtiesContext.ClassMode.BEFORE_EACH_TEST_METHOD)
@ExtendWith(WebHookServerMockExtension.class)
public class BaseIT {
  private static Logger log = LoggerFactory.getLogger(BaseIT.class);

  public static final String TEST_JOB_SCHEDULE = "15 10 * * *";
  public static final String TEST_JOB_DEPLOYMENT_ID = "testing";
  protected static final String TEST_USERNAME = "user";

  protected static final String JOBS_URI = "/data-jobs/for-team/supercollider/jobs";
  protected static final String HEADER_X_OP_ID = "X-OPID";

  protected static final ObjectMapper mapper = new ObjectMapper();

  @Autowired protected DataJobsKubernetesService dataJobsKubernetesService;

  @Autowired protected ControlKubernetesService controlKubernetesService;

  @Autowired protected MockMvc mockMvc;

  @Autowired private WebApplicationContext context;

  @Value("${integrationTest.dataJobsNamespace:}")
  private String dataJobsNamespace;

  private boolean ownsDataJobsNamespace = false;

  @Value("${integrationTest.controlNamespace:}")
  protected String controlNamespace;

  private boolean ownsControlNamespace = false;

  protected final String testJobName = JobExecutionUtil.generateJobName(this.getClass().getSimpleName());

  @BeforeEach
  public void before() {
    log.info("Running test with: {} bytes of memory.", Runtime.getRuntime().totalMemory());
    mockMvc = MockMvcBuilders.webAppContextSetup(context).apply(springSecurity()).build();
  }

  @AfterEach
  public void after() {
    if (ownsDataJobsNamespace) {
      try {
        dataJobsKubernetesService.deleteNamespace(dataJobsNamespace);
      } catch (ApiException e) {
        log.error(String.format("Error while deleting namespace %s", dataJobsNamespace), e);
      }
    }
    if (ownsControlNamespace) {
      try {
        controlKubernetesService.deleteNamespace(controlNamespace);
      } catch (ApiException e) {
        log.error(String.format("Error while deleting namespace %s", controlNamespace), e);
      }
    }
  }

  public static Matcher<String> lambdaMatcher(Predicate<String> predicate) {
    return new BaseMatcher<>() {
      @Override
      public boolean matches(Object actual) {
        return predicate.test((String) actual);
      }

      @Override
      public void describeTo(Description description) {
        description.appendText("failed to match predicate");
      }
    };
  }

  protected Matcher<String> isDate(OffsetDateTime value) {
    return new BaseMatcher<>() {
      @Override
      public boolean matches(Object actual) {
        return value.isEqual(OffsetDateTime.parse((String) actual));
      }

      @Override
      public void describeTo(Description description) {
        description.appendText("failed to match date");
      }
    };
  }

  public static String getDataJobRequestBody(String teamName, String jobName)
      throws JsonProcessingException {
    var job = new com.vmware.taurus.controlplane.model.data.DataJob();
    job.setJobName(jobName);
    job.setTeam(teamName);
    DataJobConfig config = new DataJobConfig();
    DataJobSchedule schedule = new DataJobSchedule();
    schedule.setScheduleCron(TEST_JOB_SCHEDULE);
    config.setSchedule(schedule);
    job.setConfig(config);

    return mapper.writeValueAsString(job);
  }

  protected com.vmware.taurus.service.model.DataJob getDataJobRepositoryModel(
      String teamName, String jobName) {
    var job = new com.vmware.taurus.service.model.DataJob();
    job.setName(jobName);
    JobConfig config = new JobConfig();
    config.setTeam(teamName);
    config.setSchedule(TEST_JOB_SCHEDULE);
    job.setJobConfig(config);
    return job;
  }

  public static String getDataJobDeploymentRequestBody(String jobVersion)
      throws JsonProcessingException {
    var jobDeployment = new com.vmware.taurus.controlplane.model.data.DataJobDeployment();
    jobDeployment.setJobVersion(jobVersion);
    jobDeployment.setMode(DataJobMode.RELEASE);
    jobDeployment.setResources(new DataJobResources());
    jobDeployment.setSchedule(new DataJobSchedule());
    jobDeployment.setId(TEST_JOB_DEPLOYMENT_ID);

    return mapper.writeValueAsString(jobDeployment);
  }

  public static String getDataJobDeploymentRequestBody(String jobVersion, String pythonVersion)
      throws JsonProcessingException {
    var jobDeployment = new com.vmware.taurus.controlplane.model.data.DataJobDeployment();
    jobDeployment.setJobVersion(jobVersion);
    jobDeployment.setMode(DataJobMode.RELEASE);
    jobDeployment.setResources(new DataJobResources());
    jobDeployment.setSchedule(new DataJobSchedule());
    jobDeployment.setId(TEST_JOB_DEPLOYMENT_ID);
    jobDeployment.setPythonVersion(pythonVersion);

    return mapper.writeValueAsString(jobDeployment);
  }

  public String getDataJobDeploymentEnableRequestBody(boolean enabled)
      throws JsonProcessingException {
    var enable = new DataJobDeployment();
    enable.enabled(enabled);
    return mapper.writeValueAsString(enable);
  }

  public String getDataJobDeploymentVdkVersionRequestBody(String vdkVersion)
      throws JsonProcessingException {
    var deployment = new DataJobDeployment();
    deployment.setVdkVersion(vdkVersion);
    return mapper.writeValueAsString(deployment);
  }
}
