/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Attributes } from '../../../directives';

interface IconAttributes extends Attributes {
    style?: string;
    title?: string;
    class?: string;
    shape?: string;
    // eslint-disable-next-line @typescript-eslint/naming-convention
    'data-cy'?: string;
    size?: number;
}

export interface QuickFilter {
    id?: string;
    label: string;
    icon?: IconAttributes;
    active?: boolean;
    suppressCancel?: boolean;
    onActivate?: () => void;
    onDeactivate?: () => void;
}

export type QuickFilters = QuickFilter[];

export interface QuickFilterChangeEvent {
    deactivatedFilter: QuickFilter | null;
    activatedFilter: QuickFilter | null;
}
