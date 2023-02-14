/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.credentials;

import java.io.File;
import java.util.Optional;

/**
 * CRUD operations on principals and credentials which are associated with a given data job. The
 * backing service can be LDAP or Kerberos or Cloud IAM (AWS IAM), etc.
 */
public interface CredentialsRepository {
  /**
   * Create principal with the given name and store its credentials in the file location passed
   *
   * @param principal the name of the principal (e.g user name in LDAP)
   * @param keytabLocation here to export the file with credentials (password, keys) for the new
   *     principal. If there's already existing file, it will be deleted/overwritten with new
   *     credentials.
   */
  void createPrincipal(String principal, Optional<File> keytabLocation);

  /**
   * Check if principle already exists
   *
   * @param principal the name of the principal (e.g user name in LDAP)
   * @return
   */
  boolean principalExists(String principal);

  /**
   * Delete the principal with given name. This should also invalidate its credentials (password,
   * key, etc.)
   *
   * @param principal the name of the principal (e.g user name in LDAP)
   */
  void deletePrincipal(String principal);
}
