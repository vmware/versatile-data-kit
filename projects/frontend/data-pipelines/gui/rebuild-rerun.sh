#!/bin/bash
# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

# Ease with script hot deployments while developing
rm -rf node_modules/@versatiledatakit/data-pipelines
rm -rf dist/data-pipelines

ng build data-pipelines
npm link @versatiledatakit/data-pipelines
ng serve --host localhost.vmware.com --port 4200 --proxy-config proxy.config.json
