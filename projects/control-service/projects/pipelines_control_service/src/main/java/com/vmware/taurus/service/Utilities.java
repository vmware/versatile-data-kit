/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service;

import graphql.ExceptionWhileDataFetching;
import graphql.GraphQLError;
import org.apache.commons.lang3.StringUtils;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;

public final class Utilities {

  private static final String DEFAULT_DELIMITER = ";";

  private Utilities() {}

  /**
   * Concatenates the specified values using the default delimiter, ';', in between them.
   *
   * @param elements The values to concatenate.
   * @return The concatenated values, or an empty string if {@code elements} is null.
   */
  public static String join(Iterable<? extends CharSequence> elements) {
    return join(elements, DEFAULT_DELIMITER);
  }

  /**
   * Concatenates the specified values using the specified delimiter in between them.
   *
   * @param elements The values to concatenate.
   * @param delimiter The delimiter to use.
   * @return The concatenated values, or an empty string if {@code elements} is null.
   */
  public static String join(Iterable<? extends CharSequence> elements, CharSequence delimiter) {
    return elements == null ? "" : String.join(delimiter, elements);
  }

  /**
   * Splits the specified string into an array using the default delimiter, ';'.
   *
   * @param values The string to split.
   * @return A list of parsed strings, or an empty list, of the provided value is {@code null}.
   */
  public static List<String> parseList(String values) {
    String[] parts = StringUtils.split(values, DEFAULT_DELIMITER);
    return values == null ? Collections.emptyList() : Arrays.asList(parts);
  }

  /**
   * Hide stacktrace of the response body. Without this it return fat stacktrace into json response
   * body More info for future workarounds https://github.com/graphql-java/graphql-java/issues/939
   *
   * @param errors List of graphql errors attached to the response body
   * @return Altered errors list with stacktrace removed
   */
  public static List<GraphQLError> removeGraphQLErrorsStackTrace(List<GraphQLError> errors) {
    if (errors != null) {
      errors.stream()
          .filter(ExceptionWhileDataFetching.class::isInstance)
          .map(ExceptionWhileDataFetching.class::cast)
          .filter(exceptionWhileDataFetching -> exceptionWhileDataFetching.getException() != null)
          .forEach(
              exceptionWhileDataFetching ->
                  exceptionWhileDataFetching
                      .getException()
                      .setStackTrace(new StackTraceElement[] {}));
      return errors;
    }
    return new ArrayList<>();
  }
}
