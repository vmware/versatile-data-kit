

/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { CUSTOM_ELEMENTS_SCHEMA, ModuleWithProviders, NgModule } from "@angular/core";
import { CommonModule } from "@angular/common";
import { FormsModule, ReactiveFormsModule } from "@angular/forms";

import {
    ClarityModule,
    ClrDropdownModule,
    ClrLoadingButtonModule,
    ClrLoadingModule,
    ClrTooltipModule,
} from "@clr/angular";

import { VdkSimpleTranslateModule } from '../ngx-utils';

import {
    angleIcon,
    arrowIcon,
    checkCircleIcon,
    checkIcon,
    ClarityIcons,
    copyToClipboardIcon,
    exclamationCircleIcon,
    searchIcon,
    timesCircleIcon,
    timesIcon
} from '@cds/core/icon';

import { VdkEmptyStatePlaceholderModule } from "./empty-state-placeholder/empty-state-placeholder.module";

import { COPY_TO_CLIPBPOARD_BUTTON_DIRECTIVES } from "./copy-to-clipboard-button/index";
import { FORM_SECTION_DIRECTIVES } from "./form-section/index";
import { FORM_SECTION_CONTAINER_DIRECTIVES } from "./form-section-container/index";
import { TOAST_DIRECTIVES } from "./toast/index";
import { VdkSearchModule } from "./search";

@NgModule({
    imports: [
        CommonModule,
        FormsModule,
        ReactiveFormsModule,
        ClarityModule,
        ClrTooltipModule,
        ClrDropdownModule,
        ClrLoadingModule,
        ClrLoadingButtonModule,
        VdkSimpleTranslateModule,
        VdkEmptyStatePlaceholderModule,
        VdkSearchModule
    ],
    declarations: [
        COPY_TO_CLIPBPOARD_BUTTON_DIRECTIVES,
        FORM_SECTION_DIRECTIVES,
        FORM_SECTION_CONTAINER_DIRECTIVES,
        TOAST_DIRECTIVES
    ],
    exports: [
        COPY_TO_CLIPBPOARD_BUTTON_DIRECTIVES,
        FORM_SECTION_DIRECTIVES,
        FORM_SECTION_CONTAINER_DIRECTIVES,
        TOAST_DIRECTIVES,
        VdkEmptyStatePlaceholderModule,
        VdkSearchModule
    ],
    schemas: [
        CUSTOM_ELEMENTS_SCHEMA,
    ],
})
export class VdkComponentsModule {
    static forRoot(): ModuleWithProviders<VdkComponentsModule> {
        return {
            ngModule: VdkComponentsModule,
        };
    }

    static forChild(): ModuleWithProviders<VdkComponentsModule> {
        return {
            ngModule: VdkComponentsModule,
        };
    }

    constructor() {
        ClarityIcons.addIcons(
            angleIcon,
            arrowIcon,
            checkCircleIcon,
            checkIcon,
            copyToClipboardIcon,
            exclamationCircleIcon,
            searchIcon,
            timesCircleIcon,
            timesIcon
        );
    }
}
