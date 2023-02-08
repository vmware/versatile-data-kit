import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

const routes: Routes = [
    {
        path: '',
        redirectTo: 'overview',
        pathMatch: 'full'
    },
    // Overview
    {
        path: 'overview',
        loadChildren: () => import('./core/core.module').then((m) => m.CoreModule)
    },
    { path: '**', redirectTo: 'overview' }
];

@NgModule({
    imports: [RouterModule.forRoot(routes)],
    exports: [RouterModule]
})
export class AppRoutingModule {
}
