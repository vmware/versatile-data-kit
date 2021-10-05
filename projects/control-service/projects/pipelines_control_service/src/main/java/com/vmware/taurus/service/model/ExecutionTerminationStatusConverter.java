/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.model;

import javax.persistence.AttributeConverter;
import javax.persistence.Converter;
import java.util.Arrays;

@Converter
public class ExecutionTerminationStatusConverter implements AttributeConverter<ExecutionTerminationStatus, Integer> {

   @Override
   public Integer convertToDatabaseColumn(ExecutionTerminationStatus terminationStatus) {
      return terminationStatus != null ? terminationStatus.getInteger() : null;
   }

   @Override
   public ExecutionTerminationStatus convertToEntityAttribute(Integer dbData) {
      return Arrays.stream(ExecutionTerminationStatus.values())
            .filter(terminationStatus -> terminationStatus.getInteger().equals(dbData))
            .findAny()
            .orElse(null);
   }
}
