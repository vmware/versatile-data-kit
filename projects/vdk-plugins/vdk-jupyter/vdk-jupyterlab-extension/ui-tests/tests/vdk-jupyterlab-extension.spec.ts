/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { expect, test } from '@jupyterlab/galata';

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
  await page.getByLabel('Path to job directory:').click();
  await page.getByLabel('Path to job directory:').fill('/my-folder');
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
  await page.getByLabel('Job name:').click();
  await page.getByLabel('Job name:').fill('first-job');
  await page.getByLabel('Job team:').click();
  await page.getByLabel('Job team:').fill('example-team');
  await page.getByLabel('Path to job directory:').click();
  await page.getByLabel('Path to job directory:').fill('sdfgsdfsdfsd');
  await page.getByRole('button', { name: 'OK' }).click();
  await page
    .locator('div')
    .filter({ hasText: 'Encountered an error when creating the job.' });
  await page.getByRole('button', { name: 'OK' }).click();
});

test('should try to create a job successfully', async ({ page }) => {
  await page.goto('');
  await page.menu.open('VDK');
  await page.locator('#jp-vdk-menu').getByText('Create').click();
  await page.getByLabel('Job name:').click();
  await page.getByLabel('Job name:').fill('first-job');
  await page.getByLabel('Job team:').click();
  await page.getByLabel('Job team:').fill('my-team');
  await page.getByRole('button', { name: 'OK' }).click();
  page.on('dialog', async dialog => {
    expect(dialog.type()).toContain('alert');
    expect(dialog.message()).toContain(
      'Job with name first-job was created successfully!'
    );
    await dialog.accept();
  });
  await page.getByRole('button', { name: 'OK' }).click();
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

test('should create an init cell when opening a new notebook', async ({
  page
}) => {
  await page.goto('');
  await page.locator('.jp-LauncherCard-icon').first().click();
  await expect(
    page.getByText(`job_input = VDK.get_initialized_job_input()`)
  ).toBeVisible();
});
