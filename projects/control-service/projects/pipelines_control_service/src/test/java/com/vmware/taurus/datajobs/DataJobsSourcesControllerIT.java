/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.service.upload.FileUtils;
import com.vmware.taurus.service.upload.GitWrapper;
import org.apache.commons.io.IOUtils;
import org.eclipse.jgit.api.Git;
import org.eclipse.jgit.api.errors.GitAPIException;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.junit.jupiter.api.io.TempDir;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.http.MediaType;
import org.springframework.security.test.context.support.WithMockUser;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.context.TestContext;
import org.springframework.test.context.TestExecutionListener;
import org.springframework.test.context.TestExecutionListeners;
import org.springframework.test.context.junit.jupiter.SpringExtension;
import org.springframework.test.util.ReflectionTestUtils;
import org.springframework.test.web.servlet.MockMvc;

import java.io.File;
import java.nio.file.Path;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest(
    webEnvironment = SpringBootTest.WebEnvironment.MOCK,
    classes = ControlplaneApplication.class)
@ExtendWith(SpringExtension.class)
@AutoConfigureMockMvc
@ActiveProfiles({"MockKubernetes", "MockKerberos", "unittest", "MockTelemetry"})
@TestExecutionListeners(
    listeners = DataJobsSourcesControllerIT.SetGitUrlAsTempFolder.class,
    mergeMode = TestExecutionListeners.MergeMode.MERGE_WITH_DEFAULTS)
public class DataJobsSourcesControllerIT {

  @TempDir static File temporaryFolder;

  // team name can have spaces in it so we are purposefully using one with space
  private static final String TEST_TEAM_NAME = "test team";
  private static final String TEST_JOB_NAME = "test-job-sources";

  @Autowired private MockMvc mockMvc;

  private final ObjectMapper mapper = new ObjectMapper();

  static class SetGitUrlAsTempFolder implements TestExecutionListener {

    @Override
    public void beforeTestExecution(TestContext testContext) throws GitAPIException {
      if (testContext.hasApplicationContext()) {
        GitWrapper bean = testContext.getApplicationContext().getBean(GitWrapper.class);

        var git = Git.init().setDirectory(temporaryFolder).call();
        git.commit().setMessage("Initial commit").call();
        ReflectionTestUtils.setField(bean, "gitDataJobsUrl", "file://" + temporaryFolder);
      }
    }
  }

  @BeforeEach
  public void beforeEach() throws Exception {
    var job = TestUtils.getDataJob(TEST_TEAM_NAME, TEST_JOB_NAME);

    String body = mapper.writeValueAsString(job);
    mockMvc
        .perform(
            post(String.format("/data-jobs/for-team/%s/jobs", TEST_TEAM_NAME))
                .content(body)
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isCreated());
  }

  @AfterEach
  public void afterEach() throws Exception {
    mockMvc
        .perform(
            delete(String.format("/data-jobs/for-team/%s/jobs/%s", TEST_TEAM_NAME, TEST_JOB_NAME))
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isOk());
  }

  @Test
  @WithMockUser
  public void testDataJobSourcesNotFound() throws Exception {
    mockMvc
        .perform(
            get(
                String.format(
                    "/data-jobs/for-team/%s/jobs/%s/sources", TEST_TEAM_NAME, TEST_JOB_NAME)))
        .andExpect(status().isNotFound());
  }

  @Test
  @WithMockUser
  public void testDataJobSourcesUploadDownload(@TempDir Path tempDir) throws Exception {
    byte[] jobZipBinary =
        IOUtils.toByteArray(
            getClass().getClassLoader().getResourceAsStream("file_test/test_job.zip"));

    mockMvc
        .perform(
            post(String.format(
                    "/data-jobs/for-team/%s/jobs/%s/sources", TEST_TEAM_NAME, TEST_JOB_NAME))
                .content(jobZipBinary)
                .contentType(MediaType.APPLICATION_OCTET_STREAM))
        .andExpect(status().isOk());

    var downlaodedJobZipBinary =
        mockMvc
            .perform(
                get(
                    String.format(
                        "/data-jobs/for-team/%s/jobs/%s/sources", TEST_TEAM_NAME, TEST_JOB_NAME)))
            .andExpect(status().isOk())
            .andReturn()
            .getResponse()
            .getContentAsByteArray();
    File jobDir =
        FileUtils.unzipDataJob(
            new ByteArrayResource(downlaodedJobZipBinary), tempDir.toFile(), TEST_JOB_NAME);
    Assertions.assertTrue(jobDir.isDirectory());
  }
}
