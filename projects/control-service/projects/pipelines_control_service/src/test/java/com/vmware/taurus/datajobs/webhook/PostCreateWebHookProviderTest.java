/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs.webhook;

import lombok.Getter;
import org.mockito.InjectMocks;

@Getter
/** See {@link BaseWebHookProviderTest} for the details of the tests. */
public class PostCreateWebHookProviderTest extends BaseWebHookProviderTest {
  @InjectMocks
  private PostCreateWebHookProvider webHookProvider = new PostCreateWebHookProvider("", -1);
}
