/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs.it;

//import com.vmware.taurus.RepositoryUtil;

import com.vmware.taurus.ServiceApp;
import com.vmware.taurus.service.JobExecutionRepository;
import com.vmware.taurus.service.JobsRepository;
import com.vmware.taurus.service.deploy.DeploymentService;
import com.vmware.taurus.service.model.*;
import org.junit.jupiter.api.*;
import org.mockito.Mockito;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.request.MockMvcRequestBuilders;

import java.time.OffsetDateTime;
import java.util.List;
import java.util.UUID;

import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest(classes = ServiceApp.class)
@AutoConfigureMockMvc
@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
public class GraphQLJobExecutionsSortByEndTimeIT {

    @MockBean
    DeploymentService deploymentService;

    @Autowired
    MockMvc mockMvc;

    @Autowired
    JobExecutionRepository jobExecutionRepository;

    @Autowired
    JobsRepository jobsRepository;

    private DataJob jobA;
    private final String uri = "/data-jobs/for-team/supercollider/jobs";


    @BeforeEach
    private void setUpJobsAndDeployments() {
        var depl = new JobDeploymentStatus();
        depl.setDataJobName("jobA");
        depl.setEnabled(true);
        depl.setLastDeployedBy("Me");
        depl.setLastDeployedDate("today");
        depl.setMode("testing");
        depl.setGitCommitSha("1234asdasd");
        depl.setImageName("imngname");
        depl.setCronJobName("jobA-cron");
        Mockito.when(deploymentService.readDeployments()).thenReturn(List.of(depl));
        JobConfig config = new JobConfig();
        config.setSchedule("schedule");
        jobA = new DataJob("jobA", config);
        jobA.setLatestJobDeploymentStatus(DeploymentStatus.SUCCESS);
        jobsRepository.save(jobA);
    }

    @AfterEach
    public void cleanup() {
        jobsRepository.deleteAll();
        jobExecutionRepository.deleteAll();
    }

    private void addJobExecution(OffsetDateTime endTime, String executionId) {
        var execution = createDataJobExecution(jobExecutionRepository, executionId,
                jobA, ExecutionStatus.FINISHED, "message", OffsetDateTime.now());
        execution.setEndTime(endTime);
        jobExecutionRepository.save(execution);
    }

    private String getQuery(String sortOrder) {
        return "{\n" +
                "  jobs(pageNumber: 1, pageSize: 100, filter: [{property: \"jobName\", sort: ASC}]) {\n" +
                "    content {\n" +
                "      jobName\n" +
                "      deployments {\n" +
                "        executions(pageNumber: 1, pageSize: 10, filter: [{property: \"endTime\", sort: " + sortOrder + "}]) {\n" +
                "          id\n" +
                "          endTime\n" +
                "        }\n" +
                "      }\n" +
                "    }\n" +
                "  }\n" +
                "}";
    }

    @Test
    public void testEmptyCallAsc() throws Exception {
        mockMvc.perform(MockMvcRequestBuilders.get(uri)
               .queryParam("query", getQuery("ASC")))
               .andExpect(status().is(200));
    }

    @Test
    public void testEmptyCallDesc() throws Exception {
        mockMvc.perform(MockMvcRequestBuilders.get(uri)
               .queryParam("query", getQuery("DESC")))
               .andExpect(status().is(200));
    }

    @Test
    public void testCallWithSingleExecution() throws Exception {
        var expectedEndTime = OffsetDateTime.now();

        addJobExecution(expectedEndTime, "testId");
        mockMvc.perform(MockMvcRequestBuilders.get(uri)
               .queryParam("query", getQuery("DESC")))
               .andExpect(status().is(200))
               .andExpect(content().contentType("application/json"))
               .andExpect(jsonPath("$.data.content[0].deployments[0].executions").exists())
               .andExpect(jsonPath("$.data.content[0].deployments[0].executions[0].endTime").value(expectedEndTime.toString()));

    }

    @Test
    public void testCallTwoExecutionsSortAsc() throws Exception {
        var expectedEndTimeLarger = OffsetDateTime.now();
        var expectedEndTimeSmaller = OffsetDateTime.now().minusDays(1);

        addJobExecution(expectedEndTimeLarger, "testId");
        addJobExecution(expectedEndTimeSmaller, "testId2");

        mockMvc.perform(MockMvcRequestBuilders.get(uri)
               .queryParam("query", getQuery("ASC")))
               .andExpect(status().is(200))
               .andExpect(content().contentType("application/json"))
               .andExpect(jsonPath("$.data.content[0].deployments[0].executions[0]").exists())
               .andExpect(jsonPath("$.data.content[0].deployments[0].executions[1]").exists())
               .andExpect(jsonPath("$.data.content[0].deployments[0].executions[0].endTime").value(expectedEndTimeSmaller.toString()))
               .andExpect(jsonPath("$.data.content[0].deployments[0].executions[1].endTime").value(expectedEndTimeLarger.toString()));
    }

    @Test
    public void testCallTwoExecutionsSortDesc() throws Exception {
        var expectedEndTimeLarger = OffsetDateTime.now();
        var expectedEndTimeSmaller = OffsetDateTime.now().minusDays(1);

        addJobExecution(expectedEndTimeLarger, "testId");
        addJobExecution(expectedEndTimeSmaller, "testId2");

        mockMvc.perform(MockMvcRequestBuilders.get(uri)
               .queryParam("query", getQuery("DESC")))
               .andExpect(status().is(200))
               .andExpect(content().contentType("application/json"))
               .andExpect(jsonPath("$.data.content[0].deployments[0].executions[0]").exists())
               .andExpect(jsonPath("$.data.content[0].deployments[0].executions[1]").exists())
               .andExpect(jsonPath("$.data.content[0].deployments[0].executions[0].endTime").value(expectedEndTimeLarger.toString()))
               .andExpect(jsonPath("$.data.content[0].deployments[0].executions[1].endTime").value(expectedEndTimeSmaller.toString()));
    }

    @Test
    public void testCallPagination() throws Exception {
        for (int i = 0; i < 15; i++) {
            addJobExecution(OffsetDateTime.now(), UUID.randomUUID().toString());
        }
        // Query pagination is set to 10 items per page.
        mockMvc.perform(MockMvcRequestBuilders.get(uri)
               .queryParam("query", getQuery("DESC")))
               .andExpect(status().is(200))
               .andExpect(content().contentType("application/json"))
               .andExpect(jsonPath("$.data.content[0].deployments[0].executions[0]").exists())
               .andExpect(jsonPath("$.data.content[0].deployments[0].executions[9]").exists())
               .andExpect(jsonPath("$.data.content[0].deployments[0].executions[10]").doesNotExist());

    }

    public static DataJobExecution createDataJobExecution(
            JobExecutionRepository jobExecutionRepository,
            String executionId,
            DataJob dataJob,
            ExecutionStatus executionStatus,
            String message,
            OffsetDateTime startTime) {

        var expectedJobExecution = DataJobExecution.builder()
                .id(executionId)
                .dataJob(dataJob)
                .startTime(startTime)
                .type(ExecutionType.MANUAL)
                .status(executionStatus)
                .resourcesCpuRequest(1F)
                .resourcesCpuLimit(2F)
                .resourcesMemoryRequest(500)
                .resourcesMemoryLimit(1000)
                .message(message)
                .lastDeployedBy("test_user")
                .lastDeployedDate(OffsetDateTime.now())
                .jobVersion("test_version")
                .jobSchedule("*/5 * * * *")
                .opId("test_op_id")
                .vdkVersion("test_vdk_version")
                .build();

        return jobExecutionRepository.save(expectedJobExecution);
    }
}
