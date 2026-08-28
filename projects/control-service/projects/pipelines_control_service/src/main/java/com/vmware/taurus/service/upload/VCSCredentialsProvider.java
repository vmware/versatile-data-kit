/*
 * Copyright 2023-2024 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.upload;

import org.eclipse.jgit.transport.CredentialsProvider;

/**
 * Class responsible for handling different credential providers.
 *
 */
public interface VCSCredentialsProvider {

    CredentialsProvider getProvider();
}
