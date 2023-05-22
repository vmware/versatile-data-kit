/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/// <reference types="cypress" />

import { BasePagePO } from '../../support/pages/base/base-page.po';
import { GetStartedPagePO } from '../../support/pages/get-started/get-started-page.po';

describe('Routing for pages', () => {
    describe('smoke', { tags: ['@smoke'] }, () => {
        it('navigates to get-started page when explore page route is ignored', () => {
            BasePagePO.executeCypressCommand(
                'appConfigInterceptorDisableExploreRoute'
            );
            // wait for login
            BasePagePO.wireUserSession();
            BasePagePO.initInterceptors();
            BasePagePO.navigateTo();
            // go to explore page url
            cy.visit('/explore/data-jobs');
            // should navigate to get-started instead
            cy.location().should((l) =>
                expect(l.pathname).to.equal('/get-started')
            );
        });
    });
});
