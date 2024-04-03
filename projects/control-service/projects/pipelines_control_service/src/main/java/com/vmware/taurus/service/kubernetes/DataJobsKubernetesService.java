/*
 * Copyright 2023-2024 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.kubernetes;

import com.google.gson.JsonSyntaxException;
import com.vmware.taurus.exception.DataJobExecutionCannotBeCancelledException;
import com.vmware.taurus.exception.ExecutionCancellationFailureReason;
import com.vmware.taurus.exception.KubernetesException;
import com.vmware.taurus.service.KubernetesService;
import com.vmware.taurus.service.deploy.JobCommandProvider;
import com.vmware.taurus.service.model.JobAnnotation;
import io.kubernetes.client.openapi.ApiClient;
import io.kubernetes.client.openapi.ApiException;
import io.kubernetes.client.openapi.apis.BatchV1Api;
import io.kubernetes.client.openapi.models.V1Container;
import io.kubernetes.client.openapi.models.V1Volume;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.codec.digest.DigestUtils;
import org.apache.commons.collections4.MapUtils;
import org.apache.commons.lang3.SerializationUtils;
import org.springframework.beans.factory.annotation.Qualifier;

import java.util.*;
import java.util.stream.Collectors;
import java.util.stream.Stream;

/**
 * Kubernetes service used for serving data jobs deployments. All deployed data jobs are executed in
 * this environment and all other necessary resources that are used only during the execution of a
 * data job should be create in this kubernetes.
 */
// @Service
@Slf4j
public class DataJobsKubernetesService extends KubernetesService {

  public DataJobsKubernetesService(
      @Qualifier("dataJobsNamespace") String namespace,
      @Qualifier("deploymentApiClient") ApiClient client,
      @Qualifier("deploymentBatchV1Api") BatchV1Api batchV1Api,
      JobCommandProvider jobCommandProvider) {
    super(namespace, log, client, batchV1Api, jobCommandProvider);
  }

  public void createCronJob(KubernetesService.CronJob cronJob) throws ApiException {
    createCronJob(
        cronJob.getName(),
        cronJob.getImage(),
        cronJob.getSchedule(),
        cronJob.isEnable(),
        cronJob.getJobContainer(),
        cronJob.getInitContainer(),
        cronJob.getVolumes(),
        cronJob.getJobAnnotations(),
        cronJob.getJobLabels(),
        cronJob.getImagePullSecret());
  }

  public void createCronJob(
      String name,
      String image,
      String schedule,
      boolean enable,
      V1Container jobContainer,
      V1Container initContainer,
      List<V1Volume> volumes,
      Map<String, String> jobAnnotations,
      Map<String, String> jobLabels,
      List<String> imagePullSecrets)
      throws ApiException {
    createV1CronJob(
        name,
        image,
        schedule,
        enable,
        jobContainer,
        initContainer,
        volumes,
        jobAnnotations,
        jobLabels,
        imagePullSecrets);
  }

  public String getCronJobSha512(
      KubernetesService.CronJob cronJob, JobAnnotation excludeAnnotation) {
    String cronJobString = null;
    Map<String, String> jobAnnotations = cronJob.getJobAnnotations();

    if (MapUtils.isNotEmpty(jobAnnotations) && excludeAnnotation != null) {
      jobAnnotations = SerializationUtils.clone((HashMap) cronJob.getJobAnnotations());
      jobAnnotations.remove(excludeAnnotation.getValue());
    }

    cronJobString =
        v1CronJobFromTemplate(
                cronJob.getName(),
                cronJob.getSchedule(),
                !cronJob.isEnable(),
                cronJob.getJobContainer(),
                cronJob.getInitContainer(),
                cronJob.getVolumes(),
                jobAnnotations,
                cronJob.getJobLabels(),
                cronJob.getImagePullSecret())
            .toString();
    return DigestUtils.sha1Hex(cronJobString);
  }

  public void updateCronJob(KubernetesService.CronJob cronJob) throws ApiException {
    updateCronJob(
        cronJob.getName(),
        cronJob.getImage(),
        cronJob.getSchedule(),
        cronJob.isEnable(),
        cronJob.getJobContainer(),
        cronJob.getInitContainer(),
        cronJob.getVolumes(),
        cronJob.getJobAnnotations(),
        cronJob.getJobLabels(),
        cronJob.getImagePullSecret());
  }

  public void updateCronJob(
      String name,
      String image,
      String schedule,
      boolean enable,
      V1Container jobContainer,
      V1Container initContainer,
      List<V1Volume> volumes,
      Map<String, String> jobAnnotations,
      Map<String, String> jobLabels,
      List<String> imagePullSecrets)
      throws ApiException {
    updateV1CronJob(
        name,
        image,
        schedule,
        enable,
        jobContainer,
        initContainer,
        volumes,
        jobAnnotations,
        jobLabels,
        imagePullSecrets);
  }

  /**
   * Returns a set of cron job names for a given namespace in a Kubernetes cluster. The cron jobs
   * can be of version V1 or V1Beta.
   *
   * @return a set of cron job names
   * @throws ApiException if there is a problem accessing the Kubernetes API
   */
  public Set<String> listCronJobs() throws ApiException {
    log.debug("Listing k8s cron jobs");
    Set<String> v1CronJobNames = Collections.emptySet();

    try {
      var v1CronJobs = batchV1Api.listNamespacedCronJob(namespace).execute();
      v1CronJobNames =
          v1CronJobs.getItems().stream()
              .map(j -> j.getMetadata().getName())
              .collect(Collectors.toSet());
      log.trace("K8s V1 cron jobs: {}", v1CronJobNames);
    } catch (ApiException e) {
      if (e.getCode()
          == 404) { // as soon as the minimum supported k8s version is >=1.21 then we should remove
        // this.
        log.trace("Unable to query for v1 batch jobs", e);
      } else {
        throw e;
      }
    }

    var cronJobs = batchV1Api.listNamespacedCronJob(namespace).execute();
    var cronJobNames =
        cronJobs.getItems().stream()
            .map(j -> j.getMetadata().getName())
            .collect(Collectors.toSet());
    log.trace("K8s cron jobs: {}", cronJobNames);
    return Stream.concat(v1CronJobNames.stream(), cronJobNames.stream())
        .collect(Collectors.toSet());
  }

  public void deleteCronJob(String name) throws ApiException {
    log.debug("Deleting k8s cron job: {}", name);
    batchV1Api.deleteNamespacedCronJob(name, namespace).execute();
    log.debug("Deleted k8s cron job: {}", name);
  }

  public void cancelRunningCronJob(String teamName, String jobName, String executionId)
      throws ApiException {
    log.info(
        "K8S deleting job for team: {} data job name: {} execution: {} namespace: {}",
        teamName,
        jobName,
        executionId,
        namespace);
    try {
      var operationResponse =
          batchV1Api.deleteNamespacedJob(executionId, namespace).executeWithHttpInfo();
      // Status of the operation. One of: "Success" or "Failure"
      if (operationResponse == null || operationResponse.getStatusCode() == 404) {
        log.info(
            "Execution: {} for data job: {} with team: {} not found! The data job has likely"
                + " completed before it could be cancelled.",
            executionId,
            jobName,
            teamName);
        throw new DataJobExecutionCannotBeCancelledException(
            executionId, ExecutionCancellationFailureReason.DataJobExecutionNotFound);
      } else if (operationResponse.getStatusCode() != 200) {
        log.warn(
            "Failed to delete K8S job. Reason: {} Details: {}",
            operationResponse.getData().getReason(),
            operationResponse.getData().getDetails());
        throw new KubernetesException(
            operationResponse.getData().getMessage(),
            new ApiException(
                operationResponse.getStatusCode(), operationResponse.getData().getMessage()));
      }
    } catch (JsonSyntaxException e) {
      if (e.getCause() instanceof IllegalStateException) {
        IllegalStateException ise = (IllegalStateException) e.getCause();
        if (ise.getMessage() != null
            && ise.getMessage().contains("Expected a string but was BEGIN_OBJECT"))
          log.debug(
              "Catching exception because of issue"
                  + " https://github.com/kubernetes-client/java/issues/86",
              e);
        else throw e;
      } else throw e;

    } catch (ApiException e) {
      // If no response body is present this might be a transport layer failure.
      if (e.getCode() == 404) {
        log.debug(
            "Job execution: {} team: {}, job: {} cannot be found. K8S response body {}. Will set"
                + " its status to Cancelled in the DB.",
            executionId,
            teamName,
            jobName,
            e.getResponseBody());
      } else throw e;
    }
  }
}
