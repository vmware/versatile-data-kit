/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { expect, test } from '@jupyterlab/galata';
import { assert } from 'console';

/**
 * Don't load JupyterLab webpage before running the tests.
 * This is required to ensure we capture all log messages.
 */
test.use({ autoGoto: false });

test('should open run job pop up and then cancel the operation', async ({
  page
}) => {
  await page.goto('');
  await page.menu.open('VDK');
  await page.locator('#jp-vdk-menu').getByText('Run').click();
  await page.locator('div').filter({ hasText: 'Run Job' });
  await page.getByRole('button', { name: 'Cancel' }).click();
});

test('should try to run a job with empty input and get error', async ({
  page
}) => {
  await page.goto('');
  await page.menu.open('VDK');
  await page.locator('#jp-vdk-menu').getByText('Run').click();
  await page.locator('div').filter({ hasText: 'Run Job' });
  await page.getByRole('button', { name: 'OK' }).click();
  await page
    .locator('div')
    .filter({ hasText: 'Encountered an error when trying to run the job.' });
  await page.getByRole('button', { name: 'OK' }).click();
});

test('should try to run a job with incorrect data and get a dialog error message', async ({
  page
}) => {
  await page.goto('');
  await page.menu.open('VDK');
  await page.locator('#jp-vdk-menu').getByText('Run').click();
  await page.getByLabel('Path to parent directory:').click();
  await page.getByLabel('Path to parent directory:').fill('/my-folder');
  await page.getByRole('button', { name: 'OK' }).click();
  page.once('dialog', async dialog => {
    console.log(`Dialog message: ${dialog.message()}`);
    dialog.dismiss().catch(() => {});
  });
});

test('should open create job pop up and then cancel the operation', async ({
  page
}) => {
  await page.goto('');
  await page.menu.open('VDK');
  await page.locator('#jp-vdk-menu').getByText('Create').click();
  await page.locator('div').filter({ hasText: 'Create Job' });
  await page.getByRole('button', { name: 'Cancel' }).click();
});

test('should try to create a job with empty input and get error', async ({
  page
}) => {
  await page.goto('');
  await page.menu.open('VDK');
  await page.locator('#jp-vdk-menu').getByText('Create').click();
  await page.locator('div').filter({ hasText: 'Run Job' });
  await page.getByRole('button', { name: 'OK' }).click();
  await page
    .locator('div')
    .filter({ hasText: 'Encountered an error when creating the job.' });
  await page.getByRole('button', { name: 'OK' }).click();
});

test('should try to create a job with incorrect input and get error', async ({
  page
}) => {
  await page.goto('');
  await page.menu.open('VDK');
  await page.locator('#jp-vdk-menu').getByText('Create').click();
  await page.getByLabel('Local').check();
  await page.getByLabel('Job name:').click();
  await page.getByLabel('Job name:').fill('first-job');
  await page.getByLabel('Job team:').click();
  await page.getByLabel('Job team:').fill('example-team');
  await page.getByLabel('Path to parent directory:').click();
  await page.getByLabel('Path to parent directory:').fill('sdfgsdfsdfsd');
  await page.getByRole('button', { name: 'OK' }).click();
  await page
    .locator('div')
    .filter({ hasText: 'Encountered an error when creating the job.' });
  await page.getByRole('button', { name: 'OK' }).click();
});

test('should open delete job pop up and then cancel the operation', async ({
  page
}) => {
  await page.goto('');
  await page.menu.open('VDK');
  await page.locator('#jp-vdk-menu').getByText('Delete').click();
  await page.locator('div').filter({ hasText: 'Delete Job' });
  await page.getByRole('button', { name: 'Cancel' }).click();
});

test('should open delete job confirmation pop up', async ({ page }) => {
  await page.goto('');
  await page.menu.open('VDK');
  await page.locator('#jp-vdk-menu').getByText('Delete').click();
  await page.locator('div').filter({ hasText: 'Delete Job' });
  await page.getByRole('button', { name: 'OK' }).click();
  // this is tested with empty input that's why the message is with null
  await page.locator('div').filter({
    hasText: 'Do you really want to delete the job with name null from null?'
  });
  await page.getByRole('button', { name: 'Cancel' }).click();
});

test('should try to delete a job with empty input and get error', async ({
  page
}) => {
  await page.goto('');
  await page.menu.open('VDK');
  await page.locator('#jp-vdk-menu').getByText('Delete').click();
  await page.locator('div').filter({ hasText: 'Delete Job' });
  await page.getByRole('button', { name: 'OK' }).click();
  // this is tested with empty input that's why the message is with null
  await page
    .locator('div')
    .filter({
      hasText: 'Do you really want to delete the job with name null from null?'
    })
    .first()
    .click();
  await page.getByRole('button', { name: 'Yes' }).click();
  await page
    .locator('div')
    .filter({ hasText: 'Encountered an error when deleting the job.' });
});

test('should open download job pop up and then cancel the operation', async ({
  page
}) => {
  await page.goto('');
  await page.menu.open('VDK');
  await page.locator('#jp-vdk-menu').getByText('Download').click();
  await page.locator('div').filter({ hasText: 'Download Job' });
  await page.getByRole('button', { name: 'Cancel' }).click();
});

test('should try download operation with empty input and get error', async ({
  page
}) => {
  await page.goto('');
  await page.menu.open('VDK');
  await page.locator('#jp-vdk-menu').getByText('Download').click();
  await page.locator('div').filter({ hasText: 'Download Job' });
  await page.getByRole('button', { name: 'OK' }).click();
  await page.locator('div').filter({
    hasText: 'Encountered an error when trying to download the job. '
  });
  await page.getByRole('button', { name: 'OK' }).click();
});
