/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.deploy;

import com.vmware.taurus.exception.ErrorMessage;
import lombok.extern.slf4j.Slf4j;
import org.ini4j.Ini;
import org.ini4j.IniPreferences;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import java.io.File;
import java.util.HashMap;
import java.util.Map;
import java.util.prefs.BackingStoreException;
import java.util.prefs.Preferences;

/**
 * VDK Options and environment variables that are passed to VDK during execution. Enables
 * administrators to apply common configuration for all Data Jobs. Admins can specify global options
 * in "default" ini section or per job in "job-name" ini section.
 */
@Component
@Slf4j
public class VdkOptionsReader {

  private String vdkOptionsIni;

  @Autowired
  public VdkOptionsReader(@Value("${datajobs.vdk_options_ini}") String vdkOptionsIni) {
    this.vdkOptionsIni = vdkOptionsIni;
  }

  public Map<String, String> readVdkOptions(String jobName) {
    Map<String, String> vdkOptions = new HashMap<>();

    try {
      var iniFile = new File(this.vdkOptionsIni);
      if (!iniFile.isFile()) {
        ErrorMessage message =
            new ErrorMessage(
                "VDK Options file is not specified or missing.",
                String.format(
                    "'%s' is missing. Most likely it is not configured during installation.",
                    vdkOptionsIni),
                "This is not necessarily a problem since the defaults that come with VDK will be"
                    + " used for the data jobs. ",
                "Specify during installation vdk options file if it's necessary otherwise nothing"
                    + " and you can ignore this.");
        log.warn(message.toString());
        return vdkOptions;
      }

      Preferences vdkOptionsIni = new IniPreferences(new Ini(iniFile));

      var defaults = iniSectionToMap("default", "", vdkOptionsIni);
      var perJob = iniSectionToMap(jobName, "", vdkOptionsIni);
      vdkOptions.putAll(defaults);
      // TODO add per team ?
      vdkOptions.putAll(perJob);
    } catch (Exception e) {
      log.error("Error while reading VDK runtime options. Default options will be used.", e);
    }
    return vdkOptions;
  }

  public Map<String, String> iniSectionToMap(String section, String def, Preferences ini)
      throws BackingStoreException {
    Map<String, String> sectionMap = new HashMap<>();

    if (ini.nodeExists(section)) {
      Preferences iniSection = ini.node(section);
      for (var key : iniSection.keys()) {
        sectionMap.put(key, iniSection.get(key, def));
      }
    }
    return sectionMap;
  }
}
