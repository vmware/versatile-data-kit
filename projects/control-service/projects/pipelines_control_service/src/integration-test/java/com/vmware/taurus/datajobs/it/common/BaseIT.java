/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs.it.common;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import com.vmware.taurus.controlplane.model.data.*;
import com.vmware.taurus.service.credentials.KerberosCredentialsRepository;
import com.vmware.taurus.service.kubernetes.ControlKubernetesService;
import com.vmware.taurus.service.kubernetes.DataJobsKubernetesService;
import com.vmware.taurus.service.model.JobConfig;
import io.kubernetes.client.openapi.ApiException;
import org.apache.commons.lang3.StringUtils;
import org.hamcrest.BaseMatcher;
import org.hamcrest.Description;
import org.hamcrest.Matcher;
import org.jetbrains.annotations.NotNull;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.extension.ExtendWith;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.TestConfiguration;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Import;
import org.springframework.context.annotation.Primary;
import org.springframework.http.MediaType;
import org.springframework.test.annotation.DirtiesContext;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.util.ReflectionTestUtils;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import org.springframework.web.context.WebApplicationContext;

import java.time.Instant;
import java.time.OffsetDateTime;
import java.util.List;
import java.util.concurrent.TimeUnit;
import java.util.function.Predicate;
import java.util.stream.Collectors;

import static org.awaitility.Awaitility.await;
import static org.junit.jupiter.api.Assertions.*;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.user;
import static org.springframework.security.test.web.servlet.setup.SecurityMockMvcConfigurers.springSecurity;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@AutoConfigureMockMvc
@ActiveProfiles({"test"})
@Import({BaseIT.KerberosConfig.class})
@DirtiesContext(classMode = DirtiesContext.ClassMode.BEFORE_EACH_TEST_METHOD)
@ExtendWith(WebHookServerMockExtension.class)
public class BaseIT extends KerberosSecurityTestcaseJunit5 {

  private static Logger log = LoggerFactory.getLogger(BaseIT.class);

  public static final String TEST_JOB_SCHEDULE = "15 10 * * *";
  public static final String TEST_JOB_DEPLOYMENT_ID = "testing";
  protected static final String TEST_USERNAME = "user";

  protected static final String JOBS_URI = "/data-jobs/for-team/supercollider/jobs";
  protected static final String HEADER_X_OP_ID = "X-OPID";

  protected static final ObjectMapper mapper = new ObjectMapper();
  private final ObjectMapper objectMapper =
      new ObjectMapper()
          .registerModule(new JavaTimeModule()); // Used for converting to OffsetDateTime;

  @TestConfiguration
  static class KerberosConfig {

    @Bean
    @Primary
    public KerberosCredentialsRepository credentialsRepository() {
      return new MiniKdcCredentialsRepository();
    }
  }

  @Autowired private MiniKdcCredentialsRepository kerberosCredentialsRepository;

  @Autowired protected DataJobsKubernetesService dataJobsKubernetesService;

  @Autowired protected ControlKubernetesService controlKubernetesService;

  @Autowired protected MockMvc mockMvc;

  @Autowired private WebApplicationContext context;

  @Value("${integrationTest.dataJobsNamespace:}")
  private String dataJobsNamespace;

  private boolean ownsDataJobsNamespace = false;

  @Value("${integrationTest.controlNamespace:}")
  private String controlNamespace;

  private boolean ownsControlNamespace = false;

  @BeforeEach
  public void before() throws Exception {
    log.info("Running test with: {} bytes of memory.", Runtime.getRuntime().totalMemory());
    mockMvc = MockMvcBuilders.webAppContextSetup(context).apply(springSecurity()).build();

    kerberosCredentialsRepository.setMiniKdc(getKdc());

    if (StringUtils.isBlank(dataJobsNamespace)) {
      dataJobsNamespace = "test-ns-" + Instant.now().toEpochMilli();
      log.info("Create namespace {}", dataJobsNamespace);
      dataJobsKubernetesService.createNamespace(dataJobsNamespace);
      this.ownsDataJobsNamespace = true;
    } else {
      log.info("Using predefined data jobs namespace {}", dataJobsNamespace);
    }
    ReflectionTestUtils.setField(dataJobsKubernetesService, "namespace", dataJobsNamespace);

    if (StringUtils.isBlank(controlNamespace)) {
      controlNamespace = "test-ns-" + Instant.now().toEpochMilli();
      ;
      log.info("Create namespace {}", controlNamespace);
      controlKubernetesService.createNamespace(controlNamespace);
      this.ownsControlNamespace = true;
    } else {
      log.info("Using predefined control namespace {}", controlNamespace);
    }
    ReflectionTestUtils.setField(controlKubernetesService, "namespace", controlNamespace);
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
    return new BaseMatcher<String>() {
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

  protected void checkDataJobExecutionStatus(
      String executionId,
      DataJobExecution.StatusEnum executionStatus,
      String opId,
      String jobName,
      String teamName,
      String username)
      throws Exception {

    try {
      testDataJobExecutionRead(executionId, executionStatus, opId, jobName, teamName, username);
      testDataJobExecutionList(executionId, executionStatus, opId, jobName, teamName, username);
      testDataJobDeploymentExecutionList(
          executionId, executionStatus, opId, jobName, teamName, username);
      testDataJobExecutionLogs(executionId, jobName, teamName, username);
    } catch (Error e) {
      try {
        // print logs in case execution has failed
        MvcResult dataJobExecutionLogsResult =
            getExecuteLogs(executionId, jobName, teamName, username);
        log.info(
            "Job Execution {} logs:\n{}",
            executionId,
            dataJobExecutionLogsResult.getResponse().getContentAsString());
      } catch (Error ignore) {
      }
      throw e;
    }
  }

  private void testDataJobExecutionRead(
      String executionId,
      DataJobExecution.StatusEnum executionStatus,
      String opId,
      String jobName,
      String teamName,
      String username) {

    DataJobExecution[] dataJobExecution = new DataJobExecution[1];

    await()
        .atMost(5, TimeUnit.MINUTES)
        .with()
        .pollInterval(15, TimeUnit.SECONDS)
        .until(
            () -> {
              String dataJobExecutionReadUrl =
                  String.format(
                      "/data-jobs/for-team/%s/jobs/%s/executions/%s",
                      teamName, jobName, executionId);
              MvcResult dataJobExecutionResult =
                  mockMvc
                      .perform(
                          get(dataJobExecutionReadUrl)
                              .with(user(username))
                              .contentType(MediaType.APPLICATION_JSON))
                      .andExpect(status().isOk())
                      .andReturn();

              dataJobExecution[0] =
                  objectMapper.readValue(
                      dataJobExecutionResult.getResponse().getContentAsString(),
                      DataJobExecution.class);
              if (dataJobExecution[0] == null) {
                log.info("No response from server");
              } else {
                log.info("Response from server  " + dataJobExecution[0].getStatus());
              }
              return dataJobExecution[0] != null
                  && executionStatus.equals(dataJobExecution[0].getStatus());
            });

    assertDataJobExecutionValid(
        executionId, executionStatus, opId, dataJobExecution[0], jobName, username);
  }

  private void testDataJobExecutionList(
      String executionId,
      DataJobExecution.StatusEnum executionStatus,
      String opId,
      String jobName,
      String teamName,
      String username)
      throws Exception {

    String dataJobExecutionListUrl =
        String.format("/data-jobs/for-team/%s/jobs/%s/executions", teamName, jobName);
    MvcResult dataJobExecutionResult =
        mockMvc
            .perform(
                get(dataJobExecutionListUrl)
                    .with(user(username))
                    .contentType(MediaType.APPLICATION_JSON))
            .andExpect(status().isOk())
            .andReturn();

    List<DataJobExecution> dataJobExecutions =
        objectMapper.readValue(
            dataJobExecutionResult.getResponse().getContentAsString(), new TypeReference<>() {});
    assertNotNull(dataJobExecutions);
    dataJobExecutions =
        dataJobExecutions.stream()
            .filter(e -> e.getId().equals(executionId))
            .collect(Collectors.toList());
    assertEquals(1, dataJobExecutions.size());
    assertDataJobExecutionValid(
        executionId, executionStatus, opId, dataJobExecutions.get(0), jobName, username);
  }

  private void testDataJobDeploymentExecutionList(
      String executionId,
      DataJobExecution.StatusEnum executionStatus,
      String opId,
      String jobName,
      String teamName,
      String username)
      throws Exception {

    String dataJobDeploymentExecutionListUrl =
        String.format(
            "/data-jobs/for-team/%s/jobs/%s/deployments/%s/executions",
            teamName, jobName, "release");
    MvcResult dataJobExecutionResult =
        mockMvc
            .perform(
                get(dataJobDeploymentExecutionListUrl)
                    .with(user(username))
                    .contentType(MediaType.APPLICATION_JSON))
            .andExpect(status().isOk())
            .andReturn();

    List<DataJobExecution> dataJobExecutions =
        objectMapper.readValue(
            dataJobExecutionResult.getResponse().getContentAsString(), new TypeReference<>() {});
    assertNotNull(dataJobExecutions);
    dataJobExecutions =
        dataJobExecutions.stream()
            .filter(e -> e.getId().equals(executionId))
            .collect(Collectors.toList());
    assertEquals(1, dataJobExecutions.size());
    assertDataJobExecutionValid(
        executionId, executionStatus, opId, dataJobExecutions.get(0), jobName, username);
  }

  private void testDataJobExecutionLogs(
      String executionId, String jobName, String teamName, String username) throws Exception {
    MvcResult dataJobExecutionLogsResult = getExecuteLogs(executionId, jobName, teamName, username);
    assertFalse(dataJobExecutionLogsResult.getResponse().getContentAsString().isEmpty());
  }

  @NotNull
  private MvcResult getExecuteLogs(
      String executionId, String jobName, String teamName, String username) throws Exception {
    String dataJobExecutionListUrl =
        String.format(
            "/data-jobs/for-team/%s/jobs/%s/executions/%s/logs", teamName, jobName, executionId);
    MvcResult dataJobExecutionLogsResult =
        mockMvc
            .perform(get(dataJobExecutionListUrl).with(user(username)))
            .andExpect(status().isOk())
            .andReturn();
    return dataJobExecutionLogsResult;
  }

  private void assertDataJobExecutionValid(
      String executionId,
      DataJobExecution.StatusEnum executionStatus,
      String opId,
      DataJobExecution dataJobExecution,
      String jobName,
      String username) {

    assertNotNull(dataJobExecution);
    assertEquals(executionId, dataJobExecution.getId());
    assertEquals(jobName, dataJobExecution.getJobName());
    assertEquals(executionStatus, dataJobExecution.getStatus());
    assertEquals(DataJobExecution.TypeEnum.MANUAL, dataJobExecution.getType());
    assertEquals(username + "/" + "user", dataJobExecution.getStartedBy());
    assertEquals(opId, dataJobExecution.getOpId());
  }
}
