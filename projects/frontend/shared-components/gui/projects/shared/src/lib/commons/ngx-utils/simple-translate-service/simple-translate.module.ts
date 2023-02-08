

import { NgModule, ModuleWithProviders } from "@angular/core";

import { VmwSimpleTranslateService } from "./simple-translate.service";
import { VmwSimpleTranslatePipe } from "./simple-translate.pipe";

@NgModule({
    declarations: [
        VmwSimpleTranslatePipe,
    ],
    exports: [
        VmwSimpleTranslatePipe,
    ],
})
export class VmwSimpleTranslateModule {
    static forRoot(): ModuleWithProviders<VmwSimpleTranslateModule> {
        return {
            ngModule: VmwSimpleTranslateModule,
            providers: [
                VmwSimpleTranslateService,
            ]
        };
    }
}
