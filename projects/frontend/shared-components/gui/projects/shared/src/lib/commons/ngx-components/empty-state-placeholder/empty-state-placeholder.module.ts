
import { CommonModule } from "@angular/common";
import { CUSTOM_ELEMENTS_SCHEMA, NgModule } from "@angular/core";
import { VmwEmptyStatePlaceholderComponent } from "./empty-state-placeholder.component";

@NgModule({
    imports: [
        CommonModule,
    ],
    declarations: [
        VmwEmptyStatePlaceholderComponent,
    ],
    exports: [
        VmwEmptyStatePlaceholderComponent,
    ],
    schemas: [
        CUSTOM_ELEMENTS_SCHEMA,
    ],
})
export class VmwEmptyStatePlaceholderModule {
}
