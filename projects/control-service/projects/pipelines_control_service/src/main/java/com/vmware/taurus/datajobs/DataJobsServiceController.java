/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs;

import com.vmware.taurus.controlplane.model.api.DataJobsServiceApi;
import com.vmware.taurus.controlplane.model.data.DataJobApiInfo;
import com.vmware.taurus.service.UserAgentService;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.RestController;

/**
 * REST controller for operations on data job
 *
 * <p>REST behaviour and response codes should follow guidelines at
 *
 * <p>The controller may throw exception which will be handled by {@link
 * com.vmware.taurus.exception.ExceptionControllerAdvice}. The advice class logs error so no need to
 * log them here.
 */
@RestController
@AllArgsConstructor
@NoArgsConstructor
@Tag(name = "Data Jobs Service")
public class DataJobsServiceController implements DataJobsServiceApi {

  @Autowired UserAgentService userAgentService;

  @Override
  public ResponseEntity<DataJobApiInfo> info(String teamName) {
    DataJobApiInfo result = new DataJobApiInfo();
    result.setApiVersion(userAgentService.getUserAgentDetails());
    return ResponseEntity.ok(result);
  }
}
