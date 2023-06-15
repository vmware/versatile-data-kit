/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.google.common.annotations.VisibleForTesting;
import com.google.common.base.Charsets;
import com.google.common.collect.Iterables;
import com.google.gson.JsonSyntaxException;
import com.google.gson.reflect.TypeToken;
import com.vmware.taurus.exception.JsonDissectException;
import com.vmware.taurus.exception.KubernetesException;
import com.vmware.taurus.exception.KubernetesJobDefinitionException;
import com.vmware.taurus.exception.DataJobExecutionCannotBeCancelledException;
import com.vmware.taurus.exception.ExecutionCancellationFailureReason;
import com.vmware.taurus.service.deploy.DockerImageName;
import com.vmware.taurus.service.deploy.JobCommandProvider;
import com.vmware.taurus.service.model.JobAnnotation;
import com.vmware.taurus.service.model.JobDeploymentStatus;
import com.vmware.taurus.service.model.JobLabel;
import com.vmware.taurus.service.threads.ThreadPoolConf;
import io.kubernetes.client.openapi.ApiClient;
import io.kubernetes.client.openapi.ApiException;
import io.kubernetes.client.openapi.Configuration;
import io.kubernetes.client.PodLogs;
import io.kubernetes.client.openapi.apis.*;
import io.kubernetes.client.custom.IntOrString;
import io.kubernetes.client.custom.Quantity;
import io.kubernetes.client.openapi.models.*;
import io.kubernetes.client.util.Watch;
import io.kubernetes.client.util.Yaml;
import lombok.*;
import net.javacrumbs.shedlock.spring.annotation.EnableSchedulerLock;
import org.apache.commons.lang3.StringUtils;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.apache.commons.lang3.tuple.Pair;
import org.slf4j.Logger;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.io.ClassPathResource;
import org.springframework.stereotype.Service;
import org.springframework.util.CollectionUtils;

import java.io.*;
import java.math.BigInteger;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.time.Instant;
import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.util.*;
import java.util.function.Consumer;
import java.util.function.Function;
import java.util.stream.Collectors;
import java.util.stream.Stream;

/**
 * A facade over Kubernetes (https://en.wikipedia.org/wiki/Facade_pattern) (not complete see
 * JobImageDeployer)
 *
 * <p>This way there's clear description on what parts of Kubernetes the app depends on. Or changing
 * underlying kubernetes client can be done with changes in a single place.
 *
 * <p>TODO: Consider all methods to throw KubernetesException (instead of ApiException) because: *
 * Better encapsulation * KubernetesException is more detailed and actually prints the cause. TODO:
 * automatically inject standard labels like OpID, Data Job Name, User.
 *
 * <p>We are using sub-classes for different type of connections in order to make use of class-based
 * auto-wiring in Spring.
 *
 * @see com.vmware.taurus.service.kubernetes.ControlKubernetesService
 * @see com.vmware.taurus.service.kubernetes.DataJobsKubernetesService
 */
@Service
public abstract class KubernetesService {

  public static final String LABEL_PREFIX = "com.vmware.taurus";
  private static final int WATCH_JOBS_TIMEOUT_SECONDS = 300;


  private static int fromInteger(Integer value) {
    return Optional.ofNullable(value).orElse(0);
  }

  private static long fromDateTime(OffsetDateTime value) {
    return Optional.ofNullable(value)
        .map(OffsetDateTime::toInstant)
        .map(Instant::toEpochMilli)
        .orElse(0L);
  }

  @Value
  @AllArgsConstructor
  public static class JobStatus {
    private final int active;
    private final int failed;
    private final int succeeded;
    private final long started;
    private final long completed;

    JobStatus(V1JobStatus status) {
      this(
          KubernetesService.fromInteger(status.getActive()),
          KubernetesService.fromInteger(status.getFailed()),
          KubernetesService.fromInteger(status.getSucceeded()),
          KubernetesService.fromDateTime(status.getStartTime()),
          KubernetesService.fromDateTime(status.getCompletionTime()));
    }
  }

  @Value
  public static class JobStatusCondition {
    private final boolean success;
    private final String type;
    private final String reason;
    private final String message;
    long completionTime;
  }

  @Value
  public static class Resources {
    private final String cpu;
    private final String memory;
  }

  @Value
  public static class Probe {
    private final int port;
    private final String path;
    private final int period;
  }

  @Value
  @Builder
  @ToString
  public static class JobExecution {
    String executionId;
    String executionType;
    String jobName;
    String mainContainerTerminationMessage;
    String jobTerminationReason;
    Boolean succeeded;
    String opId;
    OffsetDateTime startTime;
    OffsetDateTime endTime;
    String jobVersion;
    String jobSchedule;
    String jobPythonVersion;
    Float resourcesCpuRequest;
    Float resourcesCpuLimit;
    Integer resourcesMemoryRequest;
    Integer resourcesMemoryLimit;
    OffsetDateTime deployedDate;
    String deployedBy;
    String mainContainerTerminationReason;
    String initContainerTerminationReason;
  }

  @AllArgsConstructor
  private enum ContainerResourceType {
    CPU("cpu"),
    MEMORY("memory");

    @Getter private final String value;
  }


  @org.springframework.beans.factory.annotation.Value(
      "${datajobs.control.k8s.jobTTLAfterFinishedSeconds}")
  protected int jobTTLAfterFinishedSeconds;

  protected String namespace;
  private final Logger log;
  private final ApiClient client;
  protected final BatchV1Api batchV1Api;
  private final boolean k8sSupportsV1CronJob;

  /**
   * @param namespace the namespace where the kubernetes operation will act on. leave empty to infer
   *     from kubeconfig
   * @param k8sSupportsV1CronJob Whether the target K8s cluster supports the V1CronJob API
   * @param log log to use - used in subclasses in order to set classname to subclass.
   */
  protected KubernetesService(
      String namespace,
      boolean k8sSupportsV1CronJob,
      Logger log,
      ApiClient client,
      BatchV1Api batchV1Api) {
    this.namespace = namespace;
    this.k8sSupportsV1CronJob = k8sSupportsV1CronJob;
    this.log = log;
    this.client = client;
    this.batchV1Api = batchV1Api;
  }

  protected boolean getK8sSupportsV1CronJob() {
    return this.k8sSupportsV1CronJob;
  }


  private List<String> getNamespaceFileContents() {
    try {
      String namespaceFile = "/var/run/secrets/kubernetes.io/serviceaccount/namespace";
      return Files.readAllLines(Paths.get(namespaceFile));
    } catch (IOException e) {
      return Collections.emptyList();
    }
  }

  public Pair<Boolean, String> health() {
    try {
      var info = new VersionApi(client).getCode();
      return Pair.of(true, info.getGitVersion());
    } catch (Exception e) {
      return Pair.of(false, e.getMessage());
    }
  }

  public void deleteNamespace(String namespaceName) throws ApiException {
    try {
      new CoreV1Api(client).deleteNamespace(namespaceName, null, null, null, null, null, null);
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
    }
  }

  public Set<String> listJobs() throws ApiException {
    log.debug("Listing k8s jobs");
    var jobs =
        batchV1Api.listNamespacedJob(
            namespace, null, null, null, null, null, null, null, null, null, null);
    var set =
        jobs.getItems().stream().map(j -> j.getMetadata().getName()).collect(Collectors.toSet());
    log.debug("K8s jobs: {}", set);
    return set;
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
          batchV1Api.deleteNamespacedJobWithHttpInfo(
              executionId, namespace, null, null, null, null, "Foreground", null);
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

  public void createJob(
      String name,
      String image,
      boolean privileged,
      boolean readOnlyRootFilesystem,
      Map<String, String> envs,
      List<String> args,
      List<V1Volume> volumes,
      List<V1VolumeMount> volumeMounts,
      String imagePullPolicy,
      Resources request,
      Resources limit,
      long runAsUser,
      long runAsGroup,
      long fsGroup,
      String serviceAccountName,
      String registrySecret)
      throws ApiException {

    log.debug("Creating k8s job name:{}, image:{}", name, image);
    var podSpecBuilder =
        new V1PodSpecBuilder()
            .withRestartPolicy("Never")
            .withContainers(
                container(
                    name,
                    image,
                    privileged,
                    readOnlyRootFilesystem,
                    envs,
                    args,
                    volumeMounts,
                    imagePullPolicy,
                    request,
                    limit,
                    null))
            .withVolumes(volumes)
            .withSecurityContext(
                new V1PodSecurityContext()
                    .runAsUser(runAsUser)
                    .runAsGroup(runAsGroup)
                    .fsGroup(fsGroup));

    if (StringUtils.isNotEmpty(serviceAccountName)) {
      podSpecBuilder.withServiceAccountName(serviceAccountName);
    }
    if (StringUtils.isNotEmpty(registrySecret)) {
      podSpecBuilder.addNewImagePullSecret().withName(registrySecret).endImagePullSecret();
    }
    var template = new V1PodTemplateSpecBuilder().withSpec(podSpecBuilder.build()).build();
    var spec =
        new V1JobSpecBuilder()
            .withBackoffLimit(3) // TODO configure
            .withTtlSecondsAfterFinished(jobTTLAfterFinishedSeconds)
            .withTemplate(template)
            .build();
    createNewJob(name, spec, Collections.emptyMap(), Collections.emptyMap());
  }

  // Default for testing purposes
  public void createNewJob(
      String name, V1JobSpec spec, Map<String, String> labels, Map<String, String> annotations)
      throws ApiException {
    var job =
        new V1JobBuilder()
            .withMetadata(
                new V1ObjectMetaBuilder()
                    .withName(name)
                    .addToLabels(labels)
                    .addToAnnotations(annotations)
                    .build())
            .withSpec(spec)
            .build();

    V1Job nsJob = batchV1Api.createNamespacedJob(namespace, job, null, null, null, null);
    log.debug("Created k8s job: {}", nsJob);
    log.debug(
        "Created k8s job name: {}, uid:{}, link:{}",
        nsJob.getMetadata().getName(),
        nsJob.getMetadata().getUid(),
        nsJob.getMetadata().getSelfLink());
  }

  public Optional<V1Pod> getPod(String podName) throws ApiException {
    List<V1Pod> allPods =
        new CoreV1Api(client)
            .listNamespacedPod(
                namespace, "false", null, null, null, null, null, null, null, null, null)
            .getItems();

    return allPods.stream()
        .filter(pod -> pod.getMetadata().getName().startsWith(podName))
        .findFirst();
  }

  private List<V1Pod> listJobPods(V1Job job) throws ApiException {
    var labelsToSelect = Map.of("job-name", job.getMetadata().getName());
    log.debug("Getting pods with labels {}", labelsToSelect);
    String labelSelector = buildLabelSelector(labelsToSelect);
    var pods =
        new CoreV1Api(client)
            .listNamespacedPod(
                namespace, null, null, null, null, labelSelector, null, null, null, null, null)
            .getItems();
    log.trace("K8s pods with label selector {}: {}", labelSelector, pods);
    return pods;
  }

  public boolean isRunningJob(String dataJobName) throws ApiException {
    var labelsToSelect = Map.of(JobLabel.NAME.getValue(), dataJobName);
    String labelSelector = buildLabelSelector(labelsToSelect);
    V1JobList v1JobList =
        batchV1Api.listNamespacedJob(
            namespace, null, null, null, null, labelSelector, null, null, null, null, null);

    // In this case we use getConditions() instead of getActive()
    // because if the job is in init state the active flag is zero.
    // We want to track those jobs as submitted as well.
    // The getConditions() returns result only if the job is completed.
    return Optional.ofNullable(v1JobList).map(V1JobList::getItems).stream()
        .flatMap(Collection::stream)
        .map(V1Job::getStatus)
        .filter(Objects::nonNull)
        .map(V1JobStatus::getConditions)
        .anyMatch(CollectionUtils::isEmpty);
  }

  public String getPodLogs(String podName) throws IOException, ApiException {
    log.info("Get logs for pod {}", podName);
    Optional<V1Pod> pod = getPod(podName);

    String logs = "";
    if (pod.isPresent()) {
      PodLogs podLogs = new PodLogs(client);

      try (BufferedReader br =
          new BufferedReader(
              new InputStreamReader(podLogs.streamNamespacedPodLog(pod.get()), Charsets.UTF_8))) {
        // The builder logs are relatively small so we can afford to load it all in memory for
        // easier processing.
        log.info("Retrieving logs for Pod with name: {}", podName);
        logs =
            br.lines()
                .peek(s -> log.debug("[{}] {}", podName, s))
                .collect(Collectors.joining(System.lineSeparator()));
      }
    }
    return logs;
  }

  public Optional<String> getJobLogs(String jobName, Integer tailLines)
      throws ApiException, IOException {
    var job = getJob(jobName);
    if (job.isPresent()) {
      var pods = listJobPods(job.get());
      if (pods.size() > 0) {
        var pod = pods.get(pods.size() - 1);
        PodLogs podLogs = new PodLogs(client);

        try (BufferedReader br =
            new BufferedReader(
                new InputStreamReader(
                    podLogs.streamNamespacedPodLog(
                        pod.getMetadata().getNamespace(),
                        pod.getMetadata().getName(),
                        pod.getSpec().getContainers().get(0).getName(),
                        null,
                        tailLines,
                        true),
                    Charsets.UTF_8))) {
          String logs = br.lines().collect(Collectors.joining(System.lineSeparator()));
          return Optional.of(logs);
        }
      }
    }
    return Optional.empty();
  }

  public JobStatusCondition watchJob(
      String jobName, int timeoutSeconds, Consumer<JobStatus> watcher)
      throws ApiException, IOException, InterruptedException {
    log.debug("Watch job {}; timeoutSeconds: {}", jobName, timeoutSeconds);
    JobStatusCondition condition = null;
    // we may have started watching too soon
    // TODO: set resourceVersion when watching to optimize waits or even avoid the loop here ?
    // https://kubernetes.io/docs/reference/using-api/api-concepts/#resource-versions
    // https://kubernetes.io/docs/reference/using-api/api-concepts/#efficient-detection-of-changes
    int counter = timeoutSeconds;
    while (condition == null && --counter > 0) {
      Thread.sleep(1000);
      condition = watchJobInternal(jobName, timeoutSeconds, watcher);
    }
    if (condition == null) {
      condition = new JobStatusCondition(false, null, "Cannot determine job status", "", 0);
    }
    return condition;
  }

  private JobStatusCondition watchJobInternal(
      String jobName, int timeoutSeconds, Consumer<JobStatus> watcher)
      throws IOException, ApiException {
    String fieldSelector = String.format("metadata.name=%s", jobName);
    try (Watch<V1Job> watch =
        Watch.createWatch(
            Configuration.getDefaultApiClient(),
            batchV1Api.listNamespacedJobCall(
                namespace,
                null,
                null,
                null,
                fieldSelector,
                null,
                null,
                null,
                null,
                timeoutSeconds,
                true,
                null),
            new TypeToken<Watch.Response<V1Job>>() {}.getType())) {
      for (var response : watch) {
        log.debug("watch k8s response type: {}", response.type);
        var job = response.object;

        var status = new JobStatus(job.getStatus());
        log.debug("watch k8s status: {}", status);
        watcher.accept(status);

        return getJobCondition(job);
      }
    } catch (RuntimeException e) {
      log.info(
          "Could not get status of a job. " + " Error was: " + e.getMessage(),
          " Will try to get status again from kubernetes if the job exists");
      var job = getJob(jobName);
      return getJobCondition(job.get());
    }
    return null;
  }

  private static String buildLabelSelector(Map<String, String> labels) {
    if (labels == null) {
      return null;
    }
    return labels.entrySet().stream()
        .map(e -> e.getKey() + "=" + e.getValue())
        .collect(Collectors.joining(","));
  }

  private static String getContainerName(V1Job job) {
    Objects.requireNonNull(job, "The job cannot be null");

    var containers =
        Optional.ofNullable(job.getSpec())
            .map(V1JobSpec::getTemplate)
            .map(V1PodTemplateSpec::getSpec)
            .map(V1PodSpec::getContainers)
            .orElse(null);

    return (containers != null && !containers.isEmpty()) ? containers.get(0).getName() : null;
  }

  private static Optional<V1ContainerStateTerminated> getTerminatedState(
      V1Pod pod, Function<V1PodStatus, List<V1ContainerStatus>> containerStatusFunction) {
    Objects.requireNonNull(pod, "The pod cannot be null");
    var status = pod.getStatus();
    if (status == null
        || status.getContainerStatuses() == null
        || status.getContainerStatuses().isEmpty()) {
      return Optional.empty();
    }
    final var containerStatus = containerStatusFunction.apply(status).get(0);
    return getTerminatedState(containerStatus.getState())
        .or(() -> getTerminatedState(containerStatus.getLastState()));
  }

  private static Optional<V1ContainerStateTerminated> getTerminatedState(V1ContainerState state) {
    return (state == null || state.getTerminated() == null)
        ? Optional.empty()
        : Optional.ofNullable(state.getTerminated());
  }

  /**
   * Returns the termination status of the specified job by looking at its associated pods and
   * searching for the last terminated one.
   *
   * @param job The job whose status to return.
   * @return A {@link V1ContainerStateTerminated} object representing the termination status of the
   *     job.
   */
  ImmutablePair<Optional<V1ContainerStateTerminated>, Optional<V1ContainerStateTerminated>>
      getTerminationStatus(V1Job job) {
    List<V1Pod> jobPods;

    try {
      jobPods = listJobPods(job);
    } catch (ApiException ex) {
      log.info(
          "Could not list pods for job {}",
          job.getMetadata().getName(),
          new KubernetesException("", ex));
      return ImmutablePair.of(Optional.empty(), Optional.empty());
    }

    var lastMainTerminatedPodState =
        jobPods.stream()
            .map(v1Pod -> getTerminatedState(v1Pod, V1PodStatus::getContainerStatuses))
            .filter(Optional::isPresent)
            .map(Optional::get)
            .max(Comparator.comparing(V1ContainerStateTerminated::getFinishedAt));

    if (lastMainTerminatedPodState.isEmpty()) {
      log.info("Could not find a main terminated pod for job {}", job.getMetadata().getName());
    }

    var lastInitTerminatedPodState =
        jobPods.stream()
            .map(v1Pod -> getTerminatedState(v1Pod, V1PodStatus::getInitContainerStatuses))
            .filter(Optional::isPresent)
            .map(Optional::get)
            .max(Comparator.comparing(V1ContainerStateTerminated::getFinishedAt));

    if (lastInitTerminatedPodState.isEmpty()) {
      log.info("Could not find a data job terminated pod for job {}", job.getMetadata().getName());
    }

    return ImmutablePair.of(lastInitTerminatedPodState, lastMainTerminatedPodState);
  }

  /**
   * Returns the Data Job execution status of the specified job
   *
   * @param job The job whose status to return.
   * @return A {@link JobExecution} object representing the Data Job execution status.
   */
  Optional<JobExecution> getJobExecutionStatus(V1Job job, JobStatusCondition jobStatusCondition) {
    JobExecution.JobExecutionBuilder jobExecutionStatusBuilder = JobExecution.builder();
    // jobCondition = null means that the K8S Job is still running
    if (jobStatusCondition != null) {
      // Job termination status
      ImmutablePair<Optional<V1ContainerStateTerminated>, Optional<V1ContainerStateTerminated>>
          podTerminationStatus = getTerminationStatus(job);

      Optional<V1ContainerStateTerminated> lastInitContainerStateTerminated =
          podTerminationStatus.getLeft();
      // Termination Reason of the pod init container
      lastInitContainerStateTerminated
          .map(
              v1ContainerStateTerminated ->
                  StringUtils.trim(v1ContainerStateTerminated.getReason()))
          .ifPresent(jobExecutionStatusBuilder::initContainerTerminationReason);

      Optional<V1ContainerStateTerminated> lastMainContainerStateTerminated =
          podTerminationStatus.getRight();
      // If the job completed but its pod did not produce a termination message, we infer the
      // termination status later, based on the status of the job itself.
      lastMainContainerStateTerminated
          .map(
              v1ContainerStateTerminated ->
                  StringUtils.trim(v1ContainerStateTerminated.getMessage()))
          .ifPresent(jobExecutionStatusBuilder::mainContainerTerminationMessage);
      jobExecutionStatusBuilder.jobTerminationReason(jobStatusCondition.getReason());

      // Termination Reason of the data job pod container
      lastMainContainerStateTerminated
          .map(
              v1ContainerStateTerminated ->
                  StringUtils.trim(v1ContainerStateTerminated.getReason()))
          .ifPresent(s -> jobExecutionStatusBuilder.mainContainerTerminationReason(s));
    }

    // Job resources
    Optional<V1Container> containerOptional =
        Optional.ofNullable(job.getSpec())
            .map(V1JobSpec::getTemplate)
            .map(V1PodTemplateSpec::getSpec)
            .map(V1PodSpec::getContainers)
            .filter(v1Containers -> !CollectionUtils.isEmpty(v1Containers))
            .map(v1Containers -> v1Containers.get(0));

    Optional<Map<String, Quantity>> resourcesRequest =
        containerOptional.map(V1Container::getResources).map(V1ResourceRequirements::getRequests);
    jobExecutionStatusBuilder.resourcesCpuRequest(
        resourcesRequest
            .map(stringQuantityMap -> stringQuantityMap.get(ContainerResourceType.CPU.getValue()))
            .map(Quantity::getNumber)
            .map(Number::floatValue)
            .orElse(null));
    jobExecutionStatusBuilder.resourcesMemoryRequest(
        resourcesRequest
            .map(
                stringQuantityMap -> stringQuantityMap.get(ContainerResourceType.MEMORY.getValue()))
            .map(KubernetesService::convertMemoryToMBs)
            .orElse(null));

    Optional<Map<String, Quantity>> resourcesLimit =
        containerOptional.map(V1Container::getResources).map(V1ResourceRequirements::getLimits);
    jobExecutionStatusBuilder.resourcesCpuLimit(
        resourcesLimit
            .map(stringQuantityMap -> stringQuantityMap.get(ContainerResourceType.CPU.getValue()))
            .map(Quantity::getNumber)
            .map(Number::floatValue)
            .orElse(null));
    jobExecutionStatusBuilder.resourcesMemoryLimit(
        resourcesLimit
            .map(
                stringQuantityMap -> stringQuantityMap.get(ContainerResourceType.MEMORY.getValue()))
            .map(quantity -> convertMemoryToMBs(quantity))
            .orElse(null));

    // Job metadata
    Optional<V1ObjectMeta> metadata = Optional.ofNullable(job.getMetadata());

    jobExecutionStatusBuilder.executionId(metadata.map(V1ObjectMeta::getName).orElse(null));

    // Job labels
    Optional<Map<String, String>> labels = metadata.map(V1ObjectMeta::getLabels);

    jobExecutionStatusBuilder.jobVersion(
        labels
            .map(stringStringMap -> stringStringMap.get(JobLabel.VERSION.getValue()))
            .orElse(
                containerOptional
                    .map(V1Container::getImage)
                    .map(imageStr -> imageStr.substring(imageStr.lastIndexOf(":") + 1))
                    .orElse(null)));

    jobExecutionStatusBuilder.jobName(
        labels
            .map(stringStringMap -> stringStringMap.get(JobLabel.NAME.getValue()))
            .orElse(getContainerName(job)));

    // Job annotations
    Optional<Map<String, String>> annotations = metadata.map(V1ObjectMeta::getAnnotations);

    jobExecutionStatusBuilder.deployedDate(
        annotations
            .map(stringStringMap -> stringStringMap.get(JobAnnotation.DEPLOYED_DATE.getValue()))
            .filter(lastDeployedDateStr -> StringUtils.isNotBlank(lastDeployedDateStr))
            .map(lastDeployedDateStr -> OffsetDateTime.parse(lastDeployedDateStr))
            .orElse(null));

    jobExecutionStatusBuilder.deployedBy(
        annotations
            .map(stringStringMap -> stringStringMap.get(JobAnnotation.DEPLOYED_BY.getValue()))
            .orElse(null));

    jobExecutionStatusBuilder.executionType(
        annotations
            .map(stringStringMap -> stringStringMap.get(JobAnnotation.EXECUTION_TYPE.getValue()))
            .orElse(null));

    jobExecutionStatusBuilder.opId(
        annotations
            .map(stringStringMap -> stringStringMap.get(JobAnnotation.OP_ID.getValue()))
            .orElse(metadata.map(V1ObjectMeta::getName).orElse(null)));

    jobExecutionStatusBuilder.jobSchedule(
        annotations
            .map(stringStringMap -> stringStringMap.get(JobAnnotation.SCHEDULE.getValue()))
            .orElse(null));

    jobExecutionStatusBuilder.jobPythonVersion(
        annotations
            .map(stringStringMap -> stringStringMap.get(JobAnnotation.PYTHON_VERSION.getValue()))
            .orElse(null));

    // Job status
    Optional<V1JobStatus> jobStatus = Optional.ofNullable(job.getStatus());

    jobExecutionStatusBuilder.startTime(
        jobStatus
            .map(V1JobStatus::getStartTime)
            .map(startTime -> Instant.ofEpochMilli(startTime.toInstant().toEpochMilli()))
            .map(startTimeInstant -> OffsetDateTime.ofInstant(startTimeInstant, ZoneOffset.UTC))
            .orElse(null));

    jobExecutionStatusBuilder.endTime(
        Optional.ofNullable(jobStatusCondition)
            .map(JobStatusCondition::getCompletionTime)
            .map(endTime -> Instant.ofEpochMilli(endTime))
            .map(endTimeInstant -> OffsetDateTime.ofInstant(endTimeInstant, ZoneOffset.UTC))
            .orElse(null));

    // jobCondition = null means that the Data Job is still running
    jobExecutionStatusBuilder.succeeded(
        Optional.ofNullable(jobStatusCondition).map(JobStatusCondition::isSuccess).orElse(null));

    return Optional.of(jobExecutionStatusBuilder.build());
  }

  /**
   * Initiates a watch for the jobs with labels specified by {@code labelsToWatch}. The watch will
   * be active for no longer than the number of seconds specified by {@code timeoutSeconds}. The
   * specified watcher is invoked whenever a job is completed and has an associated pod with a
   * termination message.
   *
   * @param labelsToWatch The labels for the jobs to watch, or null, to watch all jobs.
   * @param watcher A {@link Consumer} to receive notifications about completed jobs.
   * @param lastWatchTime The time of the last completed job watch, expressed in millis since Epoch.
   * @throws ApiException
   * @throws IOException
   */
  public void watchJobs(
      Map<String, String> labelsToWatch,
      Consumer<JobExecution> watcher,
      Consumer<List<String>> runningJobExecutionsConsumer,
      long lastWatchTime)
      throws IOException, ApiException {

    watchJobs(
        labelsToWatch,
        watcher,
        runningJobExecutionsConsumer,
        lastWatchTime,
        WATCH_JOBS_TIMEOUT_SECONDS);
  }

  /**
   * Initiates a watch for the jobs with labels specified by {@code labelsToWatch}. The watch will
   * be active for no longer than the number of seconds specified by {@code timeoutSeconds}. The
   * specified watcher is invoked whenever a job is completed and has an associated pod with a
   * termination message.
   *
   * @param labelsToWatch The labels for the jobs to watch, or null, to watch all jobs.
   * @param watcher A {@link Consumer} to receive notifications about completed jobs.
   * @param lastWatchTime The time of the last completed job watch, expressed in millis since Epoch.
   * @param timeoutSeconds The maximum number of seconds that the watch should be active, or null,
   *     to watch using the default timeout configured on the server (usually 5 minutes). If this
   *     value is changed, the {@code defaultLockAtMostFor} value of the {@link EnableSchedulerLock}
   *     annotation (see {@link ThreadPoolConf}) should be adjusted accordingly to ensure that the
   *     lock will be held long enough for the watch to complete.
   * @throws ApiException
   * @throws IOException
   */
  public void watchJobs(
      Map<String, String> labelsToWatch,
      Consumer<JobExecution> watcher,
      Consumer<List<String>> runningJobExecutionsConsumer,
      long lastWatchTime,
      Integer timeoutSeconds)
      throws ApiException, IOException {

    Objects.requireNonNull(watcher, "The watcher cannot be null");
    log.info("Start watching jobs with labels: {}", labelsToWatch);

    // Job change detection implementation:
    // https://kubernetes.io/docs/reference/using-api/api-concepts/#efficient-detection-of-changes
    String labelSelector = buildLabelSelector(labelsToWatch);
    String resourceVersion;
    try {
      var jobList =
          batchV1Api.listNamespacedJob(
              namespace, "false", null, null, null, labelSelector, null, null, null, null, null);
      List<String> runningExecutionIds = new ArrayList<>();

      jobList
          .getItems()
          .forEach(
              job -> {
                var condition = getJobCondition(job);

                if (condition == null) {
                  Optional.ofNullable(job.getMetadata())
                      .map(V1ObjectMeta::getName)
                      .ifPresent(executionId -> runningExecutionIds.add(executionId));
                } else if (condition.getCompletionTime() > lastWatchTime) {
                  getJobExecutionStatus(job, condition).ifPresent(watcher);
                }
              });

      runningJobExecutionsConsumer.accept(runningExecutionIds);
      resourceVersion = jobList.getMetadata().getResourceVersion();
    } catch (ApiException ex) {
      log.info("Failed to list jobs for watching. Error was: {}", ex.getMessage());
      return;
    }

    try (Watch<V1Job> watch =
        Watch.createWatch(
            Configuration.getDefaultApiClient(),
            batchV1Api.listNamespacedJobCall(
                namespace,
                null,
                null,
                null,
                null,
                labelSelector,
                null,
                resourceVersion,
                null,
                timeoutSeconds,
                true,
                null),
            new TypeToken<Watch.Response<V1Job>>() {}.getType())) {
      for (var response : watch) {
        if (response.status != null) {
          // Watch failed, possibly due to the specified resource version no longer present
          log.info("Failed to watch jobs. Error was: {}", response.status.getMessage());
          break;
        }

        var job = response.object;

        if (job == null) {
          log.info("Failed to watch jobs due to the missing V1Job object.");
          break;
        }

        log.debug("Job {} is {}", job.getMetadata().getName(), response.type);

        if (!"DELETED".equals(response.type)) {
          // Occasionally events arrive for jobs that have completed into the past.
          // Ignore events that have arrived later than one hour after the job's completion time
          var condition = getJobCondition(job);
          boolean isLateEvent = false;
          if (condition != null && condition.getCompletionTime() != 0) {
            Instant jobCompletionTime = Instant.ofEpochMilli(condition.getCompletionTime());
            isLateEvent = Instant.now().isAfter(jobCompletionTime.plusSeconds(3600));
          }
          if (!isLateEvent) {
            getJobExecutionStatus(job, condition).ifPresent(watcher);
          } else {
            log.info(
                "Ignoring a Kubernetes event received after job completion for job {}",
                job.getMetadata().getName());
            log.debug(job.toString());
          }
        }
      }
    } catch (RuntimeException e) {
      log.info("Failed to watch jobs. Error was: {}", e.getMessage(), e);
    }

    log.info("Finish watching jobs with labels: {}", labelsToWatch);
  }

  private JobStatusCondition getJobCondition(V1Job job) {
    V1JobStatus jobStatus = job.getStatus();
    if (jobStatus.getConditions() != null) {
      if (jobStatus.getConditions().size() > 1) {
        log.warn("More than one Job conditions found, returning first only. Job: {}", job);
      }
      for (var c : jobStatus.getConditions()) {
        log.trace(
            "k8s job condition type: {} reason: {} message: {}",
            c.getType(),
            c.getReason(),
            c.getMessage());
        return new JobStatusCondition(
            c.getType().equals("Complete"),
            c.getType(),
            c.getReason(),
            c.getMessage(),
            c.getLastTransitionTime() != null
                ? c.getLastTransitionTime().toInstant().toEpochMilli()
                : 0);
      }
    }
    return null;
  }

  /**
   * Deletes a Job in kubernets with given name if it exists.
   *
   * @param name the name of the job
   * @throws ApiException
   */
  public void deleteJob(String name) throws ApiException {
    log.debug("Deleting k8s job: {}", name);
    try {
      var status =
          batchV1Api.deleteNamespacedJob(name, namespace, null, null, null, null, null, null);
      log.debug("Deleted k8s job: {}, status: {}", name, status);
    } catch (JsonSyntaxException e) {
      log.warn(
          "Ignoring JsonSyntaxException during deleteNamespacedJob {}. Reason: {}",
          name,
          e.getMessage());
    } catch (ApiException e) {
      if (e.getCode() == 404) {
        log.debug("Job {} already deleted or does not exists", name);
      } else {
        throw e;
      }
    }
    log.debug("Deleting k8s pods for job: {}", name);
    var status =
        new CoreV1Api(client)
            .deleteCollectionNamespacedPod(
                namespace,
                null,
                null,
                null,
                null,
                null,
                "job-name=" + name,
                null,
                null,
                null,
                null,
                null,
                null,
                null);
    log.debug("Deleted k8s pods for job: {}, status: {}", name, status);
  }

  public static V1Volume volume(String name) {
    return new V1VolumeBuilder().withName(name).withEmptyDir(new V1EmptyDirVolumeSource()).build();
  }

  public static V1Volume volume(String name, String secretName) {
    return new V1VolumeBuilder()
        .withName(name)
        .withSecret(new V1SecretVolumeSourceBuilder().withSecretName(secretName).build())
        .build();
  }

  public static V1VolumeMount volumeMount(String name, String mountPath, boolean readOnly) {
    return new V1VolumeMountBuilder()
        .withName(name)
        .withMountPath(mountPath)
        .withReadOnly(readOnly)
        .build();
  }

  private Optional<V1Job> getJob(String jobName) throws ApiException {
    String fieldSelector = String.format("metadata.name=%s", jobName);
    try {
      var jobs =
          batchV1Api.listNamespacedJob(
              namespace, null, null, null, fieldSelector, null, null, null, null, null, null);
      if (!jobs.getItems().isEmpty()) {
        return Optional.of(jobs.getItems().get(0));
      }
    } catch (ApiException e) {
      if (e.getCode() != 404) {
        throw e;
      }
    }
    return Optional.empty();
  }


  public static V1Container container(
      String name,
      String image,
      boolean privileged,
      boolean readOnlyRootFilesystem,
      Map<String, String> envs,
      List<String> args,
      List<V1VolumeMount> volumeMounts,
      String imagePullPolicy,
      Resources request,
      Resources limit,
      Probe probe,
      List commands) {
    var builder =
        new V1ContainerBuilder()
            .withName(name)
            .withImage(image)
            .withVolumeMounts(volumeMounts)
            .withImagePullPolicy(imagePullPolicy)
            .withSecurityContext(
                new V1SecurityContextBuilder()
                    .withPrivileged(privileged)
                    .withReadOnlyRootFilesystem(readOnlyRootFilesystem)
                    .build())
            .withResources(
                new V1ResourceRequirementsBuilder()
                    .withRequests(resources(request))
                    .withLimits(resources(limit))
                    .build())
            .withEnvFrom(
                new V1EnvFromSource()
                    .secretRef(new V1SecretEnvSource().name("builder-secrets").optional(true)))
            .withEnv(
                envs.entrySet().stream()
                    .map(KubernetesService::envVar)
                    .collect(Collectors.toList()))
            .withArgs(args)
            .withCommand(commands);

    if (probe != null) {
      builder.withLivenessProbe(
          new V1ProbeBuilder()
              .withHttpGet(
                  new V1HTTPGetActionBuilder()
                      .withPort(new IntOrString(probe.port))
                      .withPath(probe.path)
                      .build())
              .withInitialDelaySeconds(probe.period)
              .withPeriodSeconds(probe.period)
              .build());
    }

    return builder.build();
  }

  private static V1Container container(
      String name,
      String image,
      boolean privileged,
      boolean readOnlyRootFilesystem,
      Map<String, String> envs,
      List<String> args,
      List<V1VolumeMount> volumeMounts,
      String imagePullPolicy,
      Resources request,
      Resources limit,
      Probe probe) {
    return container(
        name,
        image,
        privileged,
        readOnlyRootFilesystem,
        envs,
        args,
        volumeMounts,
        imagePullPolicy,
        request,
        limit,
        probe,
        List.of());
  }

  private static Map<String, Quantity> resources(Resources resources) {
    return Map.of(
        "cpu",
        Quantity.fromString(resources.getCpu()),
        "memory",
        Quantity.fromString(resources.getMemory()));
  }

  private static V1EnvVar envVar(Map.Entry<String, String> entry) {
    var b = new V1EnvVarBuilder().withName(entry.getKey());
    if (entry.getValue().startsWith("$")) {
      b.withValueFrom(
          new V1EnvVarSourceBuilder()
              .withFieldRef(
                  new V1ObjectFieldSelectorBuilder()
                      .withFieldPath(entry.getValue().substring(1))
                      .build())
              .build());
    } else {
      b.withValue(entry.getValue());
    }
    return b.build();
  }

  /** Get secret data from kubernetes secret or empty map if there's nothing saved. */
  public Map<String, byte[]> getSecretData(String name) throws ApiException {
    CoreV1Api api = new CoreV1Api(client);
    try {
      V1Secret v1Secret = api.readNamespacedSecret(name, this.namespace, null);
      return v1Secret.getData();
    } catch (ApiException e) {
      if (e.getCode() == 404) {
        return Collections.emptyMap();
      } else {
        throw e;
      }
    }
  }

  /** Removes secret with given name if it exists. */
  public void removeSecretData(String name) throws ApiException {
    log.debug("Deleting k8s secret: {}", name);
    try {
      var status =
          new CoreV1Api(client)
              .deleteNamespacedSecret(name, this.namespace, null, null, null, null, null, null);
      log.debug("Deleted k8s secret: {}, status: {}", name, status);
    } catch (ApiException e) {
      if (e.getCode() == 404) {
        log.debug("Already deleted: k8s secret: {}");
      } else {
        log.error("Failed to remove K8S secret {}", name);
        throw e;
      }
    }
  }

  /**
   * Saves a secret data into a Kubernetes secret. It will overwrite previous content or create new
   * secret if it does not exists
   *
   * @param name the name of the secret. If the secret exists. It will be
   * @param data the map with secrets, can be empty but not NULL
   * @throws ApiException
   */
  public void saveSecretData(String name, Map<String, byte[]> data) throws ApiException {
    log.debug("Saving k8s secret:{}", name);
    V1Secret secret = buildV1Secret(name, data);
    CoreV1Api api = new CoreV1Api(client);

    V1Secret nsSecret;
    try {
      nsSecret = api.replaceNamespacedSecret(name, this.namespace, secret, null, null, null, null);
    } catch (ApiException e) {
      if (e.getCode() == 404) {
        log.debug("Secret {} does not exist. Creating ...", name);
        nsSecret = api.createNamespacedSecret(this.namespace, secret, null, null, null, null);
      } else {
        log.error("Failed to save k8s secret: {}", name);
        throw e;
      }
    }
    log.debug("Saved k8s secret: {}", name);
    logSecretDebugInformation(nsSecret);
  }

  /**
   * This method logs secret information for debugging purposes. While also omitting any sensitive
   * data. We don't want to throw any exceptions from this method, since it is only meant for
   * logging.
   *
   * @param nsSecret
   */
  private void logSecretDebugInformation(V1Secret nsSecret) {
    try {
      var dataKeys =
          Optional.ofNullable(nsSecret.getData()).map(secret -> secret.keySet()).orElse(null);
      var metaData =
          Optional.ofNullable(nsSecret.getMetadata()).map(secret -> secret.toString()).orElse(null);
      var stringDataKeys =
          Optional.ofNullable(nsSecret.getStringData()).map(secret -> secret.keySet()).orElse(null);
      log.debug(
          "Replaced namespaced secret. Data keys : {}, MetaData: {}, StringData keys: {}, Type: {},"
              + " ApiVer: {}",
          dataKeys,
          metaData,
          stringDataKeys,
          nsSecret.getType(),
          nsSecret.getApiVersion());
    } catch (Exception e) {
      log.debug("Could not log secret information due to: ", e);
    }
  }

  private V1Secret buildV1Secret(String name, Map<String, byte[]> data) {
    return new V1SecretBuilder()
        .withNewMetadata()
        .withName(name)
        .withNamespace(this.namespace)
        .endMetadata()
        .withData(data)
        .build();
  }


  /**
   * Default for testing purposes. This method returns the megabytes amount contained in a quantity.
   *
   * @param quantity the quantity to convert.
   * @return integer MB's in the quantity
   */
  static int convertMemoryToMBs(Quantity quantity) {
    var divider = BigInteger.valueOf(1024);
    if (quantity.getFormat().getBase() == 10) {
      divider = BigInteger.valueOf(1000);
    }
    return quantity.getNumber().toBigInteger().divide(divider.multiply(divider)).intValue();
  }

}
