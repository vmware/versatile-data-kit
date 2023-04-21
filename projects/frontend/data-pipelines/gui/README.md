# VDK Data Pipeline UI

The gui part of data-pipelines contains:

  * **[Data Pipelines](projects/data-pipelines/README.md)** Library that holds UI Components for managing Data Pipeline API.
  * **[UI](projects/ui/src)** Default UI Wrapper Implementation of the Data Pipeline library

The wrapper ([ui](projects/ui/src)) provides standard OAuth2 authorization flow, configuration of which could be found in [appConfig.json](projects/ui/src/assets/data/appConfig.json)

## Running and Testing

You can use Frontend implementation in `projects/ui`.
Using `npm link` you can achieve real-time development of the library without the need to upload it to repository

_**Note**_: If you run directly npm install without linking it will tell you that there is no such package.
That's why you need to link it the first time you build your development environment.

Refer to [.gitlab-ci.yml](../../.gitlab-ci.yml) file for correct setup guaranteed to work by automation.
Bug in general the steps are:

0. Set npm registry to use
   ```bash
   $ npm config set legacy-peer-deps true
   ```
1. Install Angular Cli and all other dependencies except '@versatiledatakit/data-pipelines'
   ```bash
   npm i -g @angular/cli@13
   ```
   ```bash
   npm i --omit=optional
   ```
1. Update peer dependencies to latest versions (optional)

   Run this step if it's not a fresh install and peer dependencies need to be
   updated
   ```bash
   npm update
   ```
2. Build the data-pipelines UI library
   ```bash
   npm run build
   ```
3. Go to the build dir
   ```bash
   cd dist/data-pipelines
   ```
4. Link it to local repo
   ```bash
   npm link
   ```
5. Return to project dir
   ```bash
   cd ../../
   ```
6. Create symlink from build artifact to the wrapper ui (ui)
   ```bash
   npm link @versatiledatakit/data-pipelines
   ```
7. Start the wrapper ui application, serve on [http://localhost.vmware.com:4200](http://localhost.vmware.com:4200)
   ```bash
   npm start
   ```

## Adding boilerplate code

This project is using [NX](https://nx.dev/latest/angular/getting-started/getting-started).
It supports many plugins which add capabilities for developing different types of applications and different tools.
These capabilities include generating applications, libraries, etc as well as the devtools to test, and build projects as well.

### Generate a library

Run `ng g @nrwl/angular:lib <my-lib>` to generate a library.

Libraries are shareable across libraries and applications. They can be imported from `@versatiledatakit/<mylib>`.

### Code scaffolding
Run `ng generate component component-name --project ui` to generate a new component. You can also use `ng generate directive|pipe|service|class|guard|interface|enum|module --project ui`.
> Note: Don't forget to add `--project ui` or else it will be added to the default project in your `angular.json` file.

Also, this project uses [NgRx](https://ngrx.io/) for state management, you can check their [schematics](https://ngrx.io/guide/schematics) for code generation like:
```shell
ng generate @ngrx/schematics:effect Teams --module app.module.ts
```

### Linting
Run `npm run lint` to execute lint via [ESLint](https://eslint.org/docs/user-guide/getting-started).

### Running tests

[Unit] Run `npm run test` to execute the unit tests via [Karma](https://karma-runner.github.io).

_**Note**_: Code coverage report will be generated in `reports/coverage`(for the UI Wrapper and the Data Pipeline Library)

_**Note**_: Code coverage report for the Data Pipeline library will be also logged in the Console(and consumed by the CI/CD)

[TODO](https://github.com/vmware/versatile-data-kit/issues/1610) re-visit when OAuth is agreed on
[E2E] Run `npx cypress open --env OAUTH2_API_TOKEN=<the API token>` to open [Cypress](https://www.cypress.io/) dev tool for e2e testing
* Configuring the e2e tests environment: In `cypress.json > env` section are configured `login_url` and `data_jobs_url`
 that are used by the e2e tests. To override the values a feasible option is to create a local file: `cypress.env.json`
 that will provide the overriden values like:
  `{
  "data_jobs_url": "http://localhost:8092"
  }`

   See: https://docs.cypress.io/guides/guides/environment-variables.html#Setting

_**Note**_: Capturing HAR reports. In order to capture the HAR reports(default location: `e2e/hars`) during the e2e tests execution
 you need to run the tests using Chrome browser.
Example run: `npx cypress run --browser chrome --env OAUTH2_API_TOKEN=<the API token>`

_**Note**_: Chrome may have sporadic issues running the tests in headed mode. To overcome this you can:
1. Use an other browser(Firefox, Chromium, or  Electron)
2. Run the tests in headless mode: `npx cypress run --browser chrome --headless --env OAUTH2_API_TOKEN=<the API token>`

[TODO](https://github.com/vmware/versatile-data-kit/issues/1610) re-visit when OAuth is agreed on
_**Important note**_: e2e tests require OAuth2 API token to initiate the Code login flow against OAuth endpoint.
*  On _**Unix environments**_(one time): `export OAUTH2_API_TOKEN=<the API token | OAuth_DP_USER_API_TOKEN variable value from CI/CD>`
*  On _**Windows environments**_(each time): `npx cypress open --env OAUTH2_API_TOKEN=<the API token | OAuth_DP_USER_API_TOKEN variable value from CI/CD>`

[Integration Suite] The integration suite of Data Jobs UIs(that runs against TMS Staging env) as part of the Management Service console Integration Tests
is a subset of the E2E cypress tests that are filtered with `--env grepTags=@integration` and `--spec "e2e/integration/**/*.int.spec.js"`
Example run: `npx cypress run --env OAUTH2_API_TOKEN=<the API token>,grepTags=@integration --spec "e2e/integration/**/*.int.spec.js"`

_**Note**_: There are two levels of filtering of the E2E tests that constitutes the Integration Suite:
1. Naming convention for the test filename: *.int.spec.js - to avoid unnecessary scanning and execution of before etc. hooks
2. More granular tag selection: `grepTags=@integration`. e.g.: `it('Manage page - grid search', { tags: '@integration' }, () => {` or
   `describe('Data Jobs Manage Page', { tags: '@integration' }, () => {`


### Local Proxy Configuration

You can check [proxy.config.json](proxy.config.json) file to route the data pipelines to specific server
either local or some other test env.
