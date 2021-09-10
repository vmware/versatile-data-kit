/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.discovery;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

public class ServiceLocationTest {

    @Test
    public void teamRootUriTest() {
        String expected = "http://localhost:8090";
        String actual = ServiceLocation.TEAM.rootUri;
        Assertions.assertEquals(expected, actual);
    }
}
