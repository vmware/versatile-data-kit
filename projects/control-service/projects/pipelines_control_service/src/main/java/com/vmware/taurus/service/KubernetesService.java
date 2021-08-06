/*
 * Copyright (c) 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service;


import com.google.common.base.Charsets;
import com.google.gson.JsonSyntaxException;
import com.google.gson.reflect.TypeToken;
import com.vmware.taurus.exception.KubernetesException;
import com.vmware.taurus.service.model.JobAnnotation;
import com.vmware.taurus.service.model.JobDeploymentStatus;
import com.vmware.taurus.service.model.JobLabel;
import com.vmware.taurus.service.threads.ThreadPoolConf;
import io.kubernetes.client.ApiClient;
import io.kubernetes.client.ApiException;
import io.kubernetes.client.Configuration;
import io.kubernetes.client.PodLogs;
import io.kubernetes.client.apis.*;
import io.kubernetes.client.custom.IntOrString;
import io.kubernetes.client.custom.Quantity;
import io.kubernetes.client.models.*;
import io.kubernetes.client.util.ClientBuilder;
import io.kubernetes.client.util.KubeConfig;
import io.kubernetes.client.util.Watch;
import io.kubernetes.client.util.Yaml;
import lombok.*;
import net.javacrumbs.shedlock.spring.annotation.EnableSchedulerLock;
import org.apache.commons.lang3.StringUtils;
import org.apache.commons.lang3.tuple.Pair;
import org.joda.time.DateTime;
import org.slf4j.Logger;
import org.springframework.beans.factory.InitializingBean;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.io.ClassPathResource;
import org.springframework.stereotype.Service;
import org.springframework.util.CollectionUtils;

import java.io.*;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.time.Instant;
import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.util.*;
import java.util.concurrent.TimeUnit;
import java.util.function.Consumer;
import java.util.stream.Collectors;

import static java.util.function.Predicate.not;


/**
 * A facade over Kubernetes (https://en.wikipedia.org/wiki/Facade_pattern) (not complete see JobImageDeployer)
 *
 * This way there's clear description on what parts of Kubernetes the app depends on.
 * Or changing underlying kubernetes client can be done with changes in a single place.
 *
 * TODO: Consider all methods to throw KubernetesException (instead of ApiException) because:
 *  * Better encapsulation
 *  * KubernetesException is more detailed and actually prints the cause.
 * TODO: automatically inject standard labels like OpID, Data Job Name, User.
 *
 * We are using sub-classes for different type of connections in order to make use of class-based auto-wiring in Spring.
 * @see com.vmware.taurus.service.kubernetes.ControlKubernetesService
 * @see com.vmware.taurus.service.kubernetes.DataJobsKubernetesService
 */
@Service
public abstract class KubernetesService implements InitializingBean {

    public static final String LABEL_PREFIX = "com.vmware.taurus";
    public static final String LATEST_VERSION_SUFFIX = "-latest";
    private static final int WATCH_JOBS_TIMEOUT_SECONDS = 300;
    private static final String K8S_DATA_JOB_TEMPLATE_RESOURCE ="k8s-data-job-template.yaml";

    private static int fromInteger(Integer value) {
        return Optional.ofNullable(value)
                .orElse(0);
    }

    private static long fromDateTime(DateTime value) {
        return Optional.ofNullable(value)
                .map(DateTime::getMillis)
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
            this(KubernetesService.fromInteger(status.getActive()),
                    KubernetesService.fromInteger(status.getFailed()),
                    KubernetesService.fromInteger(status.getSucceeded()),
                    KubernetesService.fromDateTime(status.getStartTime()),
                    KubernetesService.fromDateTime(status.getCompletionTime()));
        }
    }

    @Value
    @AllArgsConstructor
    public static class JobDetails {
        private final String name;
        private final JobStatus status;
        private final Map<String, String> labels;
        private final Map<String, String> annotations;

        JobDetails(V1Job job) {
           this.name = job.getMetadata().getName();
           this.status = new JobStatus(job.getStatus());
           this.labels = job.getMetadata().getLabels();
           this.annotations = job.getMetadata().getAnnotations();
        }
    }

    @Value
    @AllArgsConstructor
    public static class DeploymentStatus {
        private final int ready;
        private final int updated;
        private final int total;
        private final int available;
        private final int unavailable;

        DeploymentStatus(V1DeploymentStatus status) {
            this(KubernetesService.fromInteger(status.getReadyReplicas()),
                    KubernetesService.fromInteger(status.getUpdatedReplicas()),
                    KubernetesService.fromInteger(status.getReplicas()),
                    KubernetesService.fromInteger(status.getAvailableReplicas()),
                    KubernetesService.fromInteger(status.getUnavailableReplicas()));
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
        String terminationMessage;
        Status status;
        String opId;
        OffsetDateTime startTime;
        OffsetDateTime endTime;
        String jobVersion;
        String jobSchedule;
        Float resourcesCpuRequest;
        Float resourcesCpuLimit;
        Integer resourcesMemoryRequest;
        Integer resourcesMemoryLimit;
        OffsetDateTime deployedDate;
        String deployedBy;

        public enum Status {
            RUNNING, FAILED, FINISHED, SKIPPED
        }
    }

    @AllArgsConstructor
    private enum ContainerResourceType {
        CPU("cpu"),
        MEMORY("memory");

        @Getter
        private final String value;
    }

    @AllArgsConstructor
    public enum PodTerminationMessage {
        SUCCESS("Success"),
        PLATFORM_ERROR("Platform error"),
        USER_ERROR("User error"),
        SKIPPED("Skipped");

        @Getter
        private final String value;
    }

    // The 'Value' annotation from Lombok collides with the 'Value' annotation from Spring.
    @org.springframework.beans.factory.annotation.Value("${datajobs.control.k8s.data.job.template.file}")
    private String datajobTemplateFileLocation;

    private String namespace;
    private String kubeconfig;
    private Logger log;
    private ApiClient client;

    @Autowired
    private UserAgentService userAgentService;

    /**
     *
     * @param namespace the namespace where the kubernetes operation will act on. leave empty to infer from kubeconfig
     * @param kubeconfig The kubeconfig configuration of the Kubernetes cluster to connect to
     * @param log log to use - used in subclasses in order to set classname to subclass.
     */
    protected KubernetesService(String namespace, String kubeconfig, Logger log) {
        this.namespace = namespace;
        this.kubeconfig = kubeconfig;
        this.log = log;
    }

    @Override
    public void afterPropertiesSet() throws Exception {
        log.info("Configuration used: kubeconfig: {}, namespace: {}", kubeconfig, namespace);
        if (!StringUtils.isBlank(kubeconfig) && new File(kubeconfig).isFile()) {
            log.info("Will use provided kubeconfig file from configuration: {}", kubeconfig);
            KubeConfig kubeConfig = KubeConfig.loadKubeConfig(new FileReader(kubeconfig));
            client = ClientBuilder.kubeconfig(kubeConfig).build();
            if (StringUtils.isBlank(namespace)) {
                this.namespace = kubeConfig.getNamespace();
            }
        } else {
            log.info("Will use default client");
            client = ClientBuilder.defaultClient();
            if (StringUtils.isBlank(namespace)) {
                this.namespace = getCurrentNamespace();
            }
        }
        log.info("kubernetes namespace: {}", namespace);
        if (userAgentService != null) {
            client.setUserAgent(userAgentService.getUserAgent());
        }

        // Annoying error: Watch is incompatible with debugging mode active
        // client.setDebugging(true);
        client.getHttpClient().setReadTimeout(0, TimeUnit.SECONDS);

        // Step 1 - load the internal datajob template in order to validate it.
        try {
            loadCronjobTemplate(new ClassPathResource(K8S_DATA_JOB_TEMPLATE_RESOURCE).getFile());
            log.info("The internal datajob template is valid.");
        } catch(Exception e) {
            // Log the error and fail fast (cannot continue).
            log.error("Fatal error while loading the internal datajob template. Cannot continue", e);
            throw e;
        }
        // Step 2 - load the configurable datajob template in order to validate it
        // when environment variable 'K8S_DATA_JOB_TEMPLATE_FILE' is set.
        if(!StringUtils.isEmpty(datajobTemplateFileLocation)) {
            if(loadConfigurableCronjobTemplate() == null) {
                log.warn("The configurable datajob template '{}' could not be loaded.", datajobTemplateFileLocation);
            } else {
                log.info("The configurable datajob template '{}' is valid.", datajobTemplateFileLocation);
            }
        }
    }

    private V1beta1CronJob loadCronjobTemplate() {
        if(StringUtils.isEmpty(datajobTemplateFileLocation)) {
            log.debug("Datajob template file location is not set. Using internal datajob template.");
            return loadInternalCronjobTemplate();
        }
        V1beta1CronJob cronjobTemplate = loadConfigurableCronjobTemplate();
        if(cronjobTemplate == null) {
            return loadInternalCronjobTemplate();
        }

        return cronjobTemplate;
    }

    private V1beta1CronJob loadInternalCronjobTemplate() {
        try {
            return loadCronjobTemplate(new ClassPathResource(K8S_DATA_JOB_TEMPLATE_RESOURCE).getFile());
        } catch (Exception e) {
            // This should never happen unless we are testing locally and we've messed up
            // with the internal template resource file.
            throw new RuntimeException("Unrecoverable error while loading the internal datajob template. Cannot continue.", e);
        }
    }

    private V1beta1CronJob loadConfigurableCronjobTemplate() {
        // Check whether to use configurable datajob template at all.
        if(StringUtils.isEmpty(datajobTemplateFileLocation)) {
            log.debug("Datajob template file location is not set.");
            return null;
        }

        // Check whether the configurable datajob template file exists.
        File datajobTemplateFile = new File(datajobTemplateFileLocation);
        if(!datajobTemplateFile.isFile()) {
            log.warn("Datajob template location '{}' is not a file.", datajobTemplateFileLocation);
            return null;
        }

        try {
            // Load the configurable datajob template file.
            return loadCronjobTemplate(datajobTemplateFile);
        } catch (Exception e) {
            log.error("Error while loading the datajob template file.", e);
            return null;
        }
    }

    private V1beta1CronJob loadCronjobTemplate(File datajobTemplateFile) throws Exception {
        String cronjobTemplateString = Files.readString(datajobTemplateFile.toPath());
        // Check whether the string template is a valid datajob template.
        V1beta1CronJob cronjobTemplate = Yaml.loadAs(cronjobTemplateString, V1beta1CronJob.class);
        log.debug("Datajob template for file '{}': \n{}", datajobTemplateFile.getCanonicalPath(), cronjobTemplate);

        return cronjobTemplate;
    }

    private String getCurrentNamespace() {
        return getNamespaceFileContents().stream()
                .filter(not(String::isBlank))
                .findFirst()
                .map(String::strip)
                .orElse(null);
    }

    private List<String> getNamespaceFileContents () {
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

    public void createNamespace(String namespaceName) throws ApiException {
        var namesapceBody = new V1NamespaceBuilder()
              .withMetadata(
                    new V1ObjectMetaBuilder()
                          .withName(namespaceName)
                          .build())
              .build();

        new CoreV1Api(client).createNamespace(namesapceBody, null, null, null);
    }

    public void deleteNamespace(String namespaceName) throws ApiException {
        try {
            new CoreV1Api(client).deleteNamespace(namespaceName, null, null, null, null, null, null);
        }
        catch (JsonSyntaxException e) {
            if (e.getCause() instanceof IllegalStateException) {
                IllegalStateException ise = (IllegalStateException) e.getCause();
                if (ise.getMessage() != null && ise.getMessage().contains("Expected a string but was BEGIN_OBJECT"))
                    log.debug("Catching exception because of issue https://github.com/kubernetes-client/java/issues/86", e);
                else throw e;
            }
            else throw e;
        }
    }

    public Set<String> listJobs() throws ApiException {
        return listJobsDetails(Collections.emptyMap()).stream().map(j -> j.getName()).collect(Collectors.toSet());
    }

    /**
     * Return all jobs with passed labels
     * @param labelsToSelect labels to select jobs using equality based requirement -
     *                       https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/#equality-based-requirement
     * @throws ApiException
     */
    public Set<JobDetails> listJobsDetails(Map<String, String> labelsToSelect) throws ApiException {
        log.debug("Listing k8s jobs with labels {}", labelsToSelect);
        String labelSelector = buildLabelSelector(labelsToSelect);
        var jobs = new BatchV1Api(client).listNamespacedJob(namespace, null, null, null, labelSelector, null, null, null, null);
        var set = jobs.getItems().stream()
                .map(j -> new JobDetails(j))
                .collect(Collectors.toSet());
        log.debug("K8s jobs: {}", set);
        return set;
    }

    public Optional<JobDeploymentStatus> readCronJob(String cronJobName) {
        log.debug("Reading k8s cron job: {}", cronJobName);
        V1beta1CronJob cronJob = null;
        try {
            cronJob = new BatchV1beta1Api(client).readNamespacedCronJob(cronJobName, namespace, null, null, null);
        } catch (ApiException e) {
            log.warn("Could not read cron job: {}; reason: {}", cronJobName, new KubernetesException("", e).toString());
        }

        return mapCronJobToDeploymentStatus(cronJob, cronJobName);
    }

   /**
    * Fetch all deployment statuses from Kubernetes
    * @return List of {@link JobDeploymentStatus} or empty list if there is an error while fetching data
    */
   public List<JobDeploymentStatus> readJobDeploymentStatuses() {
      log.debug("Reading all k8s cron jobs");
      V1beta1CronJobList cronJobs = null;
      try {
         cronJobs = new BatchV1beta1Api(client).listNamespacedCronJob(namespace, null, null, null, null, null, null, null, null);
      } catch (ApiException e) {
         log.warn("Failed to read k8s cron jobs: ", e);
      }

      return cronJobs == null ? Collections.emptyList() : cronJobs.getItems().stream()
            .map(cronJob -> mapCronJobToDeploymentStatus(cronJob, null))
            .flatMap(Optional::stream)
            .collect(Collectors.toList());
   }

    public void startNewCronJobExecution(String cronJobName, String executionId, Map<String, String> annotations, Map<String, String> envs) throws ApiException {
        var cron = initBatchV1beta1Api().readNamespacedCronJob(cronJobName, namespace, null, null, null);

        Optional<V1beta1JobTemplateSpec> jobTemplateSpec = Optional.ofNullable(cron)
              .map(v1beta1CronJob -> v1beta1CronJob.getSpec())
              .map(v1beta1CronJobSpec -> v1beta1CronJobSpec.getJobTemplate());

        Map<String, String> jobLabels = jobTemplateSpec
              .map(v1beta1JobTemplateSpec -> v1beta1JobTemplateSpec.getMetadata())
              .map(v1ObjectMeta1 -> v1ObjectMeta1.getLabels())
              .orElse(Collections.emptyMap());

        Map<String, String> jobAnnotations = jobTemplateSpec
              .map(v1beta1JobTemplateSpec -> v1beta1JobTemplateSpec.getMetadata())
              .map(v1ObjectMeta -> v1ObjectMeta.getAnnotations())
              .map(v1ObjectMetaAnnotations -> {
                  v1ObjectMetaAnnotations.putAll(annotations);
                  return v1ObjectMetaAnnotations;
              })
              .orElse(annotations);

        V1JobSpec jobSpec = jobTemplateSpec
              .map(v1beta1JobTemplateSpec -> v1beta1JobTemplateSpec.getSpec())
              .orElseThrow(() -> new ApiException(String.format("K8S Cron Job '%s' does not exist or is not properly defined.", cronJobName)));

        V1Container v1Container = Optional.ofNullable(jobSpec.getTemplate())
              .map(v1PodTemplateSpec -> v1PodTemplateSpec.getSpec())
              .map(v1PodSpec -> v1PodSpec.getContainers())
              .map(v1Containers -> v1Containers.get(0))
              .orElseThrow(() -> new ApiException(String.format("K8S Cron Job '%s' is not properly defined.", cronJobName)));

        if (!CollectionUtils.isEmpty(envs)) {
            envs.forEach((name, value) -> v1Container.addEnvItem(new V1EnvVar().name(name).value(value)));
        }

        createNewJob(executionId, jobSpec, jobLabels, jobAnnotations);
    }

    public Set<String> listCronJobs() throws ApiException {
        log.debug("Listing k8s cron jobs");
        var cronJobs = new BatchV1beta1Api(client).listNamespacedCronJob(namespace, null, null, null, null, null, null, null, null);
        var set = cronJobs.getItems().stream()
              .map(j -> j.getMetadata().getName())
              .collect(Collectors.toSet());
        log.debug("K8s cron jobs: {}", set);
        return set;
    }

    public void createCronJob(String name, String image, Map<String, String> envs, String schedule,
                              boolean enable, List<String> args, Resources request, Resources limit,
                              V1Container jobContainer, V1Container initContainer,
                              List<V1Volume> volumes, Map<String, String> jobDeploymentAnnotations)
            throws ApiException {
        createCronJob(name, image, envs, schedule, enable, args, request, limit, jobContainer, initContainer,
                volumes, jobDeploymentAnnotations, Collections.emptyMap(), Collections.emptyMap(), Collections.emptyMap());
    }

    // TODO:  container/volume args are breaking a bit abstraction of KubernetesService by leaking impl. details
    public void createCronJob(String name, String image, Map<String, String> envs, String schedule,
                              boolean enable, List<String> args, Resources request, Resources limit,
                              V1Container jobContainer, V1Container initContainer,
                              List<V1Volume> volumes, Map<String, String> jobDeploymentAnnotations,
                              Map<String, String> jobPodLabels, Map<String, String> jobAnnotations, Map<String, String> jobLabels)
            throws ApiException {
        log.debug("Creating k8s cron job name:{}, image:{}", name, image);
        var cronJob = cronJobFromTemplate(name, schedule, !enable, jobContainer, initContainer,
                volumes, jobDeploymentAnnotations, jobPodLabels, jobAnnotations, jobLabels);
        V1beta1CronJob nsJob = new BatchV1beta1Api(client).createNamespacedCronJob(namespace, cronJob, null, null, null);
        log.debug("Created k8s cron job: {}", nsJob);
        log.debug("Created k8s cron job name: {}, uid:{}, link:{}", nsJob.getMetadata().getName(), nsJob.getMetadata().getUid(), nsJob.getMetadata().getSelfLink());
    }

    public void updateCronJob(String name, String image,  Map<String, String> envs, String schedule,
                              boolean enable, List<String> args, Resources request, Resources limit,
                              V1Container jobContainer, V1Container initContainer,
                              List<V1Volume> volumes, Map<String, String> jobDeploymentAnnotations)
            throws ApiException {
        updateCronJob(name, image, envs, schedule, enable, args, request, limit, jobContainer,
                initContainer, volumes, jobDeploymentAnnotations, Collections.emptyMap(), Collections.emptyMap(), Collections.emptyMap());
    }

    public void updateCronJob(String name, String image,  Map<String, String> envs, String schedule,
                              boolean enable, List<String> args, Resources request, Resources limit,
                              V1Container jobContainer, V1Container initContainer,
                              List<V1Volume> volumes, Map<String, String> jobDeploymentAnnotations,
                              Map<String, String> jobPodLabels, Map<String, String> jobAnnotations, Map<String, String> jobLabels)
            throws ApiException {
        var cronJob = cronJobFromTemplate(name, schedule, !enable, jobContainer, initContainer,
                volumes, jobDeploymentAnnotations, jobPodLabels, jobAnnotations, jobLabels);
        V1beta1CronJob nsJob = new BatchV1beta1Api(client).replaceNamespacedCronJob(name, namespace, cronJob, null, null, null);
        log.debug("Updated k8s cron job status for name:{}, image:{}, uid:{}, link:{}", name, image, nsJob.getMetadata().getUid(), nsJob.getMetadata().getSelfLink());
    }

    public void deleteCronJob(String name) throws ApiException {
        log.debug("Deleting k8s cron job: {}", name);
        try {
            new BatchV1beta1Api(client).deleteNamespacedCronJob(name, namespace, null, null, null, null, null, null);
        }
        catch (JsonSyntaxException e) {
            if (e.getCause() instanceof IllegalStateException) {
                IllegalStateException ise = (IllegalStateException) e.getCause();
                if (ise.getMessage() != null && ise.getMessage().contains("Expected a string but was BEGIN_OBJECT"))
                    log.debug("Catching exception because of issue https://github.com/kubernetes-client/java/issues/86", e);
                else throw e;
            }
            else throw e;
        }
        log.debug("Deleted k8s cron job: {}", name);
    }

    public void createJob(String name, String image, boolean privileged, Map<String, String> envs,
                          List<String> args, List<V1Volume> volumes, List<V1VolumeMount> volumeMounts,
                          String imagePullPolicy, Resources request, Resources limit)
          throws ApiException {
        log.debug("Creating k8s job name:{}, image:{}", name, image);
        var template = new V1PodTemplateSpecBuilder()
                .withSpec(new V1PodSpecBuilder()
                        .withRestartPolicy("Never")
                        .withContainers(container(name, image, privileged, envs, args, volumeMounts, imagePullPolicy, request, limit, null))
                        .withVolumes(volumes)
                        .build())
                .build();
        var spec = new V1JobSpecBuilder()
                .withBackoffLimit(3) //TODO configure
                .withTtlSecondsAfterFinished(3600)  //TODO configure
                .withTemplate(template)
                .build();
        createNewJob(name, spec, Collections.emptyMap(), Collections.emptyMap());
    }

    // Default for testing purposes
    void createNewJob(String name, V1JobSpec spec, Map<String, String> labels, Map<String, String> annotations) throws ApiException {
        var job = new V1JobBuilder()
                .withMetadata(new V1ObjectMetaBuilder()
                        .withName(name)
                        .addToLabels(labels)
                        .addToAnnotations(annotations)
                        .build())
                .withSpec(spec)
                .build();

        V1Job nsJob = new BatchV1Api(client).createNamespacedJob(namespace, job, null, null, null);
        log.debug("Created k8s job: {}", nsJob);
        log.debug("Created k8s job name: {}, uid:{}, link:{}", nsJob.getMetadata().getName(), nsJob.getMetadata().getUid(), nsJob.getMetadata().getSelfLink());
    }

    public Optional<V1Pod> getPod(String podName) throws ApiException {
        List<V1Pod> allPods = new CoreV1Api(client)
              .listNamespacedPod(namespace, "false", null, null, null, null, null, null, null)
              .getItems();

        return allPods.stream()
              .filter(pod -> pod.getMetadata().getName().startsWith(podName))
              .findFirst();
    }

    private List<V1Pod> listJobPods(V1Job job) throws ApiException {
        var labelsToSelect = Map.of("job-name", job.getMetadata().getName());
        log.debug("Getting pods with labels {}", labelsToSelect);
        String labelSelector = buildLabelSelector(labelsToSelect);
        var pods = new CoreV1Api(client).listNamespacedPod(namespace, null, null, null, labelSelector, null, null, null, null).getItems();
        log.trace("K8s pods with label selector {}: {}", labelSelector, pods);
        return pods;
    }

    public boolean isRunningJob(String dataJobName) throws ApiException {
        var labelsToSelect = Map.of(JobLabel.NAME.getValue(), dataJobName);
        String labelSelector = buildLabelSelector(labelsToSelect);
        V1JobList v1JobList = initBatchV1Api().listNamespacedJob(namespace, null, null, null, labelSelector, null, null, null, null);

        // In this case we use getConditions() instead of getActive()
        // because if the job is in init state the active flag is zero.
        // We want to track those jobs as submitted as well.
        // The getConditions() returns result only if the job is completed.
        return Optional.ofNullable(v1JobList)
              .map(v1JobList1 -> v1JobList1.getItems())
              .stream()
              .flatMap(v1Jobs -> v1Jobs.stream())
              .map(v1Job1 -> v1Job1.getStatus())
              .map(v1JobStatus -> v1JobStatus.getConditions())
              .anyMatch(v1JobConditions -> CollectionUtils.isEmpty(v1JobConditions));
    }

    public String getPodLogs(String podName) throws IOException, ApiException {
        log.debug("Get logs for pod {}", podName);
        Optional<V1Pod> pod = getPod(podName);

        String logs = "";
        if (pod.isPresent()) {
            PodLogs podLogs = new PodLogs(client);

            try (BufferedReader br = new BufferedReader(new InputStreamReader(podLogs.streamNamespacedPodLog(pod.get()), Charsets.UTF_8))) {
                // The builder logs are relatively small so we can afford to load it all in memory for easier processing.
                logs = br.lines().peek(s -> log.debug("[{}] {}", podName, s)).collect(Collectors.joining(System.lineSeparator()));
            }
        }
        return logs;
    }

    public JobStatusCondition watchJob(String jobName, int timeoutSeconds, Consumer<JobStatus> watcher) throws ApiException, IOException, InterruptedException {
        log.debug("Watch job {}; timeoutSeconds: {}", jobName, timeoutSeconds);
        JobStatusCondition condition = null;
        // we may have started watching too soon
        // TODO: set resourceVersion when watching to optimize waits or even avoid the loop here ?
        // https://kubernetes.io/docs/reference/using-api/api-concepts/#resource-versions
        // https://kubernetes.io/docs/reference/using-api/api-concepts/#efficient-detection-of-changes
        int counter =  timeoutSeconds;
        while (condition == null && --counter > 0) {
            Thread.sleep(1000);
            condition = watchJobInternal(jobName, timeoutSeconds, watcher);
        }
        if (condition == null) {
            condition = new JobStatusCondition(false, null, "Cannot determine job status", "", 0);
        }
        return condition;
    }

    // Default for testing purposes
    BatchV1Api initBatchV1Api() {
        return new BatchV1Api(client);
    }

    // Default for testing purposes
    BatchV1beta1Api initBatchV1beta1Api() {
        return new BatchV1beta1Api(client);
    }

    private JobStatusCondition watchJobInternal(String jobName, int timeoutSeconds, Consumer<JobStatus> watcher) throws IOException, ApiException {
        String fieldSelector = String.format("metadata.name=%s", jobName);
        try (Watch<V1Job> watch = Watch.createWatch(Configuration.getDefaultApiClient(),
                new BatchV1Api(client).listNamespacedJobCall(namespace, null, null, fieldSelector, null, null, null, timeoutSeconds, true, null, null),
                new TypeToken<Watch.Response<V1Job>>() {
                }.getType())) {
            for (var response : watch) {
                log.debug("watch k8s response type: {}", response.type);
                var job = response.object;

                var status = new JobStatus(job.getStatus());
                log.debug("watch k8s status: {}", status);
                watcher.accept(status);

                return getJobCondition(job);
            }
        } catch (RuntimeException e) {
            log.info("Could not get status of a job. " +
                    " Error was: " + e.getMessage(),
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
        return labels
                .entrySet().stream().map(e -> e.getKey() + "=" + e.getValue())
                .collect(Collectors.joining(","));
    }

    private static String getContainerName(V1Job job) {
        Objects.requireNonNull(job, "The job cannot be null");

        var containers = Optional.ofNullable(job.getSpec())
              .map(v1JobSpec -> v1JobSpec.getTemplate())
              .map(v1PodTemplateSpec -> v1PodTemplateSpec.getSpec())
              .map(v1PodSpec -> v1PodSpec.getContainers())
              .orElse(null);

        return (containers != null && !containers.isEmpty()) ? containers.get(0).getName() : null;
    }

    private static Optional<V1ContainerStateTerminated> getTerminatedState(V1Pod pod) {
        Objects.requireNonNull(pod, "The pod cannot be null");
        var status = pod.getStatus();
        if (status == null || status.getContainerStatuses() == null || status.getContainerStatuses().isEmpty()) {
            return Optional.empty();
        }
        final var containerStatus = status.getContainerStatuses().get(0);
        return getTerminatedState(containerStatus.getState())
                .or(() -> getTerminatedState(containerStatus.getLastState()));
    }

    private static Optional<V1ContainerStateTerminated> getTerminatedState(V1ContainerState state) {
        return (state == null || state.getTerminated() == null) ? Optional.empty() : Optional.ofNullable(state.getTerminated());
    }

    /**
     * Returns the termination status of the specified job by looking at its associated pods and
     * searching for the last terminated one.
     *
     * @param job The job whose status to return.
     * @return A {@link V1ContainerStateTerminated} object representing the termination status of the job.
     */
    Optional<V1ContainerStateTerminated> getTerminationStatus(V1Job job) {
        List<V1Pod> jobPods;

        try {
            jobPods = listJobPods(job);
        } catch (ApiException ex) {
            log.info("Could not list pods for job {}", job.getMetadata().getName(), ex);
            return Optional.empty();
        }

        var lastTerminatedPodState = jobPods.stream()
              .map(KubernetesService::getTerminatedState)
              .filter(Optional::isPresent)
              .map(Optional::get)
              .max(Comparator.comparing(V1ContainerStateTerminated::getFinishedAt));

        if (lastTerminatedPodState.isEmpty()) {
            log.info("Could not find a terminated pod for job {}", job.getMetadata().getName());
        }

        return lastTerminatedPodState;
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
            Optional<V1ContainerStateTerminated> lastTerminatedPodState = getTerminationStatus(job);
            // If the job completed but its pod did not produce a termination message, we treat this (for now)
            // as a Platform error. Possible reasons for this to happen are:
            //   - Pod was not created due to insufficient resources (in the future we'd likely want to create per-team
            //     resource pools + provide per-job resource configuration; then it would be the responsibility of the
            //     users to manage their resources, in which case this should be classified as user error).
            //   - Pod failed to pull one of its images
            //   - Pod was killed in flight due to exceeding its allowed memory (this should be eventually classified
            //     as user error)
            jobExecutionStatusBuilder.terminationMessage(
                  lastTerminatedPodState.map(v1ContainerStateTerminated -> StringUtils.trim(v1ContainerStateTerminated.getMessage()))
                        .orElse(PodTerminationMessage.PLATFORM_ERROR.getValue()));
        }
        // Job resources
        Optional<V1Container> containerOptional = Optional.ofNullable(job.getSpec())
              .map(V1JobSpec::getTemplate)
              .map(V1PodTemplateSpec::getSpec)
              .map(V1PodSpec::getContainers)
              .filter(v1Containers -> !CollectionUtils.isEmpty(v1Containers))
              .map(v1Containers -> v1Containers.get(0));

        Optional<Map<String, Quantity>> resourcesRequest = containerOptional
              .map(V1Container::getResources)
              .map(v1ResourceRequirements -> v1ResourceRequirements.getRequests());
        jobExecutionStatusBuilder.resourcesCpuRequest(
              resourcesRequest
                    .map(stringQuantityMap -> stringQuantityMap.get(ContainerResourceType.CPU.getValue()))
                    .map(Quantity::getNumber)
                    .map(Number::floatValue)
                    .orElse(null));
        jobExecutionStatusBuilder.resourcesMemoryRequest(
              resourcesRequest
                    .map(stringQuantityMap -> stringQuantityMap.get(ContainerResourceType.MEMORY.getValue()))
                    .map(quantity -> convertMemoryToMBs(quantity))
                    .orElse(null));

        Optional<Map<String, Quantity>> resourcesLimit = containerOptional
              .map(V1Container::getResources)
              .map(V1ResourceRequirements::getLimits);
        jobExecutionStatusBuilder.resourcesCpuLimit(
              resourcesLimit
                    .map(stringQuantityMap -> stringQuantityMap.get(ContainerResourceType.CPU.getValue()))
                    .map(Quantity::getNumber)
                    .map(Number::floatValue)
                    .orElse(null));
        jobExecutionStatusBuilder.resourcesMemoryLimit(
              resourcesLimit
                    .map(stringQuantityMap -> stringQuantityMap.get(ContainerResourceType.MEMORY.getValue()))
                    .map(quantity -> convertMemoryToMBs(quantity))
                    .orElse(null));

        // Job metadata
        Optional<V1ObjectMeta> metadata = Optional.ofNullable(job.getMetadata());

        jobExecutionStatusBuilder.executionId(
              metadata.map(V1ObjectMeta::getName)
                    .orElse(null));

        // Job labels
        Optional<Map<String, String>> labels = metadata.map(v1ObjectMeta -> v1ObjectMeta.getLabels());

        jobExecutionStatusBuilder.jobVersion(
              labels.map(stringStringMap -> stringStringMap.get(JobLabel.VERSION.getValue()))
                    .orElse(
                          containerOptional
                                .map(V1Container::getImage)
                                .map(imageStr -> imageStr.substring(imageStr.lastIndexOf(":") + 1))
                                .orElse(null)));

        jobExecutionStatusBuilder.jobName(
              labels.map(stringStringMap -> stringStringMap.get(JobLabel.NAME.getValue()))
                    .orElse(getContainerName(job)));

        // Job annotations
        Optional<Map<String, String>> annotations = metadata.map(V1ObjectMeta::getAnnotations);

        jobExecutionStatusBuilder.deployedDate(
              annotations.map(stringStringMap -> stringStringMap.get(JobAnnotation.DEPLOYED_DATE.getValue()))
                    .filter(lastDeployedDateStr -> StringUtils.isNotBlank(lastDeployedDateStr))
                    .map(lastDeployedDateStr -> OffsetDateTime.parse(lastDeployedDateStr))
                    .orElse(null));

        jobExecutionStatusBuilder.deployedBy(
              annotations.map(stringStringMap -> stringStringMap.get(JobAnnotation.DEPLOYED_BY.getValue()))
                    .orElse(null));

        jobExecutionStatusBuilder.executionType(
              annotations.map(stringStringMap -> stringStringMap.get(JobAnnotation.EXECUTION_TYPE.getValue()))
                    .orElse(null));

        jobExecutionStatusBuilder.opId(
              annotations.map(stringStringMap -> stringStringMap.get(JobAnnotation.OP_ID.getValue()))
                    .orElse(
                          metadata.map(V1ObjectMeta::getName)
                                .orElse(null)));

        jobExecutionStatusBuilder.jobSchedule(
              annotations.map(stringStringMap -> stringStringMap.get(JobAnnotation.SCHEDULE.getValue()))
                    .orElse(null));

        // Job status
        Optional<V1JobStatus> jobStatus = Optional.ofNullable(job.getStatus());

        jobExecutionStatusBuilder.startTime(
              jobStatus.map(V1JobStatus::getStartTime)
                    .map(startTime -> Instant.ofEpochMilli(startTime.getMillis()))
                    .map(startTimeInstant -> OffsetDateTime.ofInstant(startTimeInstant, ZoneOffset.UTC))
                    .orElse(null));

        jobExecutionStatusBuilder.endTime(
              Optional.ofNullable(jobStatusCondition)
                    .map(JobStatusCondition::getCompletionTime)
                    .map(endTime -> Instant.ofEpochMilli(endTime))
                    .map(endTimeInstant -> OffsetDateTime.ofInstant(endTimeInstant, ZoneOffset.UTC))
                    .orElse(null));

        // jobCondition = null means that the Data Job is still running
        jobExecutionStatusBuilder.status(
              Optional.ofNullable(jobStatusCondition)
                    .map(JobStatusCondition::isSuccess)
                    .map(success -> success ? JobExecution.Status.FINISHED : JobExecution.Status.FAILED)
                    .orElse(JobExecution.Status.RUNNING));

        return Optional.of(jobExecutionStatusBuilder.build());
    }

    /**
     * Initiates a watch for the jobs with labels specified by {@code labelsToWatch}. The watch will be active
     * for no longer than the number of seconds specified by {@code timeoutSeconds}. The specified watcher is
     * invoked whenever a job is completed and has an associated pod with a termination message.
     *
     * @param labelsToWatch      The labels for the jobs to watch, or null, to watch all jobs.
     * @param watcher            A {@link Consumer} to receive notifications about completed jobs.
     * @param lastWatchTime      The time of the last completed job watch, expressed in millis since Epoch.
     * @throws ApiException
     * @throws IOException
     */
    public void watchJobs(Map<String, String> labelsToWatch, Consumer<JobExecution> watcher, long lastWatchTime)
            throws IOException, ApiException {
        watchJobs(labelsToWatch, watcher, lastWatchTime, WATCH_JOBS_TIMEOUT_SECONDS);
    }

    /**
     * Initiates a watch for the jobs with labels specified by {@code labelsToWatch}. The watch will be active
     * for no longer than the number of seconds specified by {@code timeoutSeconds}. The specified watcher is
     * invoked whenever a job is completed and has an associated pod with a termination message.
     *
     * @param labelsToWatch      The labels for the jobs to watch, or null, to watch all jobs.
     * @param watcher            A {@link Consumer} to receive notifications about completed jobs.
     * @param lastWatchTime      The time of the last completed job watch, expressed in millis since Epoch.
     * @param timeoutSeconds     The maximum number of seconds that the watch should be active, or null,
     *                           to watch using the default timeout configured on the server (usually 5 minutes).
     *                           If this value is changed, the {@code defaultLockAtMostFor} value of the
     *                           {@link EnableSchedulerLock} annotation (see {@link ThreadPoolConf})
     *                           should be adjusted accordingly to ensure that the lock will be held long enough
     *                           for the watch to complete.
     * @throws ApiException
     * @throws IOException
     */
    public void watchJobs(Map<String, String> labelsToWatch, Consumer<JobExecution> watcher,
                          long lastWatchTime, Integer timeoutSeconds)
            throws ApiException, IOException {
        Objects.requireNonNull(watcher, "The watcher cannot be null");

        log.info("Start watching jobs with labels: {}", labelsToWatch);

        // Job change detection implementation:
        // https://kubernetes.io/docs/reference/using-api/api-concepts/#efficient-detection-of-changes
        String labelSelector = buildLabelSelector(labelsToWatch);
        String resourceVersion;
        try {
            var jobList = new BatchV1Api(client).listNamespacedJob(
                    namespace, "false", null, null, labelSelector, null, null, null, null);
            jobList.getItems().forEach(job -> {
                var condition = getJobCondition(job);
                if (condition != null && condition.getCompletionTime() > lastWatchTime) {
                    getJobExecutionStatus(job, condition).ifPresent(watcher);
                }
            });
            resourceVersion = jobList.getMetadata().getResourceVersion();
        } catch (ApiException ex) {
            log.info("Failed to list jobs for watching. Error was: {}", ex.getMessage());
            return;
        }

        try (Watch<V1Job> watch = Watch.createWatch(Configuration.getDefaultApiClient(),
                new BatchV1Api(client).listNamespacedJobCall(
                        namespace, null, null, null, labelSelector, null, resourceVersion, timeoutSeconds, true, null, null),
                new TypeToken<Watch.Response<V1Job>>() {
                }.getType())) {
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

                if (!"ADDED".equals(response.type) && !"DELETED".equals(response.type)) {
                    var condition = getJobCondition(job);
                    getJobExecutionStatus(job, condition).ifPresent(watcher);
                }
            }
        } catch (RuntimeException e) {
            log.info("Failed to watch jobs. Error was: {}", e.getMessage());
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
                log.trace("k8s job condition type: {} reason: {} message: {}", c.getType(), c.getReason(), c.getMessage());
                return new JobStatusCondition(c.getType().equals("Complete"), c.getType(), c.getReason(), c.getMessage(),
                        c.getLastTransitionTime() != null ? c.getLastTransitionTime().getMillis() : 0);
            }
        }
        return null;
    }

    public JobDetails readJob(String name) throws ApiException {
        log.debug("Reading k8s job for: {}", name);
        var job = new BatchV1Api(client).readNamespacedJob(name, namespace, null, null, null);

        log.debug("k8s job: {}", job);
        log.debug("k8s job status: {}", job.getStatus());
        log.debug("k8s job active {} success {} fail {}", job.getStatus().getActive(), job.getStatus().getSucceeded(), job.getStatus().getFailed());
        if (job.getStatus().getConditions() != null) {
            for (var c : job.getStatus().getConditions()) {
                log.debug("k8s job condition type: {} reason: {} message: {}", c.getType(), c.getReason(), c.getMessage());
            }
        }
        log.debug("Returning k8s job status for:{} status:{}", name, job.getStatus());
        return new JobDetails(job);
    }

    /**
     * Deletes a Job in kubernets with given name if it exists.
     * @param name the name of the job
     * @throws ApiException
     */
    public void deleteJob(String name) throws ApiException {
        log.debug("Deleting k8s job: {}", name);
        try {
            var status = new BatchV1Api(client).deleteNamespacedJob(name, namespace, null, null, null, null, null, null);
            log.debug("Deleted k8s job: {}, status: {}", name, status);
        } catch (JsonSyntaxException e) {
            log.warn("Ignoring JsonSyntaxException during deleteNamespacedJob {}. Reason: {}", name, e.getMessage());
        } catch (ApiException e) {
            if (e.getCode() == 404) {
                log.debug("Job {} already deleted or does not exists", name);
            } else {
                throw e;
            }
        }
        log.debug("Deleting k8s pods for job: {}", name);
        var status = new CoreV1Api(client).deleteCollectionNamespacedPod(namespace, null, null, null, "job-name=" + name, null, null, null, null);
        log.debug("Deleted k8s pods for job: {}, status: {}", name, status);
    }


    public Set<String> listDeployments() throws ApiException {
        log.debug("Listing k8s deployments");
        var deps = new AppsV1Api(client).listNamespacedDeployment(namespace, null, null, null, null, null, null, null, null);
        var set = deps.getItems().stream()
                .map(j -> j.getMetadata().getName())
                .collect(Collectors.toSet());
        log.debug("K8s deployments: {}", set);
        return set;
    }

    public void createDeployment(String name, String image, int replicas,
                                 Map<String, String> envs, Map<String, String> labels,
                                 Resources request, Resources limit, Probe probe) throws ApiException {
        log.debug("Creating k8s deployment :{}, image:{}", name, image);
        var deployment = deployment(name, image, replicas, envs, labels, request, limit, probe);
        V1Deployment nsdDeployment = new AppsV1Api(client).createNamespacedDeployment(namespace, deployment, null, null, null);
        log.debug("Created k8s deployment :{}, image:{}, uid:{}, link:{}", name, image, nsdDeployment.getMetadata().getUid(), nsdDeployment.getMetadata().getSelfLink());
    }

    public DeploymentStatus readDeploymentStatus(String name) throws ApiException {
        log.debug("Reading k8s deployment status for name:{}", name);
        var deployment = new AppsV1Api(client).readNamespacedDeploymentStatus(name, namespace, null);
        log.debug("Returning k8s deployment status for:{} status:{}", name, deployment.getStatus());
        return new DeploymentStatus(deployment.getStatus());
    }

    public void updateDeployment(String name, String image, int replicas,
                                 Map<String, String> envs, Map<String, String> labels,
                                 Resources request, Resources limit, Probe probe) throws ApiException {
        log.debug("Updating k8s deployment status for name:{}, image:{}", name, image);
        var deployment = deployment(name, image, replicas, envs, labels, request, limit, probe);
        V1Deployment v1Deployment = new AppsV1Api(client).replaceNamespacedDeployment(name, namespace, deployment, null, null, null);
        log.debug("Updated k8s deployment status for name:{}, image:{}, uid:{}, link:{}", name, image, v1Deployment.getMetadata().getUid(), v1Deployment.getMetadata().getSelfLink());
    }

    public int deleteDeployment(String name) throws ApiException {
        log.debug("Deleting k8s deployment:{}", name);
        var status = new AppsV1Api(client).deleteNamespacedDeployment(name, namespace, null, null, null, null, null, null);
        log.debug("Deleted k8s deployment:{}, status code:{}", name, status.getCode());
        return status.getCode();
    }

    public static V1Volume volume(String name) {
        return new V1VolumeBuilder()
                .withName(name)
                .withEmptyDir(new V1EmptyDirVolumeSource())
                .build();
    }

    public static V1Volume volume(String name, String secretName) {
        return new V1VolumeBuilder()
              .withName(name)
              .withSecret(new V1SecretVolumeSourceBuilder()
                    .withSecretName(secretName)
                    .build())
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
            var jobs = new BatchV1Api(client).listNamespacedJob(namespace, null, null, fieldSelector, null, null, null, null, null);
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

    private static V1Deployment deployment(String name, String image, int replicas,
                                           Map<String, String> envs, Map<String, String> labels,
                                           Resources request, Resources limit, Probe probe) {
        var selector = new V1LabelSelectorBuilder()
                .withMatchLabels(labels)
                .build();
        var template = new V1PodTemplateSpecBuilder()
                .withMetadata(new V1ObjectMetaBuilder()
                        .withLabels(labels)
                        .build())
                .withSpec(new V1PodSpecBuilder()
                        .withContainers(container(name, image, envs, List.of(), request, limit, probe))
                        .build())
                .build();
        var spec = new V1DeploymentSpecBuilder()
                .withSelector(selector)
                .withReplicas(replicas)
                .withTemplate(template)
                .build();
        return new V1DeploymentBuilder()
                .withMetadata(new V1ObjectMetaBuilder()
                        .withName(name)
                        .withLabels(labels)
                        .build())
                .withSpec(spec)
                .build();
    }

    // TODO - in the future we want to merge the (1) configurable datajob template
    //        with the (2) default internal datajob template when something from (1)
    //        is missing. For now we just check for missing entries in (1) and overwrite
    //        them with the corresponding entries in (2).
    private void checkForMissingEntries(V1beta1CronJob cronjob) {
        V1beta1CronJob internalCronjobTemplate = loadInternalCronjobTemplate();
        if(cronjob.getMetadata() == null) {
            cronjob.setMetadata(internalCronjobTemplate.getMetadata());
        }
        V1ObjectMeta metadata = cronjob.getMetadata();
        if(metadata.getAnnotations() == null) {
            metadata.setAnnotations(new HashMap<>());
        }
        if(cronjob.getSpec() == null) {
            cronjob.setSpec(internalCronjobTemplate.getSpec());
        }
        V1beta1CronJobSpec spec = cronjob.getSpec();
        if(spec.getJobTemplate() == null) {
            spec.setJobTemplate(internalCronjobTemplate.getSpec().getJobTemplate());
        }
        if(spec.getJobTemplate().getMetadata() == null){
            spec.getJobTemplate().setMetadata(internalCronjobTemplate.getSpec().getJobTemplate().getMetadata());
        }
        if(spec.getJobTemplate().getMetadata().getLabels() == null){
            spec.getJobTemplate().getMetadata().setLabels(new HashMap<>());
        }
        if(spec.getJobTemplate().getMetadata().getAnnotations() == null){
            spec.getJobTemplate().getMetadata().setAnnotations(new HashMap<>());
        }
        if(spec.getJobTemplate().getSpec() == null) {
            spec.getJobTemplate().setSpec(internalCronjobTemplate.getSpec().getJobTemplate().getSpec());
        }
        if(spec.getJobTemplate().getSpec().getTemplate() == null) {
            spec.getJobTemplate().getSpec().setTemplate(
                    internalCronjobTemplate.getSpec().getJobTemplate().getSpec().getTemplate());
        }
        if(spec.getJobTemplate().getSpec().getTemplate().getSpec() == null) {
            spec.getJobTemplate().getSpec().getTemplate().setSpec(
                    internalCronjobTemplate.getSpec().getJobTemplate().getSpec().getTemplate().getSpec());
        }
        if(spec.getJobTemplate().getSpec().getTemplate().getMetadata() == null) {
            spec.getJobTemplate().getSpec().getTemplate().setMetadata(
                    internalCronjobTemplate.getSpec().getJobTemplate().getSpec().getTemplate().getMetadata());
        }
        if(spec.getJobTemplate().getSpec().getTemplate().getMetadata().getLabels() == null) {
            spec.getJobTemplate().getSpec().getTemplate().getMetadata().setLabels(new HashMap<>());
        }
    }

    private V1beta1CronJob cronJobFromTemplate(String name, String schedule, boolean suspend, V1Container jobContainer,
                                   V1Container initContainer, List<V1Volume> volumes,
                                   Map<String, String> jobDeploymentAnnotations,
                                   Map<String, String> jobPodLabels,
                                   Map<String, String> jobAnnotations,
                                   Map<String, String> jobLabels) {
        V1beta1CronJob cronjob = loadCronjobTemplate();
        checkForMissingEntries(cronjob);
        cronjob.getMetadata().setName(name);
        cronjob.getSpec().setSchedule(schedule);
        cronjob.getSpec().setSuspend(suspend);
        cronjob.getSpec().getJobTemplate().getSpec().getTemplate().getSpec().setContainers(Collections.singletonList(jobContainer));
        cronjob.getSpec().getJobTemplate().getSpec().getTemplate().getSpec().setInitContainers(Collections.singletonList(initContainer));
        cronjob.getSpec().getJobTemplate().getSpec().getTemplate().getSpec().setVolumes(volumes);
        // Merge the annotations and the labels.
        cronjob.getMetadata().getAnnotations().putAll(jobDeploymentAnnotations);
        cronjob.getSpec().getJobTemplate().getSpec().getTemplate().getMetadata().getLabels().putAll(jobPodLabels);

        cronjob.getSpec().getJobTemplate().getMetadata().getAnnotations().putAll(jobAnnotations);
        cronjob.getSpec().getJobTemplate().getMetadata().getLabels().putAll(jobLabels);

        return cronjob;
    }

    private static V1Container container(String name, String image, Map<String, String> envs, List<String> args,
                                         Resources request, Resources limit, Probe probe) {
        return container(name, image, false, envs, args, Collections.emptyList(), "IfNotPresent", request, limit, probe);
    }

    private static V1Container container(String name, String image, boolean privileged, Map<String, String> envs,
                                         List<String> args, List<V1VolumeMount> volumeMounts, String imagePullPolicy,
                                         Resources request, Resources limit, Probe probe) {
        return container(name, image, privileged, envs, args, volumeMounts, imagePullPolicy, request, limit, probe, List.of());
    }


    public static V1Container container(String name, String image, boolean privileged, Map<String, String> envs,
                                        List<String> args, List<V1VolumeMount> volumeMounts, String imagePullPolicy,
                                        Resources request, Resources limit, Probe probe, List commands) {
        var builder = new V1ContainerBuilder()
                .withName(name)
                .withImage(image)
                .withVolumeMounts(volumeMounts)
                .withImagePullPolicy(imagePullPolicy)
                .withSecurityContext(new V1SecurityContextBuilder()
                        .withPrivileged(privileged)
                        .build())
                .withResources(new V1ResourceRequirementsBuilder()
                        .withRequests(resources(request))
                        .withLimits(resources(limit))
                        .build())
                .withEnv(envs.entrySet().stream()
                        .map(KubernetesService::envVar)
                        .collect(Collectors.toList()))
                .withArgs(args)
                .withCommand(commands);

        if (probe != null) {
            builder.withLivenessProbe(new V1ProbeBuilder()
                    .withHttpGet(new V1HTTPGetActionBuilder()
                            .withPort(new IntOrString(probe.port))
                            .withPath(probe.path)
                            .build())
                    .withInitialDelaySeconds(probe.period)
                    .withPeriodSeconds(probe.period)
                    .build());
        }

        return builder.build();
    }

    private static Map<String, Quantity> resources(Resources resources) {
        return Map.of("cpu", Quantity.fromString(resources.getCpu()),
                "memory", Quantity.fromString(resources.getMemory()));
    }

    private static V1EnvVar envVar(Map.Entry<String, String> entry) {
        var b = new V1EnvVarBuilder()
                .withName(entry.getKey());
        if (entry.getValue().startsWith("$")) {
            b.withValueFrom(new V1EnvVarSourceBuilder()
                    .withFieldRef(new V1ObjectFieldSelectorBuilder()
                            .withFieldPath(entry.getValue().substring(1))
                            .build())
                    .build());
        } else {
            b.withValue(entry.getValue());
        }
        return b.build();
    }

    /**
     * Get secret data from kubernetes secret or empty map if there's nothing saved.
     */
    public Map<String, byte[]> getSecretData(String name) throws ApiException {
        CoreV1Api api = new CoreV1Api(client);
        try {
            V1Secret v1Secret = api.readNamespacedSecret(name, this.namespace, null, null, null);
            return v1Secret.getData();
        } catch (ApiException e) {
            if (e.getCode() == 404) {
                return Collections.emptyMap();
            } else {
                throw e;
            }
        }

    }

    /**
     * Removes secrete with given name if it exists.
     */
    public void removeSecretData(String name) throws ApiException {
        log.debug("Deleting k8s secret: {}", name);
        try {
            var status = new CoreV1Api(client).deleteNamespacedSecret(name, this.namespace, null, null, null, null, null, null);
            log.debug("Deleted k8s secret: {}, status: {}", name, status);
        } catch (ApiException e) {
            if (e.getCode() == 404) {
                log.debug("Already deleted: k8s secret: {}");
            } else {
                throw e;
            }
        }
    }

    /**
     * Saves a secret data into a Kubernetes secret.
     * It will overwrite previous content or create new secret if it does not exists
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
            nsSecret = api.replaceNamespacedSecret(name, this.namespace, secret, null, null, null);
        } catch (ApiException e) {
            if (e.getCode() == 404) {
                log.debug("Secret {} does not exits. Creating ...");
                nsSecret = api.createNamespacedSecret(this.namespace, secret, null, null, null);
            } else {
                throw e;
            }
        }
        log.debug("Saved k8s secret: {}", name);
    }

    private V1Secret buildV1Secret(String name, Map<String, byte[]> data) {
        return new V1SecretBuilder()
                    .withNewMetadata()
                    .withName(name)
                    .withNamespace(this.namespace)
                    .endMetadata()
                    .withData(data).build();
    }

   private Optional<JobDeploymentStatus> mapCronJobToDeploymentStatus(V1beta1CronJob cronJob, String cronJobName) {
      JobDeploymentStatus deployment = null;
      if (cronJob != null) {
         deployment = new JobDeploymentStatus();
         deployment.setEnabled(!cronJob.getSpec().isSuspend());
         deployment.setDataJobName(StringUtils.removeEnd(cronJob.getMetadata().getName(), LATEST_VERSION_SUFFIX));
         deployment.setMode("release"); // TODO: Get from cron job config when we support testing environments
         deployment.setCronJobName(cronJobName == null ? cronJob.getMetadata().getName() : cronJobName);

         if (cronJob.getMetadata() != null && cronJob.getMetadata().getAnnotations() != null) {
            deployment.setLastDeployedBy(cronJob.getMetadata().getAnnotations().get("lastDeployedBy"));
            deployment.setLastDeployedDate(cronJob.getMetadata().getAnnotations().get("lastDeployedDate"));
         } else {
            deployment.setLastDeployedBy("noDataAvailable");
            deployment.setLastDeployedDate("noDataAvailable");
         }

         List<V1Container> containers = cronJob.getSpec().getJobTemplate().getSpec().getTemplate().getSpec().getContainers();
         if (!containers.isEmpty()) {
            String image = containers.get(0).getImage(); // TODO: Have 2 containers. 1 for VDK and 1 for the job.
            deployment.setImageName(image); // TODO do we really need to return image_name?
            String tag = image.split(":")[1];
            deployment.setGitCommitSha(tag);
         }
      }

      return Optional.ofNullable(deployment);
   }

    private static int convertMemoryToMBs(Quantity quantity) {
        long divider = 1024;

        if (quantity.getFormat().getBase() == 10) {
            divider = 1000;
        }

        return (int) (quantity.getNumber().intValue() / (divider * divider));
    }
}
