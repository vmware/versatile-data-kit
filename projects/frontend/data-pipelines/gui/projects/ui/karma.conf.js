/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

// Karma configuration file, see link for more information
// https://karma-runner.github.io/1.0/config/configuration-file.html

module.exports = function (config) {
    config.set({
        basePath: "",
        frameworks: ["jasmine", "@angular-devkit/build-angular"],
        plugins: [
            require("karma-jasmine"),
            require("karma-chrome-launcher"),
            require("karma-jasmine-html-reporter"),
            require("karma-junit-reporter"),
            require("karma-coverage"),
            require("@angular-devkit/build-angular/plugins/karma"),
        ],
        client: {
            jasmine: {
                // you can add configuration options for Jasmine here
                // the possible options are listed at https://jasmine.github.io/api/edge/Configuration.html
                // for example, you can disable the random execution with `random: false`
                // or set a specific seed with `seed: 4321`
            },
            clearContext: false, // leave Jasmine Spec Runner output visible in browser
        },
        coverageReporter: {
            dir: require("path").join(
                __dirname,
                "../../reports/coverage/data-pipelines-ui"
            ),
            reporters: [
                //Code coverage - output only in HTML file
                { type: "html" },
                { type: "text-summary" },
                { type: "lcovonly" },
            ],
            check: {
                global: {
                    lines: 20,
                },
            },
        },
        jasmineHtmlReporter: {
            suppressAll: true, // removes the duplicated traces
        },
        junitReporter: {
            outputDir: require("path").join(
                __dirname,
                "../../reports/test-results/data-pipelines-ui"
            ),
            outputFile: "unit-tests.xml",
            useBrowserName: false,
        },
        reporters: ["progress", "junit", "coverage"],
        port: 9876,
        colors: true,
        logLevel: config.LOG_INFO,
        autoWatch: true,
        browsers: ["ChromeHeadless"],
        customLaunchers: {
            ChromeHeadless_No_Sandbox: {
                base: "ChromeHeadless",
                flags: ["--no-sandbox"],
            },
        },
        singleRun: false,
        restartOnFileChange: true,
    });
};
