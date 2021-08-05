/*
 * Copyright (c) 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service;

import com.google.common.collect.Lists;
import com.vmware.taurus.datajobs.webhook.PostCreateWebHookProvider;
import com.vmware.taurus.datajobs.webhook.PostDeleteWebHookProvider;
import com.vmware.taurus.service.credentials.JobCredentialsService;
import com.vmware.taurus.service.deploy.DeploymentService;
import com.vmware.taurus.service.model.DataJob;
import com.vmware.taurus.service.monitoring.DataJobInfoMonitor;
import com.vmware.taurus.service.webhook.WebHookRequestBody;
import com.vmware.taurus.service.webhook.WebHookRequestBodyProvider;
import com.vmware.taurus.service.webhook.WebHookResult;
import lombok.AllArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;

/**
 * CRUD and other management operations on Versatile Data Kit across all systems which the pipelines interact with:
 * configuration DB, credentials systems, Kubernetes etc
 *
 * <p>
 * Methods throw {@link org.springframework.dao.DataAccessException} in case of issues of writing to the database.
 * Operations are synchronous unless otherwise specified in javadoc.
 */
@Service
@AllArgsConstructor
public class JobsService {

   private static final Logger log = LoggerFactory.getLogger(JobsService.class);

   private final JobsRepository jobsRepository;
   private final DeploymentService deploymentService;
   private final JobCredentialsService credentialsService;
   private final WebHookRequestBodyProvider webHookRequestBodyProvider;
   private final PostCreateWebHookProvider postCreateWebHookProvider;
   private final PostDeleteWebHookProvider postDeleteWebHookProvider;
   private final DataJobInfoMonitor dataJobInfoMonitor;


   public JobOperationResult deleteJob(String name) {
      if (!jobsRepository.existsById(name)) {
         return JobOperationResult.builder()
                 .completed(false)
                 .build();
      }

      WebHookRequestBody requestBody = webHookRequestBodyProvider.constructPostDeleteBody(jobsRepository.findById(name).get());
      Optional<WebHookResult> resultHolder = postDeleteWebHookProvider.invokeWebHook(requestBody);
      if(isInvocationSuccessful(resultHolder)) {
         dataJobInfoMonitor.removeDataJobInfo(() -> {
            credentialsService.deleteJobCredentials(name);
            deploymentService.deleteDeployment(name);
            jobsRepository.deleteById(name);
            return name;
         });

         return JobOperationResult.builder()
                 .completed(true)
                 .build();
      } else {
         log.debug("Post Delete WebHook Provider returns unsuccessful result. Job: {} will not be persisted ...", name);

         //Propagate the webhook status code and message
         return JobOperationResult.builder()
                 .completed(false)
                 .webHookResult(resultHolder.get())
                 .build();
      }
   }

   /**
    * Creates a data job if it doesn't exist
    *
    * @param jobInfo the job details, not null
    * @return JobOperationResult with information whether the job was created and didn't exist before the operation.
    *  In addition it will contain WebHookResult in case the WebHookRequest returns 4xx error.
    */
   public JobOperationResult createJob(DataJob jobInfo) {
      if (jobsRepository.existsById(jobInfo.getName())) {
         return JobOperationResult.builder()
                 .completed(false)
                 .build();
      }

      WebHookRequestBody requestBody = webHookRequestBodyProvider.constructPostCreateBody(jobInfo);
      Optional<WebHookResult> resultHolder = postCreateWebHookProvider.invokeWebHook(requestBody);
      if(isInvocationSuccessful(resultHolder)) {
         // Save the data job and update the job info metrics
         dataJobInfoMonitor.updateDataJobInfo(() -> {
            if (jobInfo.getJobConfig().isGenerateKeytab()) {
               credentialsService.createJobCredentials(jobInfo.getName());
            }
            return jobsRepository.save(jobInfo);
         });

         return JobOperationResult.builder()
                 .completed(true)
                 .build();
      } else {
         log.debug("Post Create WebHook Provider returns unsuccessful result. Job: {} will not be persisted ...",
                 jobInfo.getName());

         //Propagate the webhook status code and message
         return JobOperationResult.builder()
                 .completed(false)
                 .webHookResult(resultHolder.get())
                 .build();
      }
   }

   private boolean isInvocationSuccessful(Optional<WebHookResult> resultHolder) {
      if(resultHolder.isPresent()) {
         return resultHolder.get().isSuccess();
      }
      return true;
   }

   /**
    * Updates a data job if exists
    *
    * <p>
    * Updates are always full so null input fields will overwrite fields in the database.
    *
    * @param jobInfo
    * @return if the job existed
    */
   public boolean updateJob(DataJob jobInfo) {
      return dataJobInfoMonitor.updateDataJobInfo(() ->
              jobsRepository.existsById(jobInfo.getName()) ? jobsRepository.save(jobInfo) : null);
   }

   /**
    * Read a page of jobs
    *
    * @param pageNumber The number of pages of items to skip before starting to collect the result set. Must be >= 0
    * @param pageSize   The number of items in page. Must be > 0.
    * @return a list of jobs, up to pageSize in size
    */
   public List<DataJob> getAllJobs(int pageNumber, int pageSize) {
      // validates parameters
      Pageable pageable = PageRequest.of(pageNumber, pageSize, Sort.by("name"));

      log.info("Reading jobs at {} ...", pageable.getPageNumber(), pageable);
      // Reading jobs populates their jobConfig objects too.
      var dataJobs = Lists.newArrayList(jobsRepository.findAll(pageable));
      log.info("Found {} jobs", dataJobs.size());
      return dataJobs;
   }

   /**
    * Read a page of jobs belonging to a team
    *
    * @param pageNumber The number of pages of items to skip before starting to collect the result set. Must be >= 0
    * @param pageSize   The number of items in page. Must be > 0.
    * @param teamName   The name of the team to which the job belongs
    * @return a list of jobs, up to pageSize in size
    */
   public List<DataJob> getTeamJobs(int pageNumber, int pageSize, String teamName) {
      // validates parameters
      Pageable pageable = PageRequest.of(pageNumber, pageSize, Sort.by("name"));

      log.info("Reading jobs for team {} at {} ...", teamName, pageable.getPageNumber(), pageable);
      // Reading jobs populates their jobConfig objects too.
      var dataJobs = Lists.newArrayList(jobsRepository.findAllByJobConfigTeam(teamName, pageable));
      log.info("Found {} jobs of team {}", dataJobs.size(), teamName);
      return dataJobs;
   }

   public boolean jobWithTeamExists(String jobName, String teamName) {
      return jobsRepository.existsDataJobByNameAndJobConfigTeam(jobName, teamName);
   }

   public Optional<DataJob> getByName(String name) {
      return jobsRepository.findById(name);
   }

   public Optional<DataJob> getByNameAndTeam(String jobName, String teamName) {
      return jobsRepository.findDataJobByNameAndJobConfigTeam(jobName, teamName);
   }
}
