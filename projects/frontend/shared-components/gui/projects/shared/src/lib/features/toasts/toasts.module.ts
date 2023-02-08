import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { ClipboardModule } from 'ngx-clipboard';

import { ClarityModule } from '@clr/angular';

import { VmwComponentsModule } from '../../commons';

import { ToastsComponent } from './widget';

@NgModule({
    imports: [
        CommonModule,
        ClarityModule,
        VmwComponentsModule,
        ClipboardModule
    ],
    declarations: [
        ToastsComponent
    ],
    exports: [
        ToastsComponent
    ]
})
export class ToastsModule {
}
