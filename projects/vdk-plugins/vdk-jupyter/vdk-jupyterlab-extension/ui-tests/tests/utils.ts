/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { galata } from '@jupyterlab/galata';

export async function copyDirectory(
  baseURL: string,
  sourceDirectory: string,
  destination: string
): Promise<void> {
  const contents = galata.newContentsHelper(baseURL);

  await contents.uploadDirectory(sourceDirectory, destination);
}
