
import { Type } from "@angular/core";
import { VmwToastComponent } from "./toast.component";
import { VmwToastContainerComponent } from "./toast-container.component";

export * from "./toast.component";
export * from "./toast-container.component";
export * from "./toast.model";

export const TOAST_DIRECTIVES: Type<any>[] = [
    VmwToastContainerComponent,
    VmwToastComponent,
];
