/*
 * Copyright 2023-2024 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.gpu.jpa;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface NodeWithGPURepo extends JpaRepository<NodeWithGPUs, String> {

    @Query("SELECT n FROM NodeWithGPUs n LEFT JOIN n.gpuConsumingJobs g " +
            "GROUP BY n HAVING n.deviceCount >=  :additionalResources+COALESCE(SUM(g.consumedResources), 0) " +
            "ORDER BY n.deviceCount - :additionalResources+COALESCE(SUM(g.consumedResources), 0) ")
    List<NodeWithGPUs> findNodesWithAvailableGPUs(@Param("additionalResources") double additionalResources);

}
