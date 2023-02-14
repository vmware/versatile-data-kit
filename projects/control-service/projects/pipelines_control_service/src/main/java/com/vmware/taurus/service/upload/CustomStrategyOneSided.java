/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.upload;

import org.eclipse.jgit.lib.Config;
import org.eclipse.jgit.lib.ObjectId;
import org.eclipse.jgit.lib.ObjectInserter;
import org.eclipse.jgit.lib.Repository;
import org.eclipse.jgit.merge.MergeStrategy;
import org.eclipse.jgit.merge.Merger;
import org.eclipse.jgit.merge.ResolveMerger;
import org.eclipse.jgit.merge.StrategyOneSided;

/**
 * Class responsible for rebase strategies which is a custom implementation of {@link
 * StrategyOneSided}
 *
 * <p>The class is needed as there is a well known bug with the library we are using:
 * https://bugs.eclipse.org/bugs/show_bug.cgi?id=501111
 */
public class CustomStrategyOneSided extends MergeStrategy {
  private final String strategyName;

  private final int treeIndex;

  /**
   * Create a new merge strategy to select a specific input tree.
   *
   * @param name name of this strategy.
   * @param index the position of the input tree to accept as the result.
   */
  protected CustomStrategyOneSided(String name, int index) {
    strategyName = name;
    treeIndex = index;
  }

  @Override
  public String getName() {
    return strategyName;
  }

  @Override
  public Merger newMerger(Repository db) {
    return new CustomStrategyOneSided.CustomOneSide(db, treeIndex);
  }

  @Override
  public Merger newMerger(Repository db, boolean inCore) {
    return new CustomStrategyOneSided.CustomOneSide(db, treeIndex);
  }

  @Override
  public Merger newMerger(ObjectInserter inserter, Config config) {
    return null;
  }

  static class CustomOneSide extends ResolveMerger {
    private final int treeIndex;

    protected CustomOneSide(Repository local, int index) {
      super(local);
      treeIndex = index;
    }

    @Override
    protected boolean mergeImpl() {
      return treeIndex < sourceTrees.length;
    }

    @Override
    public ObjectId getResultTreeId() {
      return sourceTrees[treeIndex];
    }

    @Override
    public ObjectId getBaseCommitId() {
      return null;
    }
  }
}
