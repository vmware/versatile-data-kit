# Taurus Data Pipelines

Data Pipelines help Data Engineers develop, deploy, run, and manage data processing workloads (called "Data Job").
This library provides UI screens that helps to manage data jobs via Data Pipelines API.

## Implementation


### Include the packages and ngrx dependencies
```shell
npm i @vdk/{data-pipelines,shared} # Actual library
npm i @ngrx/{effects,entity,router-store,@ngrx/store} # NgRx (store management)
npm i @clr/{angular,icons,ui} # Clarity (UI Components like DataGrid)

```

### Include the module and router

1. In `app.module.ts` include ngrx modules and actual Data Pipeline module
```typescript
imports: [
  ...
  VdkSharedCoreModule.forRoot(), // vdk shared core services
  VdkSharedFeaturesModule.forRoot(), // vdk shared features
  VdkSharedNgRxModule.forRootWithDevtools(), // vdk redux actual ngrx implementation
  ...
]
```

2. in `app.router.ts` you can specify the parent path for data pipelines screens.
   This example shows how can we expose the data jobs list by using `data-pipelines` string as parent.
```typescript
const routes: Routes = [
  ...
  {
    path: 'data-pipelines',
    loadChildren: () => import('@vdk/data-pipelines').then(m => m.DataPipelinesRouting)
  },
  ...
]

@NgModule({
  imports: [RouterModule.forRoot(routes, routerOptions)],
  exports: [RouterModule]
})
export class AppRouting {
}
```
**Note:** You can inspect the [data-pipelines.routing.ts](src/lib/data-pipelines.routing.ts) to see what pages could be routed

### Configure the route

3. In `app.component.ts` somewhere in you menu you can include a link to the data jobs list, like:
```angular2html
<a id="navDataJobs" routerLink="/data-pipelines/list">Data Jobs</a>
```

## Code scaffolding

Run `ng generate component component-name --project data-pipelines` to generate a new component. You can also use `ng generate directive|pipe|service|class|guard|interface|enum|module --project data-pipelines`.
> Note: Don't forget to add `--project data-pipelines` or else it will be added to the default project in your `angular.json` file.

Also, this project uses [NgRx](https://ngrx.io/) for state management, you can check their [schematics](https://ngrx.io/guide/schematics) for code generation like:
```shell
ng generate @ngrx/schematics:effect DataJobs --module data-pipelines.module.ts
```
## Build & Running

Run `npm run build` to build the project. The build artifacts will be stored in the `dist/` directory.

### Publishing

After building your library with `npm run build`, go to the dist folder `cd dist/data-pipelines` and run `npm publish`.

### Running unit tests

Run `npm run test` to execute the unit tests via [Karma](https://karma-runner.github.io).

### Testing

You can use the reference implementation in <project_root>/projects/gui/projects/ui as showcase of the library.
Using `npm link` you can achieve real-time development of the library without the need to upload it to repository
