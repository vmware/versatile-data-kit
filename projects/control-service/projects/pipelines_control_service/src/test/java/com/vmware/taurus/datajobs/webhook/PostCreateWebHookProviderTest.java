/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs.webhook;

import lombok.Getter;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.test.context.TestPropertySource;

@TestPropertySource(
    properties = {
      "datajobs.post.create.webhook.endpoint=http://localhost:4444",
      "datajobs.post.create.webhook.internal.errors.retries=0",
      "datajobs.post.create.webhook.authentication.enabled=false"
    })
@Getter
/** See {@link BaseWebHookProviderTest} for the details of the tests. */
public class PostCreateWebHookProviderTest extends BaseWebHookProviderTest {

  @Autowired private PostCreateWebHookProvider webHookProvider;
}
