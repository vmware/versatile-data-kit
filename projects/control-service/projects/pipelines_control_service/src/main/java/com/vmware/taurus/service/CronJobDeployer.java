package com.vmware.taurus.service;

import io.kubernetes.client.openapi.ApiException;
import io.kubernetes.client.openapi.models.V1Container;
import io.kubernetes.client.openapi.models.V1Volume;

import java.util.List;
import java.util.Map;


/**
 * At the moment we support deploying 2 different versions of kubernetes cronjobs; v1 and v1Beta1.
 * This interface abstracts out the differences and at runtime only a single cronjobdeployer will we wired into the spring env depending on if cronjobv1 is supported or not
 *
 */

public interface CronJobDeployer {

    void create(
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
            throws ApiException;

    void update(
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
            throws ApiException;
}
