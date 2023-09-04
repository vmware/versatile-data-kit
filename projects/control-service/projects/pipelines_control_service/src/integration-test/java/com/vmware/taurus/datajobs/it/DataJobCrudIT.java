/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs.it;

import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.datajobs.it.common.BaseIT;
import com.vmware.taurus.service.repository.JobsRepository;
import com.vmware.taurus.service.credentials.JobCredentialsService;
import com.vmware.taurus.service.model.DataJob;
import org.apache.commons.lang3.ArrayUtils;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;

import static com.vmware.taurus.datajobs.it.common.WebHookServerMockExtension.NEW_TEST_TEAM_NAME;
import static com.vmware.taurus.datajobs.it.common.WebHookServerMockExtension.TEST_CLIENT_ERROR_JOB_NAME;
import static com.vmware.taurus.datajobs.it.common.WebHookServerMockExtension.TEST_CLIENT_ERROR_TEAM;
import static com.vmware.taurus.datajobs.it.common.WebHookServerMockExtension.TEST_INTERNAL_ERROR_JOB_NAME;
import static com.vmware.taurus.datajobs.it.common.WebHookServerMockExtension.TEST_INTERNAL_ERROR_RETRIED_JOB_NAME;
import static com.vmware.taurus.datajobs.it.common.WebHookServerMockExtension.TEST_INTERNAL_ERROR_RETRIED_TEAM;
import static com.vmware.taurus.datajobs.it.common.WebHookServerMockExtension.TEST_INTERNAL_ERROR_TEAM;
import static com.vmware.taurus.datajobs.it.common.WebHookServerMockExtension.TEST_JOB_NAME;
import static com.vmware.taurus.datajobs.it.common.WebHookServerMockExtension.TEST_TEAM_NAME;
import static com.vmware.taurus.datajobs.it.common.WebHookServerMockExtension.TEST_TEAM_WRONG_NAME;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.user;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest(
    webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT,
    classes = ControlplaneApplication.class)
public class DataJobCrudIT extends BaseIT {

  @Autowired private JobsRepository jobsRepository;

  @Test
  public void testDataJobCrud() throws Exception {
    // Setup
    String dataJobRequestBody = getDataJobRequestBody(TEST_TEAM_NAME, TEST_JOB_NAME);

    // Execute create job (Post Create WebHook will return success for this call)
    mockMvc
        .perform(
            post(String.format("/data-jobs/for-team/%s/jobs", TEST_TEAM_NAME))
                .with(user("user"))
                .content(dataJobRequestBody)
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isCreated())
        .andExpect(
            header()
                .string(
                    HttpHeaders.LOCATION,
                    lambdaMatcher(
                        s ->
                            s.endsWith(
                                String.format(
                                    "/data-jobs/for-team/%s/jobs/%s",
                                    TEST_TEAM_NAME, TEST_JOB_NAME)))));
    // Validate - the job is created
    Assertions.assertTrue(jobsRepository.existsById(TEST_JOB_NAME));

    // Execute create job with no user
    mockMvc
        .perform(
            post(String.format("/data-jobs/for-team/%s/jobs", TEST_TEAM_NAME))
                .content(dataJobRequestBody)
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isUnauthorized());

    testDataJobPostCreateWebHooks();

    // Execute get swagger with no user
    mockMvc
        .perform(
            get("/data-jobs/swagger-ui.html")
                .content(dataJobRequestBody)
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().is3xxRedirection());

    // Execute get swagger with no user
    mockMvc
        .perform(
            get("/data-jobs/swagger-ui/index.html")
                .content(dataJobRequestBody)
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isOk());

    mockMvc
        .perform(
            get("/data-jobs/swagger-ui/swagger-ui.css")
                .content(dataJobRequestBody)
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isOk());
    mockMvc
        .perform(
            get("/data-jobs/swagger-ui/swagger-ui-bundle.js")
                .content(dataJobRequestBody)
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isOk());

    mockMvc
        .perform(
            get("/data-jobs/api-docs")
                .content(dataJobRequestBody)
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isOk());

    // Validation
    // Validate keytab created
    var keytabSecretName = JobCredentialsService.getJobKeytabKubernetesSecretName(TEST_JOB_NAME);
    var keytabSecretData = dataJobsKubernetesService.getSecretData(keytabSecretName);
    Assertions.assertFalse(keytabSecretData.isEmpty());
    Assertions.assertTrue(keytabSecretData.containsKey("keytab"));
    Assertions.assertTrue(ArrayUtils.isNotEmpty(keytabSecretData.get("keytab")));

    // Validate persisted job
    var jobFromDbOptional = jobsRepository.findById(TEST_JOB_NAME);
    Assertions.assertTrue(jobFromDbOptional.isPresent());
    var jobFromDb = jobFromDbOptional.get();
    Assertions.assertEquals(TEST_JOB_SCHEDULE, jobFromDb.getJobConfig().getSchedule());

    // Execute list jobs
    // deprecated jobsList in favour of jobsQuery
    mockMvc
        .perform(
            get(String.format("/data-jobs/for-team/%s/jobs", TEST_TEAM_NAME))
                .with(user("user"))
                .param(
                    "query",
                    "query($filter: [Predicate], $pageNumber: Int) {"
                        + "  jobs(pageNumber: $pageNumber, filter: $filter) {"
                        + "    content {"
                        + "      jobName"
                        + "    }"
                        + "  }"
                        + "}")
                .param(
                    "variables",
                    "{"
                        + "\"filter\": ["
                        + "    {"
                        + "      \"property\": \"config.team\","
                        + "      \"pattern\": \""
                        + TEST_TEAM_NAME
                        + "\""
                        + "    }"
                        + "  ],"
                        + "\"pageNumber\": 1"
                        + "}")
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isOk())
        .andExpect(content().string(lambdaMatcher(s -> (s.contains(TEST_JOB_NAME)))));

    // Execute list jobs with no user
    // deprecated jobsList in favour of jobsQuery
    mockMvc
        .perform(get(String.format("/data-jobs/for-team/%s/jobs", TEST_TEAM_NAME)))
        .andExpect(status().isUnauthorized())
        .andExpect(content().string(lambdaMatcher(s -> s.isBlank())));

    // Execute get job with user
    mockMvc
        .perform(
            get(String.format("/data-jobs/for-team/%s/jobs/%s", TEST_TEAM_NAME, TEST_JOB_NAME))
                .with(user("user")))
        .andExpect(status().isOk())
        .andExpect(content().string(lambdaMatcher(s -> s.contains(TEST_JOB_NAME))))
        .andExpect(content().string(lambdaMatcher(s -> s.contains(TEST_JOB_SCHEDULE))));

    // Execute get job with user and wrong team
    mockMvc
        .perform(
            get(String.format(
                    "/data-jobs/for-team/%s/jobs/%s", TEST_TEAM_WRONG_NAME, TEST_JOB_NAME))
                .with(user("user")))
        .andExpect(status().isNotFound());

    // Execute get job without user
    mockMvc
        .perform(
            get(String.format("/data-jobs/for-team/%s/jobs/%s", TEST_TEAM_NAME, TEST_JOB_NAME)))
        .andExpect(status().isUnauthorized())
        .andExpect(content().string(lambdaMatcher(s -> s.isBlank())));

    // Execute update job team with user
    mockMvc
        .perform(
            put(String.format(
                    "/data-jobs/for-team/%s/jobs/%s/team/%s",
                    TEST_TEAM_WRONG_NAME, TEST_JOB_NAME, NEW_TEST_TEAM_NAME))
                .with(user("user")))
        .andExpect(status().isNotFound());

    // Execute update job team with no user
    mockMvc
        .perform(
            put(
                String.format(
                    "/data-jobs/for-team/%s/jobs/%s/team/%s",
                    TEST_TEAM_NAME, TEST_JOB_NAME, NEW_TEST_TEAM_NAME)))
        .andExpect(status().isUnauthorized());

    // Execute update job team with same team and user
    mockMvc
        .perform(
            put(String.format(
                    "/data-jobs/for-team/%s/jobs/%s/team/%s",
                    TEST_TEAM_NAME, TEST_JOB_NAME, TEST_TEAM_NAME))
                .with(user("user")))
        .andExpect(status().isOk());

    // Execute update job team with empty team
    mockMvc
        .perform(
            put(String.format(
                    "/data-jobs/for-team/%s/jobs/%s/team/ ", TEST_TEAM_NAME, TEST_JOB_NAME))
                .with(user("user")))
        .andExpect(status().isNotFound());

    // Execute update job team with user
    mockMvc
        .perform(
            put(String.format(
                    "/data-jobs/for-team/%s/jobs/%s/team/%s",
                    TEST_TEAM_NAME, TEST_JOB_NAME, TEST_TEAM_NAME))
                .with(user("user")))
        .andExpect(status().isOk());

    // Execute update job team with non existing job
    mockMvc
        .perform(
            put(String.format("/data-jobs/for-team/%s/jobs/missing-job/team/", TEST_TEAM_NAME))
                .with(user("user")))
        .andExpect(status().isNotFound());

    // Execute update job team with empty job name
    mockMvc
        .perform(
            put(String.format(
                    "/data-jobs/for-team/%s/jobs/ /team/%s", TEST_TEAM_NAME, NEW_TEST_TEAM_NAME))
                .with(user("user")))
        .andExpect(status().isNotFound());

    // Execute update job team with missing job name
    mockMvc
        .perform(
            put(String.format(
                    "/data-jobs/for-team/%s/jobs//team/%s", TEST_TEAM_NAME, NEW_TEST_TEAM_NAME))
                .with(user("user")))
        .andExpect(status().isNotFound());

    // Execute get not allowed method to job team endpoint
    mockMvc
        .perform(
            get(String.format(
                    "/data-jobs/for-team/%s/jobs/%s/team/%s",
                    TEST_TEAM_NAME, TEST_JOB_NAME, TEST_TEAM_NAME))
                .with(user("user")))
        .andExpect(status().isMethodNotAllowed());

    // Execute put method with user and with wrong team
    // TODO: uncomment and extend tests to cover all put operations not only NotFound
    mockMvc
        .perform(
            put(String.format(
                    "/data-jobs/for-team/%s/jobs/%s", TEST_TEAM_WRONG_NAME, TEST_JOB_NAME))
                .with(user("user"))
                .contentType(MediaType.APPLICATION_JSON)
                .content(dataJobRequestBody))
        .andExpect(status().isNotFound());

    // Execute delete job with no user
    mockMvc
        .perform(
            delete(String.format("/data-jobs/for-team/%s/jobs/%s", TEST_TEAM_NAME, TEST_JOB_NAME))
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isUnauthorized());

    // Execute delete job with user and wrong team
    mockMvc
        .perform(
            delete(
                    String.format(
                        "/data-jobs/for-team/%s/jobs/%s", TEST_TEAM_WRONG_NAME, TEST_JOB_NAME))
                .with(user("user"))
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isNotFound());

    // Execute delete job with user
    mockMvc
        .perform(
            delete(String.format("/data-jobs/for-team/%s/jobs/%s", TEST_TEAM_NAME, TEST_JOB_NAME))
                .with(user("user"))
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isOk());

    // Execute update job team after job is deleted from db and is missing
    mockMvc
        .perform(
            put(String.format(
                    "/data-jobs/for-team/%s/jobs/%s/team/%s",
                    TEST_TEAM_NAME, TEST_JOB_NAME, TEST_TEAM_NAME))
                .with(user("user")))
        .andExpect(status().isNotFound());

    // Validate keytab deleted
    keytabSecretData = dataJobsKubernetesService.getSecretData(keytabSecretName);
    Assertions.assertTrue(keytabSecretData.isEmpty());

    // Validate job deleted from db
    Assertions.assertFalse(jobsRepository.existsById(TEST_JOB_NAME));

    testDataJobPostDeleteWebHooks();
  }

  private void testDataJobPostCreateWebHooks() throws Exception {
    // Post Create WebHook will prevent job creation and the result will be propagated error code
    // with no job created
    String clientErrorDataJobRequestBody =
        getDataJobRequestBody(TEST_CLIENT_ERROR_TEAM, TEST_CLIENT_ERROR_JOB_NAME);
    mockMvc
        .perform(
            post(String.format("/data-jobs/for-team/%s/jobs", TEST_CLIENT_ERROR_TEAM))
                .with(user("user"))
                .content(clientErrorDataJobRequestBody)
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isBadRequest());
    // Validate - the job is NOT created
    Assertions.assertFalse(jobsRepository.existsById(TEST_CLIENT_ERROR_JOB_NAME));

    // Post Create WebHook will prevent job creation and the result will be error 503 with no job
    // created
    String internalServerErrorDataJobRequestBody =
        getDataJobRequestBody(TEST_INTERNAL_ERROR_TEAM, TEST_INTERNAL_ERROR_JOB_NAME);
    mockMvc
        .perform(
            post(String.format("/data-jobs/for-team/%s/jobs", TEST_INTERNAL_ERROR_TEAM))
                .with(user("user"))
                .content(internalServerErrorDataJobRequestBody)
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isServiceUnavailable());
    // Validate - the job is NOT created
    Assertions.assertFalse(jobsRepository.existsById(TEST_INTERNAL_ERROR_JOB_NAME));

    // Post Create WebHook will retry 2 times and finally will allow job creation
    String retriedErrorDataJobRequestBody =
        getDataJobRequestBody(
            TEST_INTERNAL_ERROR_RETRIED_TEAM, TEST_INTERNAL_ERROR_RETRIED_JOB_NAME);
    mockMvc
        .perform(
            post(String.format("/data-jobs/for-team/%s/jobs", TEST_INTERNAL_ERROR_RETRIED_TEAM))
                .with(user("user"))
                .content(retriedErrorDataJobRequestBody)
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isCreated());
    // Validate - the job is created
    Assertions.assertTrue(jobsRepository.existsById(TEST_INTERNAL_ERROR_RETRIED_JOB_NAME));
  }

  private void testDataJobPostDeleteWebHooks() throws Exception {
    // Add test job to the repository
    DataJob clientErrorEntity =
        getDataJobRepositoryModel(TEST_CLIENT_ERROR_TEAM, TEST_CLIENT_ERROR_JOB_NAME);
    jobsRepository.save(clientErrorEntity);
    // Post Delete WebHook will prevent job deletion and the result will be propagated error code
    mockMvc
        .perform(
            delete(
                    String.format(
                        "/data-jobs/for-team/%s/jobs/%s",
                        TEST_CLIENT_ERROR_TEAM, TEST_CLIENT_ERROR_JOB_NAME))
                .with(user("user"))
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isBadRequest());
    // Validate - the job is NOT deleted
    Assertions.assertTrue(jobsRepository.existsById(TEST_CLIENT_ERROR_JOB_NAME));
    // Clean Up
    jobsRepository.delete(clientErrorEntity);

    // Add test job to the repository
    DataJob internalServerEntity =
        getDataJobRepositoryModel(TEST_INTERNAL_ERROR_TEAM, TEST_INTERNAL_ERROR_JOB_NAME);
    jobsRepository.save(internalServerEntity);
    // Post Delete WebHook will prevent job deletion and the result will be error 503
    mockMvc
        .perform(
            delete(
                    String.format(
                        "/data-jobs/for-team/%s/jobs/%s",
                        TEST_INTERNAL_ERROR_TEAM, TEST_INTERNAL_ERROR_JOB_NAME))
                .with(user("user"))
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isServiceUnavailable());
    // Validate - the job is NOT deleted
    Assertions.assertTrue(jobsRepository.existsById(TEST_INTERNAL_ERROR_JOB_NAME));
    // Clean Up
    jobsRepository.delete(internalServerEntity);

    // Add test job to the repository
    DataJob internalServerRetriedEntity =
        getDataJobRepositoryModel(
            TEST_INTERNAL_ERROR_RETRIED_TEAM, TEST_INTERNAL_ERROR_RETRIED_JOB_NAME);
    jobsRepository.save(internalServerRetriedEntity);
    // Post Create WebHook will retry 2 times and finally will allow job creation
    mockMvc
        .perform(
            delete(
                    String.format(
                        "/data-jobs/for-team/%s/jobs/%s",
                        TEST_INTERNAL_ERROR_RETRIED_TEAM, TEST_INTERNAL_ERROR_RETRIED_JOB_NAME))
                .with(user("user"))
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isOk());
    // Validate - the job is deleted
    Assertions.assertFalse(jobsRepository.existsById(TEST_INTERNAL_ERROR_RETRIED_JOB_NAME));
    // Clean Up
    jobsRepository.delete(internalServerEntity);
  }

  @Test
  public void testDataJobCreateDeleteIdempotency() throws Exception {
    String dataJobTestBody = getDataJobRequestBody(TEST_TEAM_NAME, TEST_JOB_NAME);

    mockMvc
        .perform(
            post(String.format("/data-jobs/for-team/%s/jobs", TEST_TEAM_NAME))
                .with(user("user"))
                .content(dataJobTestBody)
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isCreated());

    mockMvc
        .perform(
            delete(String.format("/data-jobs/for-team/%s/jobs/%s", TEST_TEAM_NAME, TEST_JOB_NAME))
                .with(user("user"))
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isOk());

    mockMvc
        .perform(
            delete(String.format("/data-jobs/for-team/%s/jobs/%s", TEST_TEAM_NAME, TEST_JOB_NAME))
                .with(user("user"))
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isNotFound());
  }
}
