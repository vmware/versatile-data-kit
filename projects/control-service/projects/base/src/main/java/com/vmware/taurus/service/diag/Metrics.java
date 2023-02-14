/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.diag;

public enum Metrics {
  call_failed // Boolean: false
  ,

  class_name_full // String: "com.vmware.taurus.service.diag.DiagnosticsController"
  ,

  class_name_short // String: "DiagnosticsController"
  ,

  cp_svc_name // String (containing Control Plane Service name): "team"
  ,

  error_class // class: class java.lang.RuntimeException
  ,

  error_message // String: Just throwing.
  ,

  error_stacktrace // String: java.lang.RuntimeException: Just throwing. \r\n\tat
  // com.vmware.taurus.service.diag.DiagnosticsController.throwException(DiagnosticsController.java:28) ...
  ,

  http_body_type // String (contains body.getClass.getName() ): java.lang.String
  ,

  http_code // Integer: 200
  ,

  measurable_args // String: somearg
  ,

  measurable_tags // String(CSV): [tag1, tag2]
  ,

  method_execution_time_nanos // Long: 12761970
  ,

  method_execution_end_timestamp // Unix timestamp since epoch in milliseconds: 1613944487926
  ,

  method_name // String: "foo"
  ,

  method_result // Object: ...
  ,

  op_id // String (contains Long): "01575568907793"
  ,

  request_paths // String (contains CSV): /base/debug/echo/{msg}, /base/debug/echo2/{msg}
  ,
}
