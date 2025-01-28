/*
 * Copyright 2023-2025 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

import { HttpErrorResponse } from '@angular/common/http';

import { VmwToastType } from '../../../commons';
import { ApiErrorMessage } from '../../../common';

export interface Toast {
    title: string;
    description: string;
    type: VmwToastType;
    error?: Error | ApiErrorMessage | FormattedError | HttpErrorResponse;
    expanded?: boolean;
    responseStatus?: number;
    extendedData?: {
        title: string;
        description: string;
    };
}

export interface FormattedError {
    consequences?: string;
    countermeasures?: string;
    what: string;
    why: string;
}
