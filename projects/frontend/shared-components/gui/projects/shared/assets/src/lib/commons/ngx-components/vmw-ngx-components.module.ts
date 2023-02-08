

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

import { VmwSimpleTranslateModule } from '../ngx-utils';

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

import { VmwEmptyStatePlaceholderModule } from "./empty-state-placeholder/empty-state-placeholder.module";

import { COPY_TO_CLIPBPOARD_BUTTON_DIRECTIVES } from "./copy-to-clipboard-button/index";
import { FORM_SECTION_DIRECTIVES } from "./form-section/index";
import { FORM_SECTION_CONTAINER_DIRECTIVES } from "./form-section-container/index";
import { TOAST_DIRECTIVES } from "./toast/index";
import { VmwSearchModule } from "./search";

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
        VmwSimpleTranslateModule,
        VmwEmptyStatePlaceholderModule,
        VmwSearchModule
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
        VmwEmptyStatePlaceholderModule,
        VmwSearchModule
    ],
    schemas: [
        CUSTOM_ELEMENTS_SCHEMA,
    ],
})
export class VmwComponentsModule {
    static forRoot(): ModuleWithProviders<VmwComponentsModule> {
        return {
            ngModule: VmwComponentsModule,
        };
    }

    static forChild(): ModuleWithProviders<VmwComponentsModule> {
        return {
            ngModule: VmwComponentsModule,
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
