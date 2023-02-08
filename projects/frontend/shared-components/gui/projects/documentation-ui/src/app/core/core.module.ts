import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CoreComponent } from './core.component';
import { RouterModule, Routes } from '@angular/router';
import { ClarityModule } from '@clr/angular';

const routes: Routes = [
    {
        path: '',
        component: CoreComponent
    }
];

@NgModule({
    declarations: [CoreComponent],
    imports: [RouterModule.forChild(routes), CommonModule, ClarityModule]
})
export class CoreModule {
}
