/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs.webhook;

import lombok.Getter;
import org.mockito.InjectMocks;

@Getter
/** See {@link BaseWebHookProviderTest} for the details of the tests. */
public class PostDeleteWebHookProviderTest extends BaseWebHookProviderTest {
  @InjectMocks
  private PostDeleteWebHookProvider webHookProvider = new PostDeleteWebHookProvider("", -1);
}
