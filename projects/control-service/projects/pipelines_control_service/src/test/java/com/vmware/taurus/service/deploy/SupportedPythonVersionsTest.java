/*
 * Copyright 2023-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.deploy;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.test.util.ReflectionTestUtils;

import java.util.HashMap;

@ExtendWith(MockitoExtension.class)
public class SupportedPythonVersionsTest {
    private static final String VDK_IMAGE = "vdkImage";
    private static final String BASE_IMAGE = "baseImage";


    @InjectMocks private SupportedPythonVersions supportedPythonVersions;

    @BeforeEach
    public void setUp() {
        ReflectionTestUtils.setField(supportedPythonVersions, "vdkImage", "test-vdk-image");
        ReflectionTestUtils.setField(supportedPythonVersions, "deploymentDataJobBaseImage", "python:3.7-slim");
    }

    @Test
    public void isPythonVersionSupported_noSupportedVersions() {
        ReflectionTestUtils.setField(supportedPythonVersions, "supportedPythonVersions", new HashMap<>());

        Assertions.assertFalse(supportedPythonVersions.isPythonVersionSupported("3.7"));
    }

    @Test
    public void isPythonVersionSupported_versionSupported() {
        var supportedVersions = new HashMap<String, HashMap<String, String>>();
        supportedVersions.put("3.7", new HashMap<String, String>(){
            {
                put(BASE_IMAGE, "python:3.7-slim");
                put(VDK_IMAGE, "test_vdk_image");
            }
        });

        ReflectionTestUtils.setField(supportedPythonVersions, "supportedPythonVersions", supportedVersions);

        Assertions.assertTrue(supportedPythonVersions.isPythonVersionSupported("3.7"));
    }

    @Test
    public void isPythonVersionSupported_versionNotInSupported() {
        var supportedVersions = new HashMap<String, HashMap<String, String>>();
        supportedVersions.put("3.8", new HashMap<String, String>(){
            {
                put(BASE_IMAGE, "python:3.8-slim");
                put(VDK_IMAGE, "test_vdk_image");
            }
        });

        ReflectionTestUtils.setField(supportedPythonVersions, "supportedPythonVersions", supportedVersions);

        Assertions.assertFalse(supportedPythonVersions.isPythonVersionSupported("3.7"));
    }

    @Test
    public void getSupportedPythonVersions_multipleSupportedVersions() {
        var supportedVersions = generateSupportedPythonVersionsConf();

        final String resultStr = "[3.7, 3.8, 3.9]";

        ReflectionTestUtils.setField(supportedPythonVersions, "supportedPythonVersions", supportedVersions);

        Assertions.assertEquals(resultStr, supportedPythonVersions.getSupportedPythonVersions());
    }

    @Test
    public void getSupportedPythonVersions_getDefaultVersion() {
        ReflectionTestUtils.setField(supportedPythonVersions, "supportedPythonVersions", new HashMap<>());
        final String resultStr = "[3.7]";

        Assertions.assertEquals(resultStr, supportedPythonVersions.getSupportedPythonVersions());
    }

    @Test
    public void getJobBaseImage_defaultImage() {
        ReflectionTestUtils.setField(supportedPythonVersions, "supportedPythonVersions", new HashMap<>());
        final String defaultBaseImage = "python:3.7-slim";

        Assertions.assertEquals(defaultBaseImage, supportedPythonVersions.getJobBaseImage("3.8"));
    }

    @Test
    public void getJobBaseImage_multipleSupportedVersions() {
        var supportedVersions = generateSupportedPythonVersionsConf();

        final String resultBaseImg = "python:3.8-slim";
        ReflectionTestUtils.setField(supportedPythonVersions, "supportedPythonVersions", supportedVersions);

        Assertions.assertEquals(resultBaseImg, supportedPythonVersions.getJobBaseImage("3.8"));
    }

    @Test
    public void getVdkImage_defaultImage() {
        ReflectionTestUtils.setField(supportedPythonVersions, "supportedPythonVersions", new HashMap<>());
        final String defaultVdkImage = "test-vdk-image";

        Assertions.assertEquals(defaultVdkImage, supportedPythonVersions.getVdkImage("3.8"));
    }

    @Test
    public void getVdkImage_multipleSupportedVersions() {
        var supportedVersions = generateSupportedPythonVersionsConf();

        final String resultVdkImg = "test_vdk_image_3.8";
        ReflectionTestUtils.setField(supportedPythonVersions, "supportedPythonVersions", supportedVersions);

        Assertions.assertEquals(resultVdkImg, supportedPythonVersions.getVdkImage("3.8"));
    }

    private static HashMap<String, HashMap<String, String>> generateSupportedPythonVersionsConf() {
        var supportedVersions = new HashMap<String, HashMap<String, String>>();
        supportedVersions.put("3.7", new HashMap<String, String>(){
            {
                put(BASE_IMAGE, "python:3.7-slim");
                put(VDK_IMAGE, "test_vdk_image_3.7");
            }
        });
        supportedVersions.put("3.8", new HashMap<String, String>(){
            {
                put(BASE_IMAGE, "python:3.8-slim");
                put(VDK_IMAGE, "test_vdk_image_3.8");
            }
        });
        supportedVersions.put("3.9", new HashMap<String, String>(){
            {
                put(BASE_IMAGE, "python:3.9-slim");
                put(VDK_IMAGE, "test_vdk_image_3.9");
            }
        });

        return supportedVersions;
    }
}
