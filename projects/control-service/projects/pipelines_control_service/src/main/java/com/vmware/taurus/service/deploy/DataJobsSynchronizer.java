/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.deploy;

import com.vmware.taurus.service.kubernetes.DataJobsKubernetesService;
import com.vmware.taurus.service.model.DataJob;
import com.vmware.taurus.service.model.DataJobDeployment_;
import com.vmware.taurus.service.model.DataJob_;
import com.vmware.taurus.service.repository.JobsRepository;
import io.kubernetes.client.openapi.ApiException;
import org.apache.commons.lang3.StringUtils;
import org.springframework.data.domain.Sort;
import org.springframework.scheduling.concurrent.ThreadPoolTaskExecutor;
import org.springframework.stereotype.Component;

import java.util.Set;

/**
 * This class represents a utility for synchronizing Kubernetes CronJobs with data
 * from a database to maintain the desired state in the cluster.
 * <p>
 * It provides methods to retrieve job information from a database, compare it with
 * the current state of Kubernetes Jobs, and take actions to synchronize them. This
 * can include creating new CronJobs, updating existing CronJobs, etc.
 * <p>
 * Usage:
 * - Create an instance of this class and call the `synchronizeDataJobs` method
 *   to initiate the synchronization process.
 */
@Component
public class DataJobsSynchronizer {

    private final JobsRepository jobsRepository;

    private final DeploymentServiceV2 deploymentService;

    private final DataJobsKubernetesService dataJobsKubernetesService;

    public DataJobsSynchronizer(JobsRepository jobsRepository, DeploymentServiceV2 deploymentService, DataJobsKubernetesService dataJobsKubernetesService) {
        this.jobsRepository = jobsRepository;
        this.deploymentService = deploymentService;
        this.dataJobsKubernetesService = dataJobsKubernetesService;
    }

    /**
     * Synchronizes Kubernetes CronJobs from the database to ensure that the cluster's state
     * matches the desired state defined in the database records.
     * <p>
     * This method retrieves job information from the database, compares it with the current
     * state of Kubernetes CronJobs in the cluster, and takes the necessary actions to synchronize
     * them. This can include creating new CronJobs, updating existing CronJobs, etc.
     *
     * @throws ApiException
     */
    public void synchronizeDataJobs() throws ApiException {
        ThreadPoolTaskExecutor taskExecutor = initializeTaskExecutor();
        Set<String> cronJobs = dataJobsKubernetesService.listCronJobs();

        jobsRepository.findAll(Sort.by(Sort.Direction.ASC, DataJob_.DATA_JOB_DEPLOYMENT + "." + DataJobDeployment_.DEPLOYMENT_VERSION_SHA))
                .forEach(dataJob -> taskExecutor.execute(() -> synchronizeDataJob(dataJob, cronJobs)));

        taskExecutor.shutdown();
    }

    // Default for testing purposes
    void synchronizeDataJob(DataJob dataJob, Set<String> cronJobs) {
        if (dataJob.getDataJobDeployment() != null) {
            // Sends notification only when the deployment is initiated by the user.
            boolean sendNotification = StringUtils.isEmpty(dataJob.getDataJobDeployment().getDeploymentVersionSha());
            deploymentService.updateDeployment(dataJob, sendNotification, cronJobs);
        }
    }

    private ThreadPoolTaskExecutor initializeTaskExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(5);
        executor.setMaxPoolSize(10);
        executor.setQueueCapacity(Integer.MAX_VALUE);
        executor.setAllowCoreThreadTimeOut(true);
        executor.setKeepAliveSeconds(120);
        executor.setWaitForTasksToCompleteOnShutdown(true);
        executor.initialize();

        return executor;
    }
}
