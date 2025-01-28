/*
 * Copyright 2023-2024 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

/* eslint-disable */

import { Pipe, PipeTransform } from '@angular/core';

import { VdkSimpleTranslateService } from './simple-translate.service';

@Pipe({
    name: 'simpleTranslate',
    pure: false
})
export class VdkSimpleTranslatePipe implements PipeTransform {
    constructor(private simpleTranslate: VdkSimpleTranslateService) {}

    transform(text: string, ...args: any[]) {
        return this.simpleTranslate.translate(text, ...args);
    }
}
