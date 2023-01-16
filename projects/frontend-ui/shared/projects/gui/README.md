The Shared Components contains:

* **[Shared Components Library](projects/shared/README.md)** Library that holds UI Components.

## Running and Testing

0. Install Angular Cli
   ```bash
   npm i -g @angular/cli
   ```
1. install dependencies 
   ```bas
   npm ci --omit=optional
   ```
2. Build the shared UI library
   ```bash
   npm run build
   ```

### Linting
Run `npm run lint` to execute lint via [ESLint](https://eslint.org/docs/user-guide/getting-started).

### Running tests

[Unit] Run `npm run test` to execute the unit tests via [Karma](https://karma-runner.github.io).

_**Note**_: Code coverage report will be generated in `reports/coverage`(for the UI Document Wrapper and the Shared Components Library)

_**Note**_: Code coverage report for the Shared UI Components library will be also logged in the Console(and consumed by the CI/CD)
