/*
 * Copyright 2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { ConfirmationInputModel } from '../../confirmation';

/**
 * @inheritDoc
 * Extended model on top of {@link ConfirmationInputModel} for the needs of Url Opener Service.
 */
export interface UrlOpenerModel extends ConfirmationInputModel {
    /**
     * ** Ask for explicit confirmation even when provided Url is internal.
     *
     *      - If not provided default value is false and won't ask for internal url navigation confirmation.
     *      - Internal url are all urls that don't start with <b><code>http://</code></b> or <b><code>https://</code></b>
     *              or if they start their Origin is same like Application Origin.
     */
    explicitConfirmation?: boolean;
}

/**
 * ** Url opener target.
 *
 *      - It would be same Browser tab if value is <b><code>_self</code></b>
 *      - It would be new Browser tab if value is <b><code>_blank</code></b>
 */
export type UrlOpenerTarget = '_self' | '_blank';
