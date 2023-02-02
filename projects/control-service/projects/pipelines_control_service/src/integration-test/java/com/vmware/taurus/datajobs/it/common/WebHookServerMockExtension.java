/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs.it.common;

import static org.junit.jupiter.api.extension.ExtensionContext.Namespace.GLOBAL;
import static org.mockserver.matchers.Times.exactly;
import static org.mockserver.model.HttpRequest.request;
import static org.mockserver.model.HttpResponse.response;

import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;

import io.netty.handler.codec.http.HttpMethod;
import org.junit.jupiter.api.extension.BeforeAllCallback;
import org.junit.jupiter.api.extension.ExtensionContext;
import org.mockserver.client.MockServerClient;
import org.mockserver.integration.ClientAndServer;
import org.mockserver.model.Header;
import org.mockserver.model.HttpResponse;
import org.mockserver.model.HttpStatusCode;
import org.springframework.test.context.junit.jupiter.SpringExtension;

/**
 * Extension that initializes {@link ClientAndServer} and mocks web hook operations. It is used for
 * testing of Control Service web hooks. Example
 * usage: @ExtendWith(WebHookServerMockExtension.class) public class ExampleDataJobIT { @Test public
 * void testCreateDataJob_postCreateWebHookShouldReturnSuccess() { // Execute create job (Post
 * Create WebHook will return success for this call)
 * mockMvc.perform(post(String.format("/data-jobs/for-team/%s/jobs", TEST_TEAM_NAME))
 * .with(user("user")) .content(dataJobRequestBody) .contentType(MediaType.APPLICATION_JSON))
 * .andExpect(status().isCreated()) .andExpect(header().string(HttpHeaders.LOCATION, lambdaMatcher(s
 * -> s.endsWith(String.format("/data-jobs/for-team/%s/jobs/%s", TEST_TEAM_NAME, TEST_JOB_NAME)))));
 * } }
 */
public class WebHookServerMockExtension
    implements BeforeAllCallback, ExtensionContext.Store.CloseableResource {

  private static final Lock LOCK = new ReentrantLock();
  private static final int TEST_INTERNAL_ERROR_RETRIES = 2;

  public static final String TEST_TEAM_NAME = "test-team";
  public static final String TEST_TEAM_WRONG_NAME = "test-example-team";
  public static final String NEW_TEST_TEAM_NAME = "new-test-team";
  public static final String TEST_JOB_NAME = "test-job";
  public static final String TEST_CLIENT_ERROR_TEAM = "test-client-error-team";
  public static final String TEST_CLIENT_ERROR_JOB_NAME = "test-client-error-job";
  public static final String TEST_INTERNAL_ERROR_TEAM = "test-internal-error-team";
  public static final String TEST_INTERNAL_ERROR_JOB_NAME = "test-internal-error-job";
  public static final String TEST_INTERNAL_ERROR_RETRIED_TEAM = "test-internal-error-retried-team";
  public static final String TEST_INTERNAL_ERROR_RETRIED_JOB_NAME =
      "test-internal-error-retried-job";
  public static final String TEST_JOB_1 = "test-job-1";
  public static final String TEST_JOB_2 = "test-job-2";
  public static final String TEST_JOB_3 = "test-job-3";
  public static final String TEST_JOB_4 = "test-job-4";
  public static final String TEST_JOB_5 = "test-job-5";
  public static final String TEST_JOB_6 = "test-job-6";

  private ClientAndServer mockWebHookServer;
  private MockServerClient mockWebHookServerClient;

  @Override
  public void beforeAll(ExtensionContext context) {
    LOCK.lock();
    String uniqueKey = this.getClass().getName();
    Object value = context.getRoot().getStore(GLOBAL).get(uniqueKey);

    if (value == null) {
      String mockedWebHookServerHost =
          SpringExtension.getApplicationContext(context)
              .getEnvironment()
              .getProperty("integrationTest.mockedWebHookServerHost");

      int mockedWebHookServerPort =
          Integer.parseInt(
              SpringExtension.getApplicationContext(context)
                  .getEnvironment()
                  .getProperty("integrationTest.mockedWebHookServerPort"));

      prepareWebHookServerMock(mockedWebHookServerHost, mockedWebHookServerPort);
      context.getRoot().getStore(GLOBAL).put(uniqueKey, this);
    }

    LOCK.unlock();
  }

  @Override
  public void close() {
    mockWebHookServer.close();
    mockWebHookServerClient.close();
  }

  private void prepareWebHookServerMock(
      String mockedWebHookServerHost, int mockedWebHookServerPort) {
    this.mockWebHookServer = ClientAndServer.startClientAndServer(mockedWebHookServerPort);
    this.mockWebHookServerClient =
        new MockServerClient(mockedWebHookServerHost, mockedWebHookServerPort);

    mockSuccessfulPostCreateWebHook();
    mockFailingPostCreateWebHook();
    mockSuccessfulPostDeleteWebHook();
    mockFailingPostDeleteWebHook();
  }

  private void mockFailingPostDeleteWebHook() {
    mockWebHookServerClient
        .when(
            request()
                .withMethod(HttpMethod.POST.name())
                .withHeader("Content-type", "application/json")
                .withPath(
                    String.format(
                        "/data-jobs/for-team/%s/jobs/%s",
                        TEST_CLIENT_ERROR_TEAM, TEST_CLIENT_ERROR_JOB_NAME)))
        .respond(getClientErrorResponse());

    mockWebHookServerClient
        .when(
            request()
                .withMethod(HttpMethod.POST.name())
                .withHeader("Content-type", "application/json")
                .withPath(
                    String.format(
                        "/data-jobs/for-team/%s/jobs/%s",
                        TEST_INTERNAL_ERROR_TEAM, TEST_INTERNAL_ERROR_JOB_NAME)))
        .respond(getInternalServerErrorResponse());

    // Retry 2 times - will return Error 500 range
    mockWebHookServerClient
        .when(
            request()
                .withMethod(HttpMethod.POST.name())
                .withHeader("Content-type", "application/json")
                .withPath(
                    String.format(
                        "/data-jobs/for-team/%s/jobs/%s",
                        TEST_INTERNAL_ERROR_RETRIED_TEAM, TEST_INTERNAL_ERROR_RETRIED_JOB_NAME)),
            exactly(TEST_INTERNAL_ERROR_RETRIES))
        .respond(getInternalServerErrorResponse());

    // 3-rd retry - will return 200 OK range
    mockWebHookServerClient
        .when(
            request()
                .withMethod(HttpMethod.POST.name())
                .withHeader("Content-type", "application/json")
                .withPath(
                    String.format(
                        "/data-jobs/for-team/%s/jobs/%s",
                        TEST_INTERNAL_ERROR_RETRIED_TEAM, TEST_INTERNAL_ERROR_RETRIED_JOB_NAME)),
            exactly(TEST_INTERNAL_ERROR_RETRIES + 1))
        .respond(getOkResponse());
  }

  private void mockSuccessfulPostDeleteWebHook() {
    mockWebHookServerClient
        .when(
            request()
                .withMethod(HttpMethod.POST.name())
                .withHeader("Content-type", "application/json")
                .withPath(
                    String.format("/data-jobs/for-team/%s/jobs/%s", TEST_TEAM_NAME, TEST_JOB_NAME)))
        .respond(getOkResponse());

    mockWebHookServerClient
        .when(
            request()
                .withMethod(HttpMethod.POST.name())
                .withHeader("Content-type", "application/json")
                .withPath(
                    String.format(
                        "/data-jobs/for-team/%s/jobs/%s",
                        TEST_TEAM_NAME, JobExecutionUtil.JOB_NAME_PREFIX + ".*")))
        .respond(getOkResponse());

    mockWebHookServerClient
        .when(
            request()
                .withMethod(HttpMethod.POST.name())
                .withHeader("Content-type", "application/json")
                .withPath(
                    String.format("/data-jobs/for-team/%s/jobs/%s", TEST_TEAM_NAME, TEST_JOB_1)))
        .respond(getOkResponse());

    mockWebHookServerClient
        .when(
            request()
                .withMethod(HttpMethod.POST.name())
                .withHeader("Content-type", "application/json")
                .withPath(
                    String.format("/data-jobs/for-team/%s/jobs/%s", TEST_TEAM_NAME, TEST_JOB_2)))
        .respond(getOkResponse());

    mockWebHookServerClient
        .when(
            request()
                .withMethod(HttpMethod.POST.name())
                .withHeader("Content-type", "application/json")
                .withPath(
                    String.format(
                        "/data-jobs/for-team/%s/jobs/%s", NEW_TEST_TEAM_NAME, TEST_JOB_3)))
        .respond(getOkResponse());

    mockWebHookServerClient
        .when(
            request()
                .withMethod(HttpMethod.POST.name())
                .withHeader("Content-type", "application/json")
                .withPath(
                    String.format(
                        "/data-jobs/for-team/%s/jobs/%s", NEW_TEST_TEAM_NAME, TEST_JOB_4)))
        .respond(getOkResponse());

    mockWebHookServerClient
        .when(
            request()
                .withMethod(HttpMethod.POST.name())
                .withHeader("Content-type", "application/json")
                .withPath(
                    String.format(
                        "/data-jobs/for-team/%s/jobs/%s", NEW_TEST_TEAM_NAME, TEST_JOB_5)))
        .respond(getOkResponse());

    mockWebHookServerClient
        .when(
            request()
                .withMethod(HttpMethod.POST.name())
                .withHeader("Content-type", "application/json")
                .withPath(
                    String.format("/data-jobs/for-team/%s/jobs/%s", TEST_TEAM_NAME, TEST_JOB_6)))
        .respond(getOkResponse());
  }

  private void mockFailingPostCreateWebHook() {
    mockWebHookServerClient
        .when(
            request()
                .withMethod(HttpMethod.POST.name())
                .withHeader("Content-type", "application/json")
                .withPath(String.format("/data-jobs/for-team/%s/jobs", TEST_CLIENT_ERROR_TEAM)))
        .respond(getClientErrorResponse());

    mockWebHookServerClient
        .when(
            request()
                .withMethod(HttpMethod.POST.name())
                .withHeader("Content-type", "application/json")
                .withPath(String.format("/data-jobs/for-team/%s/jobs", TEST_INTERNAL_ERROR_TEAM)))
        .respond(getInternalServerErrorResponse());

    // Retry 2 times - will return Error 500 range
    mockWebHookServerClient
        .when(
            request()
                .withMethod(HttpMethod.POST.name())
                .withHeader("Content-type", "application/json")
                .withPath(
                    String.format("/data-jobs/for-team/%s/jobs", TEST_INTERNAL_ERROR_RETRIED_TEAM)),
            exactly(TEST_INTERNAL_ERROR_RETRIES))
        .respond(getInternalServerErrorResponse());

    // 3-rd retry - will return 200 OK range
    mockWebHookServerClient
        .when(
            request()
                .withMethod(HttpMethod.POST.name())
                .withHeader("Content-type", "application/json")
                .withPath(
                    String.format("/data-jobs/for-team/%s/jobs", TEST_INTERNAL_ERROR_RETRIED_TEAM)),
            exactly(TEST_INTERNAL_ERROR_RETRIES + 1))
        .respond(getOkResponse());
  }

  private void mockSuccessfulPostCreateWebHook() {
    mockWebHookServerClient
        .when(
            request()
                .withMethod(HttpMethod.POST.name())
                .withHeader("Content-type", "application/json")
                .withPath(String.format("/data-jobs/for-team/%s/jobs", TEST_TEAM_NAME)))
        .respond(getOkResponse());

    mockWebHookServerClient
        .when(
            request()
                .withMethod(HttpMethod.POST.name())
                .withHeader("Content-type", "application/json")
                .withPath(String.format("/data-jobs/for-team/%s/jobs", NEW_TEST_TEAM_NAME)))
        .respond(getOkResponse());
  }

  private HttpResponse getOkResponse() {
    return response()
        .withStatusCode(HttpStatusCode.OK_200.code())
        .withHeaders(new Header("Content-Type", "application/json; charset=utf-8"))
        .withBody("{ \"message\": \"Success\" }");
  }

  private HttpResponse getClientErrorResponse() {
    return response()
        .withStatusCode(HttpStatusCode.BAD_REQUEST_400.code())
        .withHeaders(new Header("Content-Type", "application/json; charset=utf-8"))
        .withBody("{ \"message\": \"Client error\" }");
  }

  private HttpResponse getInternalServerErrorResponse() {
    return response()
        .withStatusCode(HttpStatusCode.BAD_GATEWAY_502.code())
        .withHeaders(new Header("Content-Type", "application/json; charset=utf-8"))
        .withBody("{ \"message\": \"Internal Server Error\" }");
  }
}
