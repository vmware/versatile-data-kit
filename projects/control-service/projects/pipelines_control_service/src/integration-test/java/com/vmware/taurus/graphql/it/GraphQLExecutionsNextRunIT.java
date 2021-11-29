/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.graphql.it;


import com.vmware.taurus.ServiceApp;
import com.vmware.taurus.service.JobsRepository;
import com.vmware.taurus.service.model.DataJob;
import com.vmware.taurus.service.model.DeploymentStatus;
import com.vmware.taurus.service.model.JobConfig;
import org.hamcrest.Matchers;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.request.MockMvcRequestBuilders;

import java.time.OffsetDateTime;
import java.time.ZoneId;

import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;

@SpringBootTest(classes = ServiceApp.class)
@AutoConfigureMockMvc
public class GraphQLExecutionsNextRunIT {

   @Autowired
   MockMvc mockMvc;

   @Autowired
   JobsRepository jobsRepository;

   private final String uri = "/data-jobs/for-team/supercollider/jobs";

   @AfterEach
   public void cleanup() {
      jobsRepository.deleteAll();
   }

   private String getQuery(String sortOrder) {
      return "{\n" +
            "  jobs(pageNumber: 1, pageSize: 100, filter: [{property: \"config.schedule.nextRunEpochSeconds\", sort:" + sortOrder + "}]) {\n" +
            "    content {\n" +
            "      jobName \n" +
            "      config {\n" +
            "        schedule {\n" +
            "          scheduleCron\n" +
            "          nextRunEpochSeconds\n" +
            "        }" +
            "      }" +
            "    }\n" +
            "  }\n" +
            "}";
   }

   private String getQueryWithFilter(String filter) {
      return "{\n" +
            "  jobs(pageNumber: 1, pageSize: 100, filter: [{property: \"config.schedule.nextRunEpochSeconds\", pattern:" + filter + "}]) {\n" +
            "    content {\n" +
            "      jobName \n" +
            "      config {\n" +
            "        schedule {\n" +
            "          scheduleCron\n" +
            "          nextRunEpochSeconds\n" +
            "        }" +
            "      }" +
            "    }\n" +
            "  }\n" +
            "}";
   }

   @Test
   public void testNextRunCall_noJobs() throws Exception {
      mockMvc.perform(MockMvcRequestBuilders.get(uri).queryParam("query", getQuery("DESC")))
            .andExpect(jsonPath("$.data.content").isEmpty());
   }

   @Test
   public void testNextRunCall_oneJob() throws Exception {
      var now = OffsetDateTime.now();
      addJob("jobA", toCron(now));

      mockMvc.perform(MockMvcRequestBuilders.get(uri).queryParam("query", getQuery("DESC")))
            .andExpect(jsonPath("$.data.content[0].jobName").value("jobA"))
            .andExpect(jsonPath("$.data.content[0].config.schedule.scheduleCron").value(toCron(now)));
   }

   @Test
   public void testNextRunCall_twoJobs_DESC() throws Exception {
      var now = OffsetDateTime.now(ZoneId.of("UTC")).plusMinutes(2);
      var later = now.plusDays(1);

      addJob("jobA", toCron(now));
      addJob("jobB", toCron(later));
      //check correct sort is applied
      mockMvc.perform(MockMvcRequestBuilders.get(uri).queryParam("query", getQuery("DESC")))
            .andExpect(jsonPath("$.data.content[0].jobName").value("jobB"))
            .andExpect(jsonPath("$.data.content[1].jobName").value("jobA"))
            .andExpect(jsonPath("$.data.content[0].config.schedule.scheduleCron").value(toCron(later)))
            .andExpect(jsonPath("$.data.content[1].config.schedule.scheduleCron").value(toCron(now)));
   }

   @Test
   public void testNextRunCall_twoJobs_ASC() throws Exception {
      var now = OffsetDateTime.now(ZoneId.of("UTC")).plusMinutes(2);
      var later = now.plusMinutes(60);

      addJob("jobA", toCron(now));
      addJob("jobB", toCron(later));
      //check correct sort is applied
      mockMvc.perform(MockMvcRequestBuilders.get(uri).queryParam("query", getQuery("ASC")))
            .andExpect(jsonPath("$.data.content[0].jobName").value("jobA"))
            .andExpect(jsonPath("$.data.content[1].jobName").value("jobB"))
            .andExpect(jsonPath("$.data.content[0].config.schedule.scheduleCron").value(toCron(now)))
            .andExpect(jsonPath("$.data.content[1].config.schedule.scheduleCron").value(toCron(later)));
   }

   @Test
   public void testNextRunCall_filter_noJobs() throws Exception {
      var now = OffsetDateTime.now();
      var before = now.minusDays(2);

      mockMvc.perform(MockMvcRequestBuilders.get(uri).queryParam("query", getQueryWithFilter(getFilterPattern(before, now))))
            .andExpect(jsonPath("$.data.content").isEmpty());

   }

   @Test
   public void testNextRunCall_filter_twoJobs() throws Exception {
      var now = OffsetDateTime.now(ZoneId.of("UTC"));
      var after = now.plusMinutes(120);

      addJob("jobA", toCron(now.minusMinutes(240)));
      addJob("jobB", toCron(now.plusMinutes(30)));

     mockMvc.perform(MockMvcRequestBuilders.get(uri).queryParam("query", getQueryWithFilter(getFilterPattern(now, after))))
           .andExpect(jsonPath("$.data.content[0].jobName").value("jobB"))
           .andExpect(jsonPath("$.data.content[*].jobName", Matchers.not(Matchers.contains("jobA"))));
   }

   private void addJob(String jobName, String jobSchedule) {
      JobConfig config = new JobConfig();
      config.setSchedule(jobSchedule);
      var job = new DataJob(jobName, config);
      job.setLatestJobDeploymentStatus(DeploymentStatus.SUCCESS);
      jobsRepository.save(job);
   }

   private String toCron(OffsetDateTime dateTime) {
      return String.format("%d %d %d %d %d", dateTime.getMinute(), dateTime.getHour(), dateTime.getDayOfMonth(),
            dateTime.getMonth().getValue(), dateTime.getDayOfWeek().getValue());
   }

   private String getFilterPattern(OffsetDateTime start, OffsetDateTime finish) {
      return String.format("\"%d-%d\"", start.toEpochSecond(), finish.toEpochSecond());
   }

}
