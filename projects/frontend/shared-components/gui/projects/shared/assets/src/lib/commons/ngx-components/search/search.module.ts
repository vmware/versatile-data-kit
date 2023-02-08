import { NgModule, CUSTOM_ELEMENTS_SCHEMA } from "@angular/core";

import { CommonModule } from "@angular/common";
import {VmwSearchComponent} from "./search.component";
import {ReactiveFormsModule} from "@angular/forms";

@NgModule({
    declarations: [
        VmwSearchComponent
    ],
    imports: [
        CommonModule,
        ReactiveFormsModule
    ],
    exports: [
        VmwSearchComponent
    ],
    schemas: [
        CUSTOM_ELEMENTS_SCHEMA,
    ],
})
export class VmwSearchModule {}
