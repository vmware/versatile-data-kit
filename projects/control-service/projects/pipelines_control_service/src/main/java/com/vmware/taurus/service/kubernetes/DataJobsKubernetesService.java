/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.kubernetes;

import com.google.common.annotations.VisibleForTesting;
import com.vmware.taurus.exception.KubernetesException;
import com.vmware.taurus.service.KubernetesService;
import com.vmware.taurus.service.deploy.DockerImageName;
import com.vmware.taurus.service.model.JobAnnotation;
import com.vmware.taurus.service.model.JobDeploymentStatus;
import com.vmware.taurus.service.model.JobLabel;
import io.kubernetes.client.openapi.ApiException;
import io.kubernetes.client.openapi.apis.BatchV1Api;
import io.kubernetes.client.openapi.apis.BatchV1beta1Api;
import io.kubernetes.client.openapi.models.*;
import io.kubernetes.client.util.Yaml;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.ClassPathResource;
import org.springframework.stereotype.Service;
import org.springframework.util.CollectionUtils;

import java.io.File;
import java.nio.file.Files;
import java.util.*;
import java.util.stream.Collectors;
import java.util.stream.Stream;

/**
 * Kubernetes service used for serving data jobs deployments. All deployed data jobs are executed in
 * this environment and all other necessary resources that are used only during the execution of a
 * data job should be create in this kubernetes.
 */
@Service
@Slf4j
public class DataJobsKubernetesService extends KubernetesService {

  // The 'Value' annotation from Lombok collides with the 'Value' annotation from Spring.
  @org.springframework.beans.factory.annotation.Value(
      "${datajobs.control.k8s.data.job.template.file}")
  private String datajobTemplateFileLocation;

  private static final String K8S_DATA_JOB_TEMPLATE_RESOURCE = "k8s-data-job-template.yaml";
  private static final String V1_K8S_DATA_JOB_TEMPLATE_RESOURCE = "v1-k8s-data-job-template.yaml";

  public DataJobsKubernetesService(
      @Value("${datajobs.deployment.k8s.namespace:}") String namespace,
      @Value("${datajobs.deployment.k8s.kubeconfig:}") String kubeconfig,
      @Value("${datajobs.control.k8s.k8sSupportsV1CronJob}") boolean k8sSupportsV1CronJob) {
    super(namespace, kubeconfig, k8sSupportsV1CronJob, log);
    if (StringUtils.isBlank(kubeconfig) && !new File(kubeconfig).isFile()) {
      log.warn(
          "Data Jobs (Deployment) Kubernetes service may not have been correctly bootstrapped. {}"
              + " file is missing Will try to use same cluster as control Plane. But this is not"
              + " recommended in production.",
          kubeconfig);
    }
  }

  @Override
  public void afterPropertiesSet() throws Exception {
    super.afterPropertiesSet();

    // Step 1 - load the internal datajob template in order to validate it.
    try {
      if (getK8sSupportsV1CronJob()) {
        loadV1CronjobTemplate(new ClassPathResource(V1_K8S_DATA_JOB_TEMPLATE_RESOURCE).getFile());
      } else {
        loadV1beta1CronjobTemplate(new ClassPathResource(K8S_DATA_JOB_TEMPLATE_RESOURCE).getFile());
      }
      log.info("The internal datajob template is valid.");
    } catch (Exception e) {
      // Log the error and fail fast (cannot continue).
      log.error("Fatal error while loading the internal datajob template. Cannot continue", e);
      throw e;
    }
    // Step 2 - load the configurable datajob template in order to validate it
    // when environment variable 'K8S_DATA_JOB_TEMPLATE_FILE' is set.
    if (!StringUtils.isEmpty(datajobTemplateFileLocation)) {
      if (getK8sSupportsV1CronJob()) {
        if (loadConfigurableV1CronjobTemplate() == null) {
          log.warn(
              "The configurable datajob template '{}' could not be loaded.",
              datajobTemplateFileLocation);
        } else {
          log.info("The configurable datajob template '{}' is valid.", datajobTemplateFileLocation);
        }
      } else {
        if (loadConfigurableV1beta1CronjobTemplate() == null) {
          log.warn(
              "The configurable datajob template '{}' could not be loaded.",
              datajobTemplateFileLocation);
        } else {
          log.info("The configurable datajob template '{}' is valid.", datajobTemplateFileLocation);
        }
      }
    }
  }

  // TODO - in the future we want to merge the (1) configurable datajob template
  //        with the (2) default internal datajob template when something from (1)
  //        is missing. For now we just check for missing entries in (1) and overwrite
  //        them with the corresponding entries in (2).
  private void v1beta1checkForMissingEntries(V1beta1CronJob cronjob) {
    V1beta1CronJob internalCronjobTemplate = loadInternalV1beta1CronjobTemplate();
    if (cronjob.getMetadata() == null) {
      cronjob.setMetadata(internalCronjobTemplate.getMetadata());
    }
    V1ObjectMeta metadata = cronjob.getMetadata();
    if (metadata.getAnnotations() == null) {
      metadata.setAnnotations(new HashMap<>());
    }
    if (cronjob.getSpec() == null) {
      cronjob.setSpec(internalCronjobTemplate.getSpec());
    }
    V1beta1CronJobSpec spec = cronjob.getSpec();
    if (spec.getJobTemplate() == null) {
      spec.setJobTemplate(internalCronjobTemplate.getSpec().getJobTemplate());
    }
    if (spec.getJobTemplate().getMetadata() == null) {
      spec.getJobTemplate()
          .setMetadata(internalCronjobTemplate.getSpec().getJobTemplate().getMetadata());
    }
    if (spec.getJobTemplate().getMetadata().getLabels() == null) {
      spec.getJobTemplate().getMetadata().setLabels(new HashMap<>());
    }
    if (spec.getJobTemplate().getMetadata().getAnnotations() == null) {
      spec.getJobTemplate().getMetadata().setAnnotations(new HashMap<>());
    }
    if (spec.getJobTemplate().getSpec() == null) {
      spec.getJobTemplate().setSpec(internalCronjobTemplate.getSpec().getJobTemplate().getSpec());
    }
    if (spec.getJobTemplate().getSpec().getTemplate() == null) {
      spec.getJobTemplate()
          .getSpec()
          .setTemplate(internalCronjobTemplate.getSpec().getJobTemplate().getSpec().getTemplate());
    }
    if (spec.getJobTemplate().getSpec().getTemplate().getSpec() == null) {
      spec.getJobTemplate()
          .getSpec()
          .getTemplate()
          .setSpec(
              internalCronjobTemplate.getSpec().getJobTemplate().getSpec().getTemplate().getSpec());
    }
    if (spec.getJobTemplate().getSpec().getTemplate().getMetadata() == null) {
      spec.getJobTemplate()
          .getSpec()
          .getTemplate()
          .setMetadata(
              internalCronjobTemplate
                  .getSpec()
                  .getJobTemplate()
                  .getSpec()
                  .getTemplate()
                  .getMetadata());
    }
    if (spec.getJobTemplate().getSpec().getTemplate().getMetadata().getLabels() == null) {
      spec.getJobTemplate().getSpec().getTemplate().getMetadata().setLabels(new HashMap<>());
    }
  }

  private void v1checkForMissingEntries(V1CronJob cronjob) {
    V1CronJob internalCronjobTemplate = loadInternalV1CronjobTemplate();
    if (cronjob.getMetadata() == null) {
      cronjob.setMetadata(internalCronjobTemplate.getMetadata());
    }
    V1ObjectMeta metadata = cronjob.getMetadata();
    if (metadata.getAnnotations() == null) {
      metadata.setAnnotations(new HashMap<>());
    }
    if (cronjob.getSpec() == null) {
      cronjob.setSpec(internalCronjobTemplate.getSpec());
    }
    V1CronJobSpec spec = cronjob.getSpec();
    if (spec.getJobTemplate() == null) {
      spec.setJobTemplate(internalCronjobTemplate.getSpec().getJobTemplate());
    }
    if (spec.getJobTemplate().getMetadata() == null) {
      spec.getJobTemplate()
          .setMetadata(internalCronjobTemplate.getSpec().getJobTemplate().getMetadata());
    }
    if (spec.getJobTemplate().getMetadata().getLabels() == null) {
      spec.getJobTemplate().getMetadata().setLabels(new HashMap<>());
    }
    if (spec.getJobTemplate().getMetadata().getAnnotations() == null) {
      spec.getJobTemplate().getMetadata().setAnnotations(new HashMap<>());
    }
    if (spec.getJobTemplate().getSpec() == null) {
      spec.getJobTemplate().setSpec(internalCronjobTemplate.getSpec().getJobTemplate().getSpec());
    }
    if (spec.getJobTemplate().getSpec().getTemplate() == null) {
      spec.getJobTemplate()
          .getSpec()
          .setTemplate(internalCronjobTemplate.getSpec().getJobTemplate().getSpec().getTemplate());
    }
    if (spec.getJobTemplate().getSpec().getTemplate().getSpec() == null) {
      spec.getJobTemplate()
          .getSpec()
          .getTemplate()
          .setSpec(
              internalCronjobTemplate.getSpec().getJobTemplate().getSpec().getTemplate().getSpec());
    }
    if (spec.getJobTemplate().getSpec().getTemplate().getMetadata() == null) {
      spec.getJobTemplate()
          .getSpec()
          .getTemplate()
          .setMetadata(
              internalCronjobTemplate
                  .getSpec()
                  .getJobTemplate()
                  .getSpec()
                  .getTemplate()
                  .getMetadata());
    }
    if (spec.getJobTemplate().getSpec().getTemplate().getMetadata().getLabels() == null) {
      spec.getJobTemplate().getSpec().getTemplate().getMetadata().setLabels(new HashMap<>());
    }
  }

  private V1CronJob loadV1CronjobTemplate() {
    if (StringUtils.isEmpty(datajobTemplateFileLocation)) {
      log.debug("Datajob template file location is not set. Using internal datajob template.");
      return loadInternalV1CronjobTemplate();
    }
    V1CronJob cronjobTemplate = loadConfigurableV1CronjobTemplate();
    if (cronjobTemplate == null) {
      return loadInternalV1CronjobTemplate();
    }

    return cronjobTemplate;
  }

  private V1beta1CronJob loadInternalV1beta1CronjobTemplate() {
    try {
      return loadV1beta1CronjobTemplate(
          new ClassPathResource(K8S_DATA_JOB_TEMPLATE_RESOURCE).getFile());
    } catch (Exception e) {
      // This should never happen unless we are testing locally and we've messed up
      // with the internal template resource file.
      throw new RuntimeException(
          "Unrecoverable error while loading the internal datajob template. Cannot continue.", e);
    }
  }

  private V1CronJob loadInternalV1CronjobTemplate() {
    try {
      return loadV1CronjobTemplate(
          new ClassPathResource(V1_K8S_DATA_JOB_TEMPLATE_RESOURCE).getFile());
    } catch (Exception e) {
      // This should never happen unless we are testing locally and we've messed up
      // with the internal template resource file.
      throw new RuntimeException(
          "Unrecoverable error while loading the internal datajob template. Cannot continue.", e);
    }
  }

  private V1beta1CronJob loadConfigurableV1beta1CronjobTemplate() {
    // Check whether to use configurable datajob template at all.
    if (StringUtils.isEmpty(datajobTemplateFileLocation)) {
      log.debug("Datajob template file location is not set.");
      return null;
    }

    // Check whether the configurable datajob template file exists.
    File datajobTemplateFile = new File(datajobTemplateFileLocation);
    if (!datajobTemplateFile.isFile()) {
      log.warn("Datajob template location '{}' is not a file.", datajobTemplateFileLocation);
      return null;
    }

    try {
      // Load the configurable datajob template file.
      return loadV1beta1CronjobTemplate(datajobTemplateFile);
    } catch (Exception e) {
      log.error("Error while loading the datajob template file.", e);
      return null;
    }
  }

  private V1CronJob loadConfigurableV1CronjobTemplate() {
    // Check whether to use configurable datajob template at all.
    if (StringUtils.isEmpty(datajobTemplateFileLocation)) {
      log.debug("Datajob template file location is not set.");
      return null;
    }

    // Check whether the configurable datajob template file exists.
    File datajobTemplateFile = new File(datajobTemplateFileLocation);
    if (!datajobTemplateFile.isFile()) {
      log.warn("Datajob template location '{}' is not a file.", datajobTemplateFileLocation);
      return null;
    }

    try {
      // Load the configurable datajob template file.
      return loadV1CronjobTemplate(datajobTemplateFile);
    } catch (Exception e) {
      log.error("Error while loading the datajob template file.", e);
      return null;
    }
  }

  private V1beta1CronJob loadV1beta1CronjobTemplate(File datajobTemplateFile) throws Exception {
    String cronjobTemplateString = Files.readString(datajobTemplateFile.toPath());
    // Check whether the string template is a valid datajob template.
    V1beta1CronJob cronjobTemplate = Yaml.loadAs(cronjobTemplateString, V1beta1CronJob.class);
    log.debug(
        "Datajob template for file '{}': \n{}",
        datajobTemplateFile.getCanonicalPath(),
        cronjobTemplate);

    return cronjobTemplate;
  }

  private V1CronJob loadV1CronjobTemplate(File datajobTemplateFile) throws Exception {
    String cronjobTemplateString = Files.readString(datajobTemplateFile.toPath());
    // Check whether the string template is a valid datajob template.
    V1CronJob cronjobTemplate = Yaml.loadAs(cronjobTemplateString, V1CronJob.class);
    log.debug(
        "Datajob template for file '{}': \n{}",
        datajobTemplateFile.getCanonicalPath(),
        cronjobTemplate);

    return cronjobTemplate;
  }

  private V1beta1CronJob loadV1beta1CronjobTemplate() {
    if (StringUtils.isEmpty(datajobTemplateFileLocation)) {
      log.debug("Datajob template file location is not set. Using internal datajob template.");
      return loadInternalV1beta1CronjobTemplate();
    }
    V1beta1CronJob cronjobTemplate = loadConfigurableV1beta1CronjobTemplate();
    if (cronjobTemplate == null) {
      return loadInternalV1beta1CronjobTemplate();
    }

    return cronjobTemplate;
  }

  @VisibleForTesting
  public V1beta1CronJob v1beta1CronJobFromTemplate(
      String name,
      String schedule,
      boolean suspend,
      V1Container jobContainer,
      V1Container initContainer,
      List<V1Volume> volumes,
      Map<String, String> jobDeploymentAnnotations,
      Map<String, String> jobAnnotations,
      Map<String, String> jobLabels,
      List<String> imagePullSecrets) {
    V1beta1CronJob cronjob = loadV1beta1CronjobTemplate();
    v1beta1checkForMissingEntries(cronjob);
    cronjob.getMetadata().setName(name);
    cronjob.getSpec().setSchedule(schedule);
    cronjob.getSpec().setSuspend(suspend);
    cronjob
        .getSpec()
        .getJobTemplate()
        .getSpec()
        .getTemplate()
        .getSpec()
        .setContainers(Collections.singletonList(jobContainer));
    cronjob
        .getSpec()
        .getJobTemplate()
        .getSpec()
        .getTemplate()
        .getSpec()
        .setInitContainers(Collections.singletonList(initContainer));
    cronjob.getSpec().getJobTemplate().getSpec().getTemplate().getSpec().setVolumes(volumes);
    // Merge the annotations and the labels.
    cronjob.getMetadata().getAnnotations().putAll(jobDeploymentAnnotations);

    cronjob.getSpec().getJobTemplate().getMetadata().getAnnotations().putAll(jobAnnotations);
    cronjob.getSpec().getJobTemplate().getMetadata().getLabels().putAll(jobLabels);

    List<V1LocalObjectReference> imagePullSecretsObj =
        Optional.ofNullable(imagePullSecrets).stream()
            .flatMap(secrets -> secrets.stream())
            .filter(secret -> StringUtils.isNotEmpty(secret))
            .map(secret -> new V1LocalObjectReferenceBuilder().withName(secret).build())
            .collect(Collectors.toList());

    if (!CollectionUtils.isEmpty(imagePullSecretsObj)) {
      cronjob
          .getSpec()
          .getJobTemplate()
          .getSpec()
          .getTemplate()
          .getSpec()
          .setImagePullSecrets(imagePullSecretsObj);
    }

    return cronjob;
  }

  @VisibleForTesting
  public V1CronJob v1CronJobFromTemplate(
      String name,
      String schedule,
      boolean suspend,
      V1Container jobContainer,
      V1Container initContainer,
      List<V1Volume> volumes,
      Map<String, String> jobDeploymentAnnotations,
      Map<String, String> jobAnnotations,
      Map<String, String> jobLabels,
      List<String> imagePullSecrets) {
    V1CronJob cronjob = loadV1CronjobTemplate();
    v1checkForMissingEntries(cronjob);
    cronjob.getMetadata().setName(name);
    cronjob.getSpec().setSchedule(schedule);
    cronjob.getSpec().setSuspend(suspend);
    cronjob
        .getSpec()
        .getJobTemplate()
        .getSpec()
        .getTemplate()
        .getSpec()
        .setContainers(Collections.singletonList(jobContainer));
    cronjob
        .getSpec()
        .getJobTemplate()
        .getSpec()
        .getTemplate()
        .getSpec()
        .setInitContainers(Collections.singletonList(initContainer));
    cronjob.getSpec().getJobTemplate().getSpec().getTemplate().getSpec().setVolumes(volumes);
    // Merge the annotations and the labels.
    cronjob.getMetadata().getAnnotations().putAll(jobDeploymentAnnotations);

    cronjob.getSpec().getJobTemplate().getMetadata().getAnnotations().putAll(jobAnnotations);
    cronjob.getSpec().getJobTemplate().getMetadata().getLabels().putAll(jobLabels);

    List<V1LocalObjectReference> imagePullSecretsObj =
        Optional.ofNullable(imagePullSecrets).stream()
            .flatMap(secrets -> secrets.stream())
            .filter(secret -> StringUtils.isNotEmpty(secret))
            .map(secret -> new V1LocalObjectReferenceBuilder().withName(secret).build())
            .collect(Collectors.toList());

    if (!CollectionUtils.isEmpty(imagePullSecretsObj)) {
      cronjob
          .getSpec()
          .getJobTemplate()
          .getSpec()
          .getTemplate()
          .getSpec()
          .setImagePullSecrets(imagePullSecretsObj);
    }

    return cronjob;
  }

  public void createCronJob(
      String name,
      String image,
      String schedule,
      boolean enable,
      V1Container jobContainer,
      V1Container initContainer,
      List<V1Volume> volumes,
      Map<String, String> jobDeploymentAnnotations)
      throws ApiException {
    if (getK8sSupportsV1CronJob()) {
      createV1CronJob(
          name,
          image,
          schedule,
          enable,
          jobContainer,
          initContainer,
          volumes,
          jobDeploymentAnnotations,
          Collections.emptyMap(),
          Collections.emptyMap(),
          List.of(""));
    } else {
      createV1beta1CronJob(
          name,
          image,
          schedule,
          enable,
          jobContainer,
          initContainer,
          volumes,
          jobDeploymentAnnotations,
          Collections.emptyMap(),
          Collections.emptyMap(),
          List.of(""));
    }
  }

  public void createCronJob(
      String name,
      String image,
      String schedule,
      boolean enable,
      V1Container jobContainer,
      V1Container initContainer,
      List<V1Volume> volumes,
      Map<String, String> jobDeploymentAnnotations,
      Map<String, String> jobAnnotations,
      Map<String, String> jobLabels,
      List<String> imagePullSecrets)
      throws ApiException {
    if (getK8sSupportsV1CronJob()) {
      createV1CronJob(
          name,
          image,
          schedule,
          enable,
          jobContainer,
          initContainer,
          volumes,
          jobDeploymentAnnotations,
          jobAnnotations,
          jobLabels,
          imagePullSecrets);
    } else {
      createV1beta1CronJob(
          name,
          image,
          schedule,
          enable,
          jobContainer,
          initContainer,
          volumes,
          jobDeploymentAnnotations,
          jobAnnotations,
          jobLabels,
          imagePullSecrets);
    }
  }

  // TODO:  container/volume args are breaking a bit abstraction of KubernetesService by leaking
  // impl. details
  public void createV1beta1CronJob(
      String name,
      String image,
      String schedule,
      boolean enable,
      V1Container jobContainer,
      V1Container initContainer,
      List<V1Volume> volumes,
      Map<String, String> jobDeploymentAnnotations,
      Map<String, String> jobAnnotations,
      Map<String, String> jobLabels,
      List<String> imagePullSecrets)
      throws ApiException {
    log.debug("Creating k8s V1beta1 cron job name:{}, image:{}", name, image);
    var cronJob =
        v1beta1CronJobFromTemplate(
            name,
            schedule,
            !enable,
            jobContainer,
            initContainer,
            volumes,
            jobDeploymentAnnotations,
            jobAnnotations,
            jobLabels,
            imagePullSecrets);
    V1beta1CronJob nsJob =
        new BatchV1beta1Api(getClient())
            .createNamespacedCronJob(namespace, cronJob, null, null, null, null);
    log.debug("Created k8s V1beta1 cron job: {}", nsJob);
    log.debug(
        "Created k8s cron job name: {}, api_version:{}, uid:{}, link:{}",
        nsJob.getMetadata().getName(),
        nsJob.getApiVersion(),
        nsJob.getMetadata().getUid(),
        nsJob.getMetadata().getSelfLink());
  }

  // TODO:  container/volume args are breaking a bit abstraction of KubernetesService by leaking
  // impl. details
  public void createV1CronJob(
      String name,
      String image,
      String schedule,
      boolean enable,
      V1Container jobContainer,
      V1Container initContainer,
      List<V1Volume> volumes,
      Map<String, String> jobDeploymentAnnotations,
      Map<String, String> jobAnnotations,
      Map<String, String> jobLabels,
      List<String> imagePullSecrets)
      throws ApiException {
    log.debug("Creating k8s V1 cron job name:{}, image:{}", name, image);
    var cronJob =
        v1CronJobFromTemplate(
            name,
            schedule,
            !enable,
            jobContainer,
            initContainer,
            volumes,
            jobDeploymentAnnotations,
            jobAnnotations,
            jobLabels,
            imagePullSecrets);
    V1CronJob nsJob =
        new BatchV1Api(getClient())
            .createNamespacedCronJob(namespace, cronJob, null, null, null, null);
    log.debug("Created k8s V1 cron job: {}", nsJob);
    log.debug(
        "Created k8s cron job name: {}, api_version: {}, uid:{}, link:{}",
        nsJob.getMetadata().getName(),
        nsJob.getApiVersion(),
        nsJob.getMetadata().getUid(),
        nsJob.getMetadata().getSelfLink());
  }

  public void updateCronJob(
      String name,
      String image,
      String schedule,
      boolean enable,
      V1Container jobContainer,
      V1Container initContainer,
      List<V1Volume> volumes,
      Map<String, String> jobDeploymentAnnotations)
      throws ApiException {
    if (getK8sSupportsV1CronJob()) {
      updateV1CronJob(
          name,
          image,
          schedule,
          enable,
          jobContainer,
          initContainer,
          volumes,
          jobDeploymentAnnotations,
          Collections.emptyMap(),
          Collections.emptyMap(),
          List.of(""));
    } else {
      updateV1beta1CronJob(
          name,
          image,
          schedule,
          enable,
          jobContainer,
          initContainer,
          volumes,
          jobDeploymentAnnotations,
          Collections.emptyMap(),
          Collections.emptyMap(),
          List.of(""));
    }
  }

  public void updateCronJob(
      String name,
      String image,
      String schedule,
      boolean enable,
      V1Container jobContainer,
      V1Container initContainer,
      List<V1Volume> volumes,
      Map<String, String> jobDeploymentAnnotations,
      Map<String, String> jobAnnotations,
      Map<String, String> jobLabels,
      List<String> imagePullSecrets)
      throws ApiException {
    if (getK8sSupportsV1CronJob()) {
      updateV1CronJob(
          name,
          image,
          schedule,
          enable,
          jobContainer,
          initContainer,
          volumes,
          jobDeploymentAnnotations,
          jobAnnotations,
          jobLabels,
          imagePullSecrets);
    } else {
      updateV1beta1CronJob(
          name,
          image,
          schedule,
          enable,
          jobContainer,
          initContainer,
          volumes,
          jobDeploymentAnnotations,
          jobAnnotations,
          jobLabels,
          imagePullSecrets);
    }
  }

  public void updateV1beta1CronJob(
      String name,
      String image,
      String schedule,
      boolean enable,
      V1Container jobContainer,
      V1Container initContainer,
      List<V1Volume> volumes,
      Map<String, String> jobDeploymentAnnotations,
      Map<String, String> jobAnnotations,
      Map<String, String> jobLabels,
      List<String> imagePullSecrets)
      throws ApiException {
    var cronJob =
        v1beta1CronJobFromTemplate(
            name,
            schedule,
            !enable,
            jobContainer,
            initContainer,
            volumes,
            jobDeploymentAnnotations,
            jobAnnotations,
            jobLabels,
            imagePullSecrets);
    V1beta1CronJob nsJob =
        new BatchV1beta1Api(getClient())
            .replaceNamespacedCronJob(name, namespace, cronJob, null, null, null, null);
    log.debug(
        "Updated k8s V1beta1 cron job status for name:{}, image:{}, uid:{}, link:{}",
        name,
        image,
        nsJob.getMetadata().getUid(),
        nsJob.getMetadata().getSelfLink());
  }

  public void updateV1CronJob(
      String name,
      String image,
      String schedule,
      boolean enable,
      V1Container jobContainer,
      V1Container initContainer,
      List<V1Volume> volumes,
      Map<String, String> jobDeploymentAnnotations,
      Map<String, String> jobAnnotations,
      Map<String, String> jobLabels,
      List<String> imagePullSecrets)
      throws ApiException {
    var cronJob =
        v1CronJobFromTemplate(
            name,
            schedule,
            !enable,
            jobContainer,
            initContainer,
            volumes,
            jobDeploymentAnnotations,
            jobAnnotations,
            jobLabels,
            imagePullSecrets);
    V1CronJob nsJob =
        new BatchV1Api(getClient())
            .replaceNamespacedCronJob(name, namespace, cronJob, null, null, null, null);
    log.debug(
        "Updated k8s V1 cron job status for name:{}, image:{}, uid:{}, link:{}",
        name,
        image,
        nsJob.getMetadata().getUid(),
        nsJob.getMetadata().getSelfLink());
  }

  /**
   * Reads the deployment status of a cron job in a Kubernetes cluster. The method first tries to
   * read the cron job using the V1Beta API, and if it fails, it falls back to reading the cron job
   * using the V1 API.
   *
   * @param cronJobName the name of the cron job to be read
   * @return an Optional containing the deployment status of the cron job if it exists, or an empty
   *     Optional if the cron job does not exist or cannot be read
   */
  public Optional<JobDeploymentStatus> readCronJob(String cronJobName) {
    var jobStatus = readV1beta1CronJob(cronJobName);

    return jobStatus.isPresent() ? jobStatus : readV1CronJob(cronJobName);
  }

  public Optional<JobDeploymentStatus> readV1beta1CronJob(String cronJobName) {
    log.debug("Reading k8s V1beta1 cron job: {}", cronJobName);
    V1beta1CronJob cronJob = null;
    try {
      cronJob = initBatchV1beta1Api().readNamespacedCronJob(cronJobName, namespace, null);
    } catch (ApiException e) {
      log.warn(
          "Could not read cron job: {}; reason: {}",
          cronJobName,
          new KubernetesException("", e).toString());
    }

    return mapV1beta1CronJobToDeploymentStatus(cronJob, cronJobName);
  }

  public Optional<JobDeploymentStatus> readV1CronJob(String cronJobName) {
    log.debug("Reading k8s V1 cron job: {}", cronJobName);
    V1CronJob cronJob = null;
    try {
      cronJob = initBatchV1Api().readNamespacedCronJob(cronJobName, namespace, null);
    } catch (ApiException e) {
      log.warn(
          "Could not read cron job: {}; reason: {}",
          cronJobName,
          new KubernetesException("", e).toString());
    }

    return mapV1CronJobToDeploymentStatus(cronJob, cronJobName);
  }

  private Optional<JobDeploymentStatus> mapV1beta1CronJobToDeploymentStatus(
      V1beta1CronJob cronJob, String cronJobName) {
    JobDeploymentStatus deployment = null;
    String apiVersion = null;

    try {
      apiVersion = cronJob.getApiVersion();
    } catch (NullPointerException e) {
      log.debug("Could not get API version for cronjob {}", cronJobName);
    }

    if (cronJob != null) {
      deployment = new JobDeploymentStatus();
      deployment.setEnabled(!cronJob.getSpec().getSuspend());
      deployment.setDataJobName(cronJob.getMetadata().getName());
      deployment.setMode(
          "release"); // TODO: Get from cron job config when we support testing environments
      deployment.setCronJobName(
          cronJobName == null ? cronJob.getMetadata().getName() : cronJobName);

      // all fields until pod spec are required so no need to check for null
      var annotations = cronJob.getSpec().getJobTemplate().getMetadata().getAnnotations();
      if (annotations != null) {
        deployment.setLastDeployedBy(annotations.get(JobAnnotation.DEPLOYED_BY.getValue()));
        deployment.setLastDeployedDate(annotations.get(JobAnnotation.DEPLOYED_DATE.getValue()));
        deployment.setPythonVersion(annotations.get(JobAnnotation.PYTHON_VERSION.getValue()));
      }

      List<V1Container> containers =
          cronJob.getSpec().getJobTemplate().getSpec().getTemplate().getSpec().getContainers();
      if (!containers.isEmpty()) {
        String image =
            containers.get(0).getImage(); // TODO: Have 2 containers. 1 for VDK and 1 for the job.
        deployment.setImageName(image); // TODO do we really need to return image_name?
      }
      var initContainers =
          cronJob.getSpec().getJobTemplate().getSpec().getTemplate().getSpec().getInitContainers();
      if (!CollectionUtils.isEmpty(initContainers)) {
        String vdkImage = initContainers.get(0).getImage();
        deployment.setVdkImageName(vdkImage);
        deployment.setVdkVersion(DockerImageName.getTag(vdkImage));
      } else {
        log.warn("Missing init container for cronjob {}", cronJobName);
      }

      var labels = cronJob.getSpec().getJobTemplate().getMetadata().getLabels();
      if (labels == null) {
        log.warn(
            "The cronjob of data job '{}' does not have any labels defined.",
            deployment.getDataJobName());
      }
      if (labels != null && labels.containsKey(JobLabel.VERSION.getValue())) {
        deployment.setGitCommitSha(labels.get(JobLabel.VERSION.getValue()));
      } else {
        // Legacy approach to get version:
        deployment.setGitCommitSha(DockerImageName.getTag(deployment.getImageName()));
      }
    }

    return Optional.ofNullable(deployment);
  }

  private Optional<JobDeploymentStatus> mapV1CronJobToDeploymentStatus(
      V1CronJob cronJob, String cronJobName) {
    JobDeploymentStatus deployment = null;
    String apiVersion = null;

    try {
      apiVersion = cronJob.getApiVersion();
    } catch (NullPointerException e) {
      log.debug("Could not get API version for cronjob {}", cronJobName);
    }

    if (cronJob != null && apiVersion != null && apiVersion.equals("batch/v1")) {
      deployment = new JobDeploymentStatus();
      deployment.setEnabled(!cronJob.getSpec().getSuspend());
      deployment.setDataJobName(cronJob.getMetadata().getName());
      deployment.setMode(
          "release"); // TODO: Get from cron job config when we support testing environments
      deployment.setCronJobName(
          cronJobName == null ? cronJob.getMetadata().getName() : cronJobName);

      // all fields until pod spec are required so no need to check for null
      var annotations = cronJob.getSpec().getJobTemplate().getMetadata().getAnnotations();
      if (annotations != null) {
        deployment.setLastDeployedBy(annotations.get(JobAnnotation.DEPLOYED_BY.getValue()));
        deployment.setLastDeployedDate(annotations.get(JobAnnotation.DEPLOYED_DATE.getValue()));
        deployment.setPythonVersion(annotations.get(JobAnnotation.PYTHON_VERSION.getValue()));
      }

      List<V1Container> containers =
          cronJob.getSpec().getJobTemplate().getSpec().getTemplate().getSpec().getContainers();
      if (!containers.isEmpty()) {
        String image =
            containers.get(0).getImage(); // TODO: Have 2 containers. 1 for VDK and 1 for the job.
        deployment.setImageName(image); // TODO do we really need to return image_name?
      }
      var initContainers =
          cronJob.getSpec().getJobTemplate().getSpec().getTemplate().getSpec().getInitContainers();
      if (!CollectionUtils.isEmpty(initContainers)) {
        String vdkImage = initContainers.get(0).getImage();
        deployment.setVdkImageName(vdkImage);
        deployment.setVdkVersion(DockerImageName.getTag(vdkImage));
      } else {
        log.warn("Missing init container for cronjob {}", cronJobName);
      }

      var labels = cronJob.getSpec().getJobTemplate().getMetadata().getLabels();
      if (labels == null) {
        log.warn(
            "The cronjob of data job '{}' does not have any labels defined.",
            deployment.getDataJobName());
      }
      if (labels != null && labels.containsKey(JobLabel.VERSION.getValue())) {
        deployment.setGitCommitSha(labels.get(JobLabel.VERSION.getValue()));
      } else {
        // Legacy approach to get version:
        deployment.setGitCommitSha(DockerImageName.getTag(deployment.getImageName()));
      }
    }

    return Optional.ofNullable(deployment);
  }

  /**
   * Fetch all deployment statuses from Kubernetes
   *
   * @return List of {@link JobDeploymentStatus} or empty list if there is an error while fetching
   *     data
   */
  public List<JobDeploymentStatus> readJobDeploymentStatuses() {
    if (getK8sSupportsV1CronJob()) {
      return Stream.concat(
              readV1CronJobDeploymentStatuses().stream(),
              readV1beta1CronJobDeploymentStatuses().stream())
          .collect(Collectors.toList());
    } else {
      return readV1beta1CronJobDeploymentStatuses();
    }
  }

  public List<JobDeploymentStatus> readV1beta1CronJobDeploymentStatuses() {
    log.debug("Reading all k8s V1beta1 cron jobs");
    V1beta1CronJobList cronJobs = null;
    try {
      cronJobs =
          initBatchV1beta1Api()
              .listNamespacedCronJob(
                  namespace, null, null, null, null, null, null, null, null, null, null);
    } catch (ApiException e) {
      log.warn("Failed to read k8s cron jobs: ", new KubernetesException("", e));
    }

    return cronJobs == null
        ? Collections.emptyList()
        : cronJobs.getItems().stream()
            .map(cronJob -> mapV1beta1CronJobToDeploymentStatus(cronJob, null))
            .flatMap(Optional::stream)
            .collect(Collectors.toList());
  }

  public List<JobDeploymentStatus> readV1CronJobDeploymentStatuses() {
    log.debug("Reading all k8s V1 cron jobs");
    V1CronJobList cronJobs = null;
    try {
      cronJobs =
          initBatchV1Api()
              .listNamespacedCronJob(
                  namespace, null, null, null, null, null, null, null, null, null, null);
    } catch (ApiException e) {
      log.warn("Failed to read k8s cron jobs: ", new KubernetesException("", e));
    }

    return cronJobs == null
        ? Collections.emptyList()
        : cronJobs.getItems().stream()
            .map(cronJob -> mapV1CronJobToDeploymentStatus(cronJob, null))
            .flatMap(Optional::stream)
            .collect(Collectors.toList());
  }
}
