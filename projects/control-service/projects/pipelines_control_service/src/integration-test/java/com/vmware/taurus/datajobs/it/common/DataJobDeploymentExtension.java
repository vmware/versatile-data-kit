/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs.it.common;

import static org.awaitility.Awaitility.await;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.user;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.delete;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.put;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.header;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import java.lang.reflect.Parameter;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.TimeUnit;

import com.fasterxml.jackson.databind.ObjectMapper;
import io.kubernetes.client.openapi.ApiException;
import lombok.Builder;
import lombok.NoArgsConstructor;
import lombok.NonNull;
import lombok.RequiredArgsConstructor;
import org.apache.commons.io.IOUtils;
import org.apache.commons.lang3.StringUtils;
import org.junit.jupiter.api.extension.*;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.test.context.junit.jupiter.SpringExtension;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;

import com.vmware.taurus.controlplane.model.data.DataJobConfig;
import com.vmware.taurus.controlplane.model.data.DataJobContacts;
import com.vmware.taurus.controlplane.model.data.DataJobDeployment;
import com.vmware.taurus.controlplane.model.data.DataJobMode;
import com.vmware.taurus.controlplane.model.data.DataJobSchedule;
import com.vmware.taurus.controlplane.model.data.DataJobVersion;
import com.vmware.taurus.service.deploy.JobImageDeployer;
import com.vmware.taurus.service.kubernetes.DataJobsKubernetesService;
import com.vmware.taurus.service.model.JobDeploymentStatus;

/**
 * Extension that deploys Data Job before all tests. Before the test execution, the extension
 * creates Data Job and deploys it to Kubernetes Cluster. Also, these properties are injected into
 * each test as method parameters: jobName, teamName, deploymentId and username. Example
 * usage: @ExtendWith(DataJobDeploymentExtension.class) public class ExampleDataJobExecutionIT
 * { @Test public void testExecuteDataJob_shouldExecuteDataJobSuccessfully(String jobName, String
 * teamName, String username) { // Execute data job String opId = jobName +
 * UUID.randomUUID().toString().toLowerCase(); DataJobExecutionRequest dataJobExecutionRequest = new
 * DataJobExecutionRequest() .startedBy(username);
 *
 * <p>String triggerDataJobExecutionUrl = String.format(
 * "/data-jobs/for-team/%s/jobs/%s/deployments/%s/executions", teamName, jobName, "release");
 * MvcResult dataJobExecutionResponse = mockMvc.perform(post(triggerDataJobExecutionUrl)
 * .with(user(username)) .header(HEADER_X_OP_ID, opId)
 * .content(mapper.writeValueAsString(dataJobExecutionRequest))
 * .contentType(MediaType.APPLICATION_JSON)) .andExpect(status().is(202)) .andReturn(); } }
 *
 * <p><b>Note the Data Job is shared between the all tests. Do not delete the job deployment since
 * this may affect other tests.</b>
 */
public class DataJobDeploymentExtension
    implements BeforeEachCallback, AfterAllCallback, ParameterResolver {

  private static final String JOB_NOTIFIED_EMAIL = "versatiledatakit@vmware.com";
  private static final String JOB_SCHEDULE = "*/20 * * * *";
  private static final String USER_NAME = "user";
  private static final String DEPLOYMENT_ID = "NOT_USED";
  private static final String TEAM_NAME = "test-team";

  protected final ObjectMapper MAPPER = new ObjectMapper();

  private String jobName =
          JobExecutionUtil.JOB_NAME_PREFIX + UUID.randomUUID().toString().substring(0, 8);

  private String jobSource = "simple_job.zip";

  private boolean initialized = false;

  private final Map<String, Object> SUPPORTED_PARAMETERS =
      Map.of(
          "jobName",
              jobName,
          "username",
          USER_NAME,
          "deploymentId",
          DEPLOYMENT_ID,
          "teamName",
          TEAM_NAME);

  public DataJobDeploymentExtension() {
  }

  public DataJobDeploymentExtension(String jobName) {
    this.jobName = jobName;
  }

  @Override
  public void beforeEach(ExtensionContext context) throws Exception {
    MockMvc mockMvc = SpringExtension.getApplicationContext(context).getBean(MockMvc.class);
    DataJobsKubernetesService dataJobsKubernetesService =
        SpringExtension.getApplicationContext(context).getBean(DataJobsKubernetesService.class);

    // Setup
    String dataJobRequestBody = BaseIT.getDataJobRequestBody(TEAM_NAME, jobName);
    // Create the data job
    mockMvc
        .perform(
            post(String.format("/data-jobs/for-team/%s/jobs", TEAM_NAME))
                .with(user("user"))
                .content(dataJobRequestBody)
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isCreated())
        .andExpect(
            header()
                .string(
                    HttpHeaders.LOCATION,
                    BaseIT.lambdaMatcher(
                        s ->
                            s.endsWith(
                                String.format(
                                    "/data-jobs/for-team/%s/jobs/%s", TEAM_NAME, jobName)))));

    if (!initialized) {
      byte[] jobZipBinary =
          IOUtils.toByteArray(getClass().getClassLoader().getResourceAsStream(jobSource));

      // Upload the data job
      MvcResult uploadResult =
          mockMvc
              .perform(
                  post(String.format("/data-jobs/for-team/%s/jobs/%s/sources", TEAM_NAME, jobName))
                      .with(user(USER_NAME))
                      .content(jobZipBinary)
                      .contentType(MediaType.APPLICATION_OCTET_STREAM))
              .andExpect(status().isOk())
              .andReturn();
      DataJobVersion dataJobVersion =
          MAPPER.readValue(uploadResult.getResponse().getContentAsString(), DataJobVersion.class);

      // Update the data job configuration
      var dataJob =
          new com.vmware.taurus.controlplane.model.data.DataJob()
              .jobName(jobName)
              .team(TEAM_NAME)
              .config(
                  new DataJobConfig()
                      .enableExecutionNotifications(false)
                      .contacts(
                          new DataJobContacts()
                              .addNotifiedOnJobSuccessItem(JOB_NOTIFIED_EMAIL)
                              .addNotifiedOnJobDeployItem(JOB_NOTIFIED_EMAIL)
                              .addNotifiedOnJobFailurePlatformErrorItem(JOB_NOTIFIED_EMAIL)
                              .addNotifiedOnJobFailureUserErrorItem(JOB_NOTIFIED_EMAIL))
                      .schedule(new DataJobSchedule().scheduleCron(JOB_SCHEDULE)));
      mockMvc.perform(
          put(String.format("/data-jobs/for-team/%s/jobs/%s", TEAM_NAME, jobName))
              .with(user(USER_NAME))
              .content(MAPPER.writeValueAsString(dataJob))
              .contentType(MediaType.APPLICATION_JSON));

      // Deploy the data job
      var dataJobDeployment =
          new DataJobDeployment()
              .jobVersion(dataJobVersion.getVersionSha())
              .mode(DataJobMode.RELEASE)
              .enabled(true);
      mockMvc
          .perform(
              post(String.format("/data-jobs/for-team/%s/jobs/%s/deployments", TEAM_NAME, jobName))
                  .with(user(USER_NAME))
                  .content(MAPPER.writeValueAsString(dataJobDeployment))
                  .contentType(MediaType.APPLICATION_JSON))
          .andExpect(status().isAccepted())
          .andReturn();

      // Verify that the job deployment was created
      String jobDeploymentName = JobImageDeployer.getCronJobName(jobName);
      await()
          .atMost(360, TimeUnit.SECONDS)
          .with()
          .pollInterval(10, TimeUnit.SECONDS)
          .until(() -> dataJobsKubernetesService.readCronJob(jobDeploymentName).isPresent());

      Optional<JobDeploymentStatus> cronJobOptional =
          dataJobsKubernetesService.readCronJob(jobDeploymentName);
      assertTrue(cronJobOptional.isPresent());
      JobDeploymentStatus cronJob = cronJobOptional.get();
      assertEquals(dataJobVersion.getVersionSha(), cronJob.getGitCommitSha());
      assertEquals(DataJobMode.RELEASE.toString(), cronJob.getMode());
      assertEquals(true, cronJob.getEnabled());
      assertTrue(cronJob.getImageName().endsWith(dataJobVersion.getVersionSha()));
      assertEquals(USER_NAME, cronJob.getLastDeployedBy());

      initialized = true;
    }
  }

  @Override
  public void afterAll(ExtensionContext context) throws Exception {
    MockMvc mockMvc = SpringExtension.getApplicationContext(context).getBean(MockMvc.class);
    DataJobsKubernetesService dataJobsKubernetesService =
        SpringExtension.getApplicationContext(context).getBean(DataJobsKubernetesService.class);

    mockMvc
        .perform(
            delete(String.format("/data-jobs/for-team/%s/jobs/%s", TEAM_NAME, jobName))
                .with(user(USER_NAME))
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isOk());

    // Finally, delete the K8s jobs to avoid them messing up subsequent runs of the same test
    dataJobsKubernetesService.listJobs().stream()
        .filter(jobName -> jobName.startsWith(this.jobName))
        .forEach(
            s -> {
              try {
                dataJobsKubernetesService.deleteJob(s);
              } catch (ApiException e) {
                e.printStackTrace();
              }
            });
  }

  @Override
  public boolean supportsParameter(
      ParameterContext parameterContext, ExtensionContext extensionContext)
      throws ParameterResolutionException {
    Parameter parameter = parameterContext.getParameter();
    return String.class.equals(parameter.getType())
        && SUPPORTED_PARAMETERS.containsKey(parameter.getName());
  }

  @Override
  public Object resolveParameter(
      ParameterContext parameterContext, ExtensionContext extensionContext)
      throws ParameterResolutionException {
    return SUPPORTED_PARAMETERS.getOrDefault(parameterContext.getParameter().getName(), null);
  }
}
