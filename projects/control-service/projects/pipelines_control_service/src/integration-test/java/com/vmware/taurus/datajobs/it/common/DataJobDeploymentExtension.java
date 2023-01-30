/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs.it.common;

import static org.awaitility.Awaitility.await;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.extension.ExtensionContext.Namespace.GLOBAL;
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
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;

import com.fasterxml.jackson.databind.ObjectMapper;
import io.kubernetes.client.openapi.ApiException;
import lombok.Builder;
import org.apache.commons.io.IOUtils;
import org.apache.commons.lang3.StringUtils;
import org.junit.jupiter.api.extension.BeforeEachCallback;
import org.junit.jupiter.api.extension.ExtensionContext;
import org.junit.jupiter.api.extension.ParameterContext;
import org.junit.jupiter.api.extension.ParameterResolutionException;
import org.junit.jupiter.api.extension.ParameterResolver;
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
    implements BeforeEachCallback, ExtensionContext.Store.CloseableResource, ParameterResolver {

  private static final Lock LOCK = new ReentrantLock();
  protected final ObjectMapper MAPPER = new ObjectMapper();

  private String JOB_NAME =
      "integration-test-" + UUID.randomUUID().toString().substring(0, 8);
  private String JOB_NOTIFIED_EMAIL = "versatiledatakit@vmware.com";
  private String JOB_SCHEDULE = "*/2 * * * *";
  private String USER_NAME = "user";
  private String DEPLOYMENT_ID = "NOT_USED";
  private String TEAM_NAME = "test-team";

  private final Map<String, Object> SUPPORTED_PARAMETERS =
      Map.of(
          "jobName",
          JOB_NAME,
          "username",
          USER_NAME,
          "deploymentId",
          DEPLOYMENT_ID,
          "teamName",
          TEAM_NAME);

  private ExtensionContext context;

  private String jobSource = "simple_job.zip";

  private boolean jobGlobal = true;

  private boolean initialized = false;

  @Builder
  private static DataJobDeploymentExtension of(String jobSource, Boolean jobGlobal){
    DataJobDeploymentExtension dataJobDeploymentExtension = new DataJobDeploymentExtension();

    if (StringUtils.isNotBlank(jobSource)) {
      dataJobDeploymentExtension.jobSource = jobSource;
    }

    if (jobGlobal != null) {
      dataJobDeploymentExtension.jobGlobal = jobGlobal;
    }

    return dataJobDeploymentExtension;
  }

  @Override
  public void beforeEach(ExtensionContext context) throws Exception {
    this.context = context;
    MockMvc mockMvc = SpringExtension.getApplicationContext(context).getBean(MockMvc.class);
    DataJobsKubernetesService dataJobsKubernetesService =
        SpringExtension.getApplicationContext(context).getBean(DataJobsKubernetesService.class);

    // Setup
    String dataJobRequestBody = BaseIT.getDataJobRequestBody(TEAM_NAME, JOB_NAME);

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
                                    "/data-jobs/for-team/%s/jobs/%s", TEAM_NAME, JOB_NAME)))));

    String uniqueKey = this.getClass().getName();

    if (jobGlobal) {
      LOCK.lock();

      if (context.getRoot().getStore(GLOBAL).get(uniqueKey) != null) {
        initialized = true;
      }
    }

    if (!initialized) {
      byte[] jobZipBinary =
          IOUtils.toByteArray(getClass().getClassLoader().getResourceAsStream(jobSource));

      // Upload the data job
      MvcResult uploadResult =
          mockMvc
              .perform(
                  post(String.format("/data-jobs/for-team/%s/jobs/%s/sources", TEAM_NAME, JOB_NAME))
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
              .jobName(JOB_NAME)
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
          put(String.format("/data-jobs/for-team/%s/jobs/%s", TEAM_NAME, JOB_NAME))
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
              post(String.format("/data-jobs/for-team/%s/jobs/%s/deployments", TEAM_NAME, JOB_NAME))
                  .with(user(USER_NAME))
                  .content(MAPPER.writeValueAsString(dataJobDeployment))
                  .contentType(MediaType.APPLICATION_JSON))
          .andExpect(status().isAccepted())
          .andReturn();

      // Verify that the job deployment was created
      String jobDeploymentName = JobImageDeployer.getCronJobName(JOB_NAME);
      await()
              .atMost(360, TimeUnit.SECONDS)
              .with()
              .pollInterval(10, TimeUnit.SECONDS)
              .until(() -> dataJobsKubernetesService.readCronJob(jobDeploymentName).isEmpty());
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

      if (jobGlobal) {
        context.getRoot().getStore(GLOBAL).put(uniqueKey, this);
        context.getRoot().getStore(GLOBAL).put("jobName", JOB_NAME);
      }
    }

    if (jobGlobal) {
      LOCK.unlock();
    }
  }

  @Override
  public void close() throws Throwable {
    if (jobGlobal) {
      JOB_NAME = (String) context.getRoot().getStore(GLOBAL).get("jobName");
    }

    MockMvc mockMvc = SpringExtension.getApplicationContext(context).getBean(MockMvc.class);
    DataJobsKubernetesService dataJobsKubernetesService =
        SpringExtension.getApplicationContext(context).getBean(DataJobsKubernetesService.class);

    // Execute delete deployment
    mockMvc
        .perform(
            delete(
                    String.format(
                        "/data-jobs/for-team/%s/jobs/%s/deployments/%s",
                        TEAM_NAME, JOB_NAME, DEPLOYMENT_ID))
                .with(user(USER_NAME))
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isAccepted());

    // Wait for deployment to be deleted
    String jobDeploymentName = JobImageDeployer.getCronJobName(JOB_NAME);
    await()
        .atMost(5, TimeUnit.SECONDS)
        .with()
        .pollInterval(1, TimeUnit.SECONDS)
        .until(() -> dataJobsKubernetesService.readCronJob(jobDeploymentName).isEmpty());

    mockMvc
        .perform(
            delete(String.format("/data-jobs/for-team/%s/jobs/%s/sources", TEAM_NAME, JOB_NAME))
                .with(user(USER_NAME))
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isOk());

    // Finally, delete the K8s jobs to avoid them messing up subsequent runs of the same test
    dataJobsKubernetesService.listJobs().stream()
        .filter(jobName -> jobName.startsWith(JOB_NAME))
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
    if (jobGlobal && parameterContext.getParameter().getName() == "jobName") {
      return context.getRoot().getStore(GLOBAL).get("jobName");
    }

    return SUPPORTED_PARAMETERS.getOrDefault(parameterContext.getParameter().getName(), null);
  }
}
