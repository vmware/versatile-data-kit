/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.graphql.strategy;

import com.vmware.taurus.service.graphql.model.Criteria;
import com.vmware.taurus.service.graphql.strategy.datajob.JobFieldStrategyBy;
import com.vmware.taurus.service.graphql.model.Filter;
import org.springframework.data.domain.Sort;
import org.springframework.lang.NonNull;
import org.apache.commons.io.FilenameUtils;

import java.util.Comparator;
import java.util.function.Predicate;

/**
 * In order to provide a complex filtering and searching functionality as well as data querying to
 * different source (K8s, Database) we need to abstract the logic for this into separate classes and
 * Strategy pattern seems like a good option. When someone ask for filtering it passes which field
 * want to manipulate by and this is the key of the key-value pair of the strategy pattern
 *
 * <p>When a new field needs to be added the steps are (currently) two: 1. Add new enum entry in
 * {@link JobFieldStrategyBy} with the field name 2. Create a class which extends this abstract
 * class and is annotated by @Component
 *
 * <p>Then, Spring will detect automatically that there is new {@link FieldStrategy} instance and it
 * will be included in the field manipulation mechanism
 */
public abstract class FieldStrategy<T> {

  /**
   * The getter for the strategy name, required to be unique, not duplicated by other impl classes
   *
   * @return Strategy unique enum entry
   */
  public abstract JobFieldStrategyBy getStrategyName();

  /**
   * By provided fields and pattern it computes the predicates needed for later stream
   * filters/sorting
   *
   * @param criteria Existing criteria containing already chained Predicates and sorting
   * @param filter Provided filter containing information about needed sorting direction and
   *     filtering pattern.
   * @return The altered chained Predicates and comparator
   */
  public abstract Criteria<T> computeFilterCriteria(
      @NonNull Criteria<T> criteria, @NonNull Filter filter);

  /**
   * By provided search string compute a predicate depending on the strategy which could be chained
   *
   * @param searchStr Search string
   * @return Predicate for specific field strategy
   */
  public abstract Predicate<T> computeSearchCriteria(@NonNull String searchStr);

  /**
   * If there is need some of the field to be computed separately (e.g the raw list is fetched from
   * database, and it needs to deep dive in other service, like K8s, in order to populate additional
   * information) this method will be invoked before computing Filter criteria and search mechanism
   * only if the specific field is requested
   *
   * @param element Target element to be enriched
   */
  public void alterFieldData(T element) {
    // Default empty action
  }

  /**
   * Helper method to detect if there is sorting needed
   *
   * @param filter Class which holds filter and sorting field data
   * @return true if there is provided direction, false if its not
   */
  protected boolean sortingProvided(Filter filter) {
    return filter != null && filter.getSort() != null;
  }

  /**
   * By default comparators are in ascending order and we can with ease reverse them using
   * Comparator.reverse()
   *
   * @param direction ASC or DESC direction
   * @return true if DESC, false if ASC
   */
  protected boolean invertSorting(Sort.Direction direction) {
    return Sort.Direction.DESC.equals(direction);
  }

  /**
   * Helper method to detect if there is filtering needed
   *
   * @param filter Class which holds filter and sorting field data
   * @return true if there is provided pattern for filtering, false if its not
   */
  protected boolean filterProvided(Filter filter) {
    return filter != null && filter.getPattern() != null;
  }

  /**
   * Helper method to detect whether we include the comparator provided by the strategy (if its
   * requested for specific field) or just use the default (last used). This means that sorting is
   * done only by 1 field
   *
   * @param filter
   * @param comparator
   * @param criteria
   * @return
   */
  protected Comparator<T> detectSortingComparator(
      Filter filter, Comparator<T> comparator, Criteria<T> criteria) {
    if (sortingProvided(filter)) {
      if (invertSorting(filter.getSort())) {
        comparator = comparator.reversed();
      }
      return comparator;
    }
    return criteria.getComparator();
  }

  /**
   * Helper method which checks if the provided search string matches with a given matcher string.
   * String capitalization is ignored. Supported operations are wildcard matching of '*' characters
   * in the matcher string, or exact matches. If the matcher string contains '*' we will attempt to
   * match wildcards, otherwise both strings are compared for equality.
   *
   * @param searchString
   * @param matcherString
   * @return
   */
  protected boolean checkMatch(String searchString, String matcherString) {
    if (searchString == null || matcherString == null) {
      return false;
    } else if (matcherString.contains("*")) {
      // Matching strings that contain * as wildcards.
      return FilenameUtils.wildcardMatch(searchString.toLowerCase(), matcherString.toLowerCase());
    } else {
      // exact matches
      return searchString.equalsIgnoreCase(matcherString);
    }
  }
}
