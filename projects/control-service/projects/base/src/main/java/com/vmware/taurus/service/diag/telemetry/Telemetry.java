/*
 * Copyright (c) 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.diag.telemetry;

//import com.vmware.ph.client.api.PhClient;
//import com.vmware.ph.client.api.commondataformat.dimensions.Collector;
//import com.vmware.ph.client.api.exceptions.PhClientConnectionException;
//import com.vmware.ph.client.api.impl.PhClientBuilder;
//import com.vmware.ph.client.common.UrlFactory;
//import com.vmware.ph.upload.service.UploadServiceBuilder;
import com.vmware.taurus.base.EnableComponents;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.beans.factory.config.ConfigurableBeanFactory;
import org.springframework.context.annotation.Scope;
import org.springframework.stereotype.Component;

import java.io.IOException;
import java.net.InetAddress;
import java.net.UnknownHostException;
import java.nio.charset.StandardCharsets;
import java.util.UUID;

@Component
@Scope(value = ConfigurableBeanFactory.SCOPE_SINGLETON)
@org.springframework.boot.autoconfigure.condition.ConditionalOnProperty(value = EnableComponents.DIAGNOSTICS, havingValue = "true", matchIfMissing = true)
public class Telemetry implements ITelemetry {
    private static final Logger log = LoggerFactory.getLogger(Telemetry.class);

    public Telemetry() {
        String instance;
        try {
            instance = InetAddress.getLocalHost().toString();
        } catch (UnknownHostException e) {
            instance = "" + System.currentTimeMillis() + " " + e;
        }
        this.instanceId = instance;
    }

    private final String instanceId;

    @Value("${telemetry.ph.collector:taurus.v0")
    private final String collectorId = "taurus.v0";

    @Value("${telemetry.ph.environment:testing")
    private final String environment = "testing";

    //private PhClient phClient = null;

    //public PhClient getClient() {
    //    synchronized (this) {
    //        if (null == phClient) {
    //            var env = UploadServiceBuilder.Environment.valueOf(this.environment.toUpperCase());
    //            log.info("Telemetry with instanceId {} will be sent to {}", instanceId, env);
    //            this.phClient = PhClientBuilder.create(env, new Collector(collectorId, instanceId)).build();
    //        }
    //    }
    //    return phClient;
    //}

    @Override
    public void sendAsync(String payload) {
        //try {
        //    getClient().upload(collectorId, instanceId, UUID.randomUUID().toString(), UrlFactory.fromByteArray(payload.getBytes(StandardCharsets.UTF_8)));
        //} catch (IOException | PhClientConnectionException e) {
        //    // PhClient doesn't actually throws those exception as communication is asynchronous.
        //    log.error("Unexpected error while scheduling telemetry", e);
        //}
    }

}
