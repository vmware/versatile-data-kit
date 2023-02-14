/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.credentials;

import com.vmware.taurus.ServiceAppPropNames;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.context.annotation.Profile;
import org.springframework.stereotype.Component;

import java.io.File;
import java.util.Optional;

/**
 * Creates dummy empty princpal that does not exists. Used to basically disable credentials
 * generation functionality.
 */
@Profile("!MockKerberos")
@Component
@ConditionalOnProperty(
    value = ServiceAppPropNames.CREDENTIALS_REPOSITORY_TYPE,
    havingValue = "EMPTY",
    matchIfMissing = true)
public class EmptyCredentialsRepository implements CredentialsRepository {
  private static final Logger log = LoggerFactory.getLogger(EmptyCredentialsRepository.class);

  public EmptyCredentialsRepository() {
    log.info("Credentials repository used will be empty - no credentials.");
  }

  @Override
  public void createPrincipal(String principal, Optional<File> keytabLocation) {
    log.trace("Create empty principal " + principal);
  }

  @Override
  public boolean principalExists(String principal) {
    return false;
  }

  @Override
  public void deletePrincipal(String principal) {
    log.trace("Delete empty principal " + principal);
  }
}
