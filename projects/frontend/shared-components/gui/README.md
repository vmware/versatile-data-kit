The Shared Components contains:

* **[Shared Components Library](projects/shared/README.md)** Library that holds UI Components.
* **[Documentation UI](projects/documentation-ui/src)** Reference UI Wrapper and Documentation Implementation


## Running and Testing

You can use the reference implementation in `projects/documentation-ui` as showcase of the library.
Using `npm link` you can achieve real-time development of the library without the need to upload it to repository

_**Note**_: If you run directly npm install without linking it will tell you that there is no such package.
That's why you need to link it the first time you build your development environment.

Refer to [.gitlab-ci.yml](../../.gitlab-ci.yml) file for correct setup guaranteed to work by automation.
Bug in general the steps are:

0. Set npm registry to use
   * There is .npmrc file in the project that refers to correct registries and provide configuration
   * If something is not working with autoconfiguration, manually set registries

   ```bash
   $ npm config set legacy-peer-deps true
   ```
1. Install Angular Cli and all other dependencies except '@versatiledatakit/shared'
   ```bash
   npm i -g @angular/cli
   ```
   ```bash
   npm ci --omit=optional
   ```
2. Build the shared UI library
   ```bash
   npm run build
   ```
3. Go to the build dir
   ```bash
   cd dist/shared
   ```
4. Link it to local repo
   ```bash
   npm link
   ```
5. Return to project dir
   ```bash
   cd ../../
   ```
6. Create symlink from build artifact to the wrapper ui (documentation-ui)
   ```bash
   npm link @versatiledatakit/shared
   ```
7. Start the wrapper ui application, serve on [http://localhost.vmware.com:4200](http://localhost.vmware.com:4200)
   ```bash
   npm start
   ```

### Linting
Run `npm run lint` to execute lint via [ESLint](https://eslint.org/docs/user-guide/getting-started).

### Running tests

[Unit] Run `npm run test` to execute the unit tests via [Karma](https://karma-runner.github.io).

_**Note**_: Code coverage report will be generated in `reports/coverage`(for the UI Document Wrapper and the Shared Components Library)

_**Note**_: Code coverage report for the Shared UI Components library will be also logged in the Console(and consumed by the CI/CD)
