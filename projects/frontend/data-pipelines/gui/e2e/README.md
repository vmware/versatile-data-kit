## Setup for running Cypress tests on local environment ##

1. ### Install npm packages using package.json in the root of the project with `npm install --omit=optional` ###
   * If installed for Data Pipelines, this step could be skipped, because e2e tests used the same node_modules from the root `gui` project


2. ### Set Cypress environment variables - for more information [follow](https://docs.cypress.io/guides/guides/environment-variables) ###
    * `OAUTH2_API_TOKEN` - __required__ variable that must be set with CSP refresh token issued from CSP-STG console in order tests to be executed
    * `CYPRESS_TERMINAL_LOGS` - __required__ variable with value location where console logs should be persisted, relatively to root of the [gui](../) project
    * `grepTags` - __optional__ variable with default empty, to reset any cypress.json configuration
      * for more information read official github documentation [Readme.md](https://github.com/cypress-io/cypress-grep/blob/main/README.md)


3. ### Check [cypress.json](../cypress.json) to view configuration for Cypress framework ###
   1. __baseUrl__ property is one of the most commonly changed and instructs against which domain Cypress tests should be executed
      * default value is `http://localhost.vmware.com:4200` but could be set to different path as well
      * If property is set to `http://localhost.vmware.com:4200` be sure that Data Pipelines gui is started locally through Angular CLI with `npm start` or `ng serve` with required parameters
   2. __env__ property holds object with different variables used in e2e tests like urls.. - for more information [follow](https://docs.cypress.io/guides/guides/environment-variables)
      1. __grepTags__ property instruct plugin cypress-grep what to execute, what to skip
         * default value is `` which instructs to not exclude or include anything from local run
         * for more information read official github documentation [Readme.md](https://github.com/cypress-io/cypress-grep/blob/main/README.md)


4. ### Execute/Run tests (choose one of the commands bellow, they exclude each other) ###
   1. `cypress open --env <key1>=<value1>,<key2>=<value2>` - will open Cypress dashboard where you could see Cypress configuration and other nice information and also realtime tests execution and their progress and steps
      * command
        ```bash
         cypress open --env grepTags=<changeme>,OAUTH2_API_TOKEN=<changeme>,CYPRESS_TERMINAL_LOGS='./e2e/logs'
        ```
   2. `cypress run --env <key1>=<value1>,<key2>=<value2>` - will execute Cypress test in headless mode, but all screenshots on test failure and video of progress will be recorded and persisted in directories
      * command
        ```bash
         cypress run --browser chrome --env grepTags=<changeme>,OAUTH2_API_TOKEN=<changeme>,CYPRESS_TERMINAL_LOGS='./e2e/logs'
        ```

5. ### Cypress e2e tests directory organization ###
   1. __[fixtures](./fixtures)__ - all fixtures which are used from tests, generic goes inside [base](./fixtures/base) and other goes in dirs similar to their url segments in SuperCollider console
   2. __[integration](./integration)__ - tests suites and actual e2e tests where every suite goes in dirs similar to their url segments in SuperCollider console
   3. __[plugins](./plugins)__ - Cypress custom plugin wrote by us to speed up before(setup) hook and execute pre-requisites on lower level where parallelism is achievable
      1. __[plugins/helpers](./plugins/helpers)__ has multiple helper functions that could be use as asynchronous tasks through Cypress plugins or directly in tests suites as util helpers
   4. __[support](./support)__ -
      1. __[support/commands.js](./support/commands.js)__ is the root file where root Cypress commands are added and exposed through Cypress API for usage in PageObjects or test suites
      2. __[support/index.js](./support/index.js)__ public api file where commands are registered from previous, and to register different 3rd party plugins and extension on top of Cypress framework
      3. __[support/pages](./support/pages)__ holds actual PageObjects representation for UI pages used in test suites, following PageObject pattern, where every PageObject class goes in dirs similar to their url segments in SuperCollider console in sync with dirs organization in [integration](./integration) dir where inheritance is actively use
         1. __[BasePagePO](e2e/support/pages/base/base-page.po.js)__ is the root class which is inherited from all PageObject classes and down there hierarchical inheritance could be use too like [ManagePagePO](./support/pages/manage/manage-page.po.js) inherited from every PageObject under the manage segment, etc...
      4. __[support/helpers](./support/helpers)__ holds constants with values that are used in fixtures and tests for easier usage of names, values, etc..
   5. __[hars](./hars)__ dir has all har files from tests execution has recorded every http request response to better triage failures
   6. __[logs](./logs)__ dir has all output files from tests execution console, with dir organization same like [integration](./integration) dir organization
   7. __[screenshots](./screenshots)__ dir has pictures for every failed tests in the time of the failure, with dir organization same like [integration](./integration) dir organization
   8. __[videos](./videos)__ dir has all videos for every test suite execution saved in separate file, with dir organization same like [integration](./integration) dir organization
