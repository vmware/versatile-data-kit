/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.monitoring;

import io.micrometer.core.instrument.Gauge;
import io.micrometer.core.instrument.Tags;

public class MonitoringUtil {

    public static boolean isGaugeChanged(final Gauge gauge, final Tags newTags) {
        if (gauge == null) {
            return false;
        }

        var existingTags = gauge.getId().getTags();
        return !newTags.stream().allMatch(existingTags::contains);
    }

}
