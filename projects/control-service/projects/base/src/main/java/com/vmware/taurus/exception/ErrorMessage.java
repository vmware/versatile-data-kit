/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.exception;

import com.fasterxml.jackson.annotation.JsonPropertyOrder;

@JsonPropertyOrder({"what", "why", "consequences", "countermeasures"})
public class ErrorMessage {
  private final String what; // Context
  private final String why; // Problem
  private final String countermeasures; // By user
  private final String consequences; // For user

  public ErrorMessage(String what, String why, String consequences, String countermeasures) {
    this.why = why;
    this.countermeasures = countermeasures;
    this.what = what;
    this.consequences = consequences;
  }

  public String getWhy() {
    return why;
  }

  public String getCountermeasures() {
    return countermeasures;
  }

  public String getWhat() {
    return what;
  }

  public String getConsequences() {
    return consequences;
  }

  @Override
  public String toString() {
    return "An issue occurred:"
        + "\n\tcontext="
        + what
        + ",\n\tproblem="
        + why
        + ",\n\tconsequences="
        + consequences
        + ",\n\tcountermeasures="
        + countermeasures;
  }
}
