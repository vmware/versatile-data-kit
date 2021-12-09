

## Directory layout

### vdk

Contains unit tests of the project.
See https://martinfowler.com/bliki/UnitTest.html

As a rule of thump the whole unit test suite should finish in under a minute. If we grow big maybe a few minutes.

Each file is named test_orignal_file_name and follow same package structure as original file under test.

### functional

Contains functional test.
See https://en.wikipedia.org/wiki/Functional_testing

They test concrete (usually user facing in some way) functionality.<br>
For example under function/run - it would test different scenarios for running data jobs.

Functional tests here must not have external dependencies (should be able to run them offline)<br>
Functional tests should be black box - should break only if behaviour / side effects being verified change but not if code is refactored.
