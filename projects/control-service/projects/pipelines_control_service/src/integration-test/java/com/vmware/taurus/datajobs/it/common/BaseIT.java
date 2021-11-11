/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs.it.common;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.vmware.taurus.controlplane.model.data.*;
import com.vmware.taurus.service.credentials.KerberosCredentialsRepository;
import com.vmware.taurus.service.kubernetes.ControlKubernetesService;
import com.vmware.taurus.service.kubernetes.DataJobsKubernetesService;
import com.vmware.taurus.service.model.JobConfig;
import io.kubernetes.client.ApiException;
import io.netty.handler.codec.http.HttpMethod;
import org.apache.commons.lang3.StringUtils;
import org.hamcrest.BaseMatcher;
import org.hamcrest.Description;
import org.hamcrest.Matcher;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockserver.client.server.MockServerClient;
import org.mockserver.integration.ClientAndServer;
import org.mockserver.model.Header;
import org.mockserver.model.HttpResponse;
import org.mockserver.model.HttpStatusCode;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.TestConfiguration;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Import;
import org.springframework.context.annotation.Primary;
import org.springframework.security.kerberos.test.KerberosSecurityTestcase;
import org.springframework.test.annotation.DirtiesContext;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.util.ReflectionTestUtils;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import org.springframework.web.context.WebApplicationContext;

import java.time.Instant;
import java.util.function.Predicate;

import static org.mockserver.matchers.Times.exactly;
import static org.mockserver.model.HttpRequest.request;
import static org.mockserver.model.HttpResponse.response;
import static org.springframework.security.test.web.servlet.setup.SecurityMockMvcConfigurers.springSecurity;

@AutoConfigureMockMvc
@ActiveProfiles({"test"})
@Import({BaseIT.KerberosConfig.class})
@DirtiesContext(classMode = DirtiesContext.ClassMode.BEFORE_EACH_TEST_METHOD)
public class BaseIT extends KerberosSecurityTestcaseJunit5 {

   private static Logger log = LoggerFactory.getLogger(BaseIT.class);

   public static final String TEST_TEAM_NAME = "test-team";
   public static final String TEST_TEAM_WRONG_NAME = "test-example-team";
   public static final String NEW_TEST_TEAM_NAME = "new-test-team";
   public static final String TEST_JOB_NAME = "test-job";
   public static final String TEST_CLIENT_ERROR_TEAM = "test-client-error-team";
   public static final String TEST_CLIENT_ERROR_JOB_NAME = "test-client-error-job";
   public static final String TEST_INTERNAL_ERROR_TEAM = "test-internal-error-team";
   public static final String TEST_INTERNAL_ERROR_JOB_NAME = "test-internal-error-job";
   public static final String TEST_INTERNAL_ERROR_RETRIED_TEAM = "test-internal-error-retried-team";
   public static final String TEST_INTERNAL_ERROR_RETRIED_JOB_NAME = "test-internal-error-retried-job";
   private static final int TEST_INTERNAL_ERROR_RETRIES = 2;
   public static final String TEST_JOB_SCHEDULE = "15 10 * * *";
   public static final String TEST_JOB_DEPLOYMENT_ID = "testing";

   public static final String TEST_JOB_1 = "test-job-1";
   public static final String TEST_JOB_2 = "test-job-2";
   public static final String TEST_JOB_3 = "test-job-3";
   public static final String TEST_JOB_4 = "test-job-4";
   public static final String TEST_JOB_5 = "test-job-5";
   public static final String TEST_JOB_6 = "test-job-6";

   protected static final ObjectMapper mapper = new ObjectMapper();

   @TestConfiguration
   static class KerberosConfig {

      @Bean
      @Primary
      public KerberosCredentialsRepository credentialsRepository(){
         return new MiniKdcCredentialsRepository();
      }
   }

   @Autowired
   private MiniKdcCredentialsRepository kerberosCredentialsRepository;

   @Autowired
   protected DataJobsKubernetesService dataJobsKubernetesService;

   @Autowired
   protected ControlKubernetesService controlKubernetesService;

   @Autowired
   protected MockMvc mockMvc;

   @Autowired
   private WebApplicationContext context;

   @Value("${integrationTest.dataJobsNamespace:}")
   private String dataJobsNamespace;
   private boolean ownsDataJobsNamespace = false;
   @Value("${integrationTest.controlNamespace:}")
   private String controlNamespace;
   private boolean ownsControlNamespace = false;

   @Value("${integrationTest.mockedWebHookServerHost}")
   private String webHookServerHost;
   @Value("${integrationTest.mockedWebHookServerPort}")
   private int webHookServerPort;
   private ClientAndServer mockWebHookServer;
   private MockServerClient mockWebHookServerClient;

   @BeforeEach
   public void before() throws Exception {
      mockMvc = MockMvcBuilders
              .webAppContextSetup(context)
              .apply(springSecurity())
              .build();

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
         controlNamespace = "test-ns-" + Instant.now().toEpochMilli();;
         log.info("Create namespace {}", controlNamespace);
         controlKubernetesService.createNamespace(controlNamespace);
         this.ownsControlNamespace = true;
      } else {
         log.info("Using predefined control namespace {}", controlNamespace);
      }
      ReflectionTestUtils.setField(controlKubernetesService, "namespace", controlNamespace);

      prepareWebHookServerMock();
   }

   private void prepareWebHookServerMock() {
      mockWebHookServer = ClientAndServer.startClientAndServer(webHookServerPort);
      mockWebHookServerClient = new MockServerClient(webHookServerHost, webHookServerPort);
      mockSuccessfulPostCreateWebHook();
      mockFailingPostCreateWebHook();
      mockSuccessfulPostDeleteWebHook();
      mockFailingPostDeleteWebHook();
   }

   private void mockFailingPostDeleteWebHook() {
      mockWebHookServerClient.when(
              request()
                      .withMethod(HttpMethod.POST.name())
                      .withHeader("'Content-type', 'application/json'")
                      .withPath(String.format("/data-jobs/for-team/%s/jobs/%s", TEST_CLIENT_ERROR_TEAM,
                              TEST_CLIENT_ERROR_JOB_NAME)))
              .respond(getClientErrorResponse());

      mockWebHookServerClient.when(
              request()
                      .withMethod(HttpMethod.POST.name())
                      .withHeader("'Content-type', 'application/json'")
                      .withPath(String.format("/data-jobs/for-team/%s/jobs/%s",
                              TEST_INTERNAL_ERROR_TEAM, TEST_INTERNAL_ERROR_JOB_NAME)))
              .respond(getInternalServerErrorResponse());

      //Retry 2 times - will return Error 500 range
      mockWebHookServerClient.when(
              request()
                      .withMethod(HttpMethod.POST.name())
                      .withHeader("'Content-type', 'application/json'")
                      .withPath(String.format("/data-jobs/for-team/%s/jobs/%s",
                              TEST_INTERNAL_ERROR_RETRIED_TEAM, TEST_INTERNAL_ERROR_RETRIED_JOB_NAME)),
              exactly(TEST_INTERNAL_ERROR_RETRIES))
              .respond(getInternalServerErrorResponse());

      //3-rd retry - will return 200 OK range
      mockWebHookServerClient.when(
              request()
                      .withMethod(HttpMethod.POST.name())
                      .withHeader("'Content-type', 'application/json'")
                      .withPath(String.format("/data-jobs/for-team/%s/jobs/%s",
                              TEST_INTERNAL_ERROR_RETRIED_TEAM, TEST_INTERNAL_ERROR_RETRIED_JOB_NAME)),
              exactly(TEST_INTERNAL_ERROR_RETRIES + 1))
              .respond(getOkResponse());
   }

   private void mockSuccessfulPostDeleteWebHook() {
      mockWebHookServerClient.when(
              request()
                      .withMethod(HttpMethod.POST.name())
                      .withHeader("'Content-type', 'application/json'")
                      .withPath(String.format("/data-jobs/for-team/%s/jobs/%s",
                              TEST_TEAM_NAME, TEST_JOB_NAME)))
              .respond(getOkResponse());

      mockWebHookServerClient.when(
              request()
                      .withMethod(HttpMethod.POST.name())
                      .withHeader("'Content-type', 'application/json'")
                      .withPath(String.format("/data-jobs/for-team/%s/jobs/%s",
                              TEST_TEAM_NAME, TEST_JOB_1)))
              .respond(getOkResponse());

      mockWebHookServerClient.when(
              request()
                      .withMethod(HttpMethod.POST.name())
                      .withHeader("'Content-type', 'application/json'")
                      .withPath(String.format("/data-jobs/for-team/%s/jobs/%s",
                              TEST_TEAM_NAME, TEST_JOB_2)))
              .respond(getOkResponse());

      mockWebHookServerClient.when(
              request()
                      .withMethod(HttpMethod.POST.name())
                      .withHeader("'Content-type', 'application/json'")
                      .withPath(String.format("/data-jobs/for-team/%s/jobs/%s",
                              NEW_TEST_TEAM_NAME, TEST_JOB_3)))
              .respond(getOkResponse());

      mockWebHookServerClient.when(
              request()
                      .withMethod(HttpMethod.POST.name())
                      .withHeader("'Content-type', 'application/json'")
                      .withPath(String.format("/data-jobs/for-team/%s/jobs/%s",
                              NEW_TEST_TEAM_NAME, TEST_JOB_4)))
              .respond(getOkResponse());

      mockWebHookServerClient.when(
            request()
                  .withMethod(HttpMethod.POST.name())
                  .withHeader("'Content-type', 'application/json'")
                  .withPath(String.format("/data-jobs/for-team/%s/jobs/%s",
                        NEW_TEST_TEAM_NAME, TEST_JOB_5)))
            .respond(getOkResponse());

      mockWebHookServerClient.when(
            request()
                  .withMethod(HttpMethod.POST.name())
                  .withHeader("'Content-type', 'application/json'")
                  .withPath(String.format("/data-jobs/for-team/%s/jobs/%s",
                        TEST_TEAM_NAME, TEST_JOB_6)))
            .respond(getOkResponse());
   }

   private void mockFailingPostCreateWebHook() {
      mockWebHookServerClient.when(
              request()
                      .withMethod(HttpMethod.POST.name())
                      .withHeader("'Content-type', 'application/json'")
                      .withPath(String.format("/data-jobs/for-team/%s/jobs", TEST_CLIENT_ERROR_TEAM)))
              .respond(getClientErrorResponse());

      mockWebHookServerClient.when(
              request()
                      .withMethod(HttpMethod.POST.name())
                      .withHeader("'Content-type', 'application/json'")
                      .withPath(String.format("/data-jobs/for-team/%s/jobs", TEST_INTERNAL_ERROR_TEAM)))
              .respond(getInternalServerErrorResponse());

      //Retry 2 times - will return Error 500 range
      mockWebHookServerClient.when(
              request()
                      .withMethod(HttpMethod.POST.name())
                      .withHeader("'Content-type', 'application/json'")
                      .withPath(String.format("/data-jobs/for-team/%s/jobs", TEST_INTERNAL_ERROR_RETRIED_TEAM)),
              exactly(TEST_INTERNAL_ERROR_RETRIES))
              .respond(getInternalServerErrorResponse());

      //3-rd retry - will return 200 OK range
      mockWebHookServerClient.when(
              request()
                      .withMethod(HttpMethod.POST.name())
                      .withHeader("'Content-type', 'application/json'")
                      .withPath(String.format("/data-jobs/for-team/%s/jobs", TEST_INTERNAL_ERROR_RETRIED_TEAM)),
              exactly(TEST_INTERNAL_ERROR_RETRIES + 1))
              .respond(getOkResponse());
   }

   private void mockSuccessfulPostCreateWebHook() {
      mockWebHookServerClient.when(
              request()
                      .withMethod(HttpMethod.POST.name())
                      .withHeader("'Content-type', 'application/json'")
                      .withPath(String.format("/data-jobs/for-team/%s/jobs", TEST_TEAM_NAME)))
              .respond(getOkResponse());

      mockWebHookServerClient.when(
              request()
                      .withMethod(HttpMethod.POST.name())
                      .withHeader("'Content-type', 'application/json'")
                      .withPath(String.format("/data-jobs/for-team/%s/jobs", NEW_TEST_TEAM_NAME)))
              .respond(getOkResponse());
   }

   private HttpResponse getOkResponse() {
      return response()
              .withStatusCode(HttpStatusCode.OK_200.code())
              .withHeaders(
                      new Header("Content-Type", "application/json; charset=utf-8"))
              .withBody("{ \"message\": \"Success\" }");
   }

   private HttpResponse getClientErrorResponse() {
      return response()
              .withStatusCode(HttpStatusCode.BAD_REQUEST_400.code())
              .withHeaders(
                      new Header("Content-Type", "application/json; charset=utf-8"))
              .withBody("{ \"message\": \"Client error\" }");
   }

   private HttpResponse getInternalServerErrorResponse() {
      return response()
              .withStatusCode(HttpStatusCode.BAD_GATEWAY_502.code())
              .withHeaders(
                      new Header("Content-Type", "application/json; charset=utf-8"))
              .withBody("{ \"message\": \"Internal Server Error\" }");
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

      mockWebHookServer.stop();
   }

   protected Matcher<String> lambdaMatcher(Predicate<String> predicate) {
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

   protected String getDataJobRequestBody(String teamName, String jobName) throws JsonProcessingException {
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

   protected com.vmware.taurus.service.model.DataJob getDataJobRepositoryModel(String teamName, String jobName) {
      var job = new com.vmware.taurus.service.model.DataJob();
      job.setName(jobName);
      JobConfig config = new JobConfig();
      config.setTeam(teamName);
      config.setSchedule(TEST_JOB_SCHEDULE);
      job.setJobConfig(config);
      return job;
   }

   public static String getDataJobDeploymentRequestBody(String jobVersion) throws JsonProcessingException {
      var jobDeployment = new com.vmware.taurus.controlplane.model.data.DataJobDeployment();
      jobDeployment.setVdkVersion("");
      jobDeployment.setJobVersion(jobVersion);
      jobDeployment.setMode(DataJobMode.RELEASE);
      jobDeployment.setEnabled(true);
      jobDeployment.setResources(new DataJobResources());
      jobDeployment.setSchedule(new DataJobSchedule());
      jobDeployment.setId(TEST_JOB_DEPLOYMENT_ID);

      return mapper.writeValueAsString(jobDeployment);
   }

   public String getDataJobDeploymentEnableRequestBody(boolean enabled) throws JsonProcessingException {
      var enable = new DataJobDeployment();
      enable.enabled(enabled);
      return mapper.writeValueAsString(enable);
   }

   public String getDataJobDeploymentVdkVersionRequestBody(String vdkVersion) throws JsonProcessingException {
      var deployment = new DataJobDeployment();
      deployment.setVdkVersion(vdkVersion);
      return mapper.writeValueAsString(deployment);
   }
}
