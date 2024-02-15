/*
 * Copyright 2023-2024 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021-2024 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs.webhook;

import lombok.Getter;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.test.context.TestPropertySource;

@TestPropertySource(
    properties = {
      "datajobs.post.delete.webhook.endpoint=http://localhost:4444",
      "datajobs.post.delete.webhook.internal.errors.retries=0",
      "datajobs.post.delete.webhook.authentication.enabled=false"
    })
@Getter
/** See {@link BaseWebHookProviderTest} for the details of the tests. */
public class PostDeleteWebHookProviderTest extends BaseWebHookProviderTest {

  @Autowired private PostDeleteWebHookProvider webHookProvider;
}
