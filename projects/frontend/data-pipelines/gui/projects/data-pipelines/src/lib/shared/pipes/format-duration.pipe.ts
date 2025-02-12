/*
 * Copyright 2023-2025 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

import { Pipe, PipeTransform } from '@angular/core';
import { FormatDeltaPipe } from './format-delta.pipe';

@Pipe({
    name: 'formatDuration'
})
export class FormatDurationPipe implements PipeTransform {
    /**
     * @inheritDoc
     */
    transform(durationSeconds: number): string {
        return durationSeconds ? FormatDeltaPipe.formatDelta(durationSeconds) : null;
    }
}
