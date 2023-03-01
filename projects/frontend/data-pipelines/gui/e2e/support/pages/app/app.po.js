/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { DataPipelinesBasePO } from "../../application/data-pipelines-base.po";

export class AppPage extends DataPipelinesBasePO {
    static getPage() {
        return new AppPage();
    }

    static navigateTo() {
        cy.visit("/");
    }

    getMainTitle() {
        return cy.get("[data-cy=app-main-title]");
    }
}
