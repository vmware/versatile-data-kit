/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.model.converter;

import javax.persistence.AttributeConverter;
import javax.persistence.Converter;
import java.util.Arrays;

import com.vmware.taurus.service.model.ExecutionStatus;

@Converter
public class ExecutionStatusConverter implements AttributeConverter<ExecutionStatus, Integer> {

   @Override
   public Integer convertToDatabaseColumn(ExecutionStatus executionStatus) {
      return executionStatus != null ? executionStatus.getDbValue() : null;
   }

   @Override
   public ExecutionStatus convertToEntityAttribute(Integer dbValue) {
      if (dbValue == null) {
         return null;
      }

      // temporary solution for backward compatibility.
      if (dbValue == 3) {
         return ExecutionStatus.PLATFORM_ERROR;
      }

      return Arrays.stream(ExecutionStatus.values())
            .filter(terminationStatus -> terminationStatus.getDbValue().equals(dbValue))
            .findAny()
            .orElse(null);
   }
}
