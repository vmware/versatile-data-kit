/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { galata, test } from '@jupyterlab/galata';
import { expect } from '@playwright/test';
import path from 'path';
import { copyDirectory } from './utils';
const baseJobPath = 'data/convert-test-job-dirty';
test.use({ autoGoto: false });

test.describe('convert job', () => {
  test.beforeEach(async ({ baseURL, page, tmpPath }) => {
    await copyDirectory(
      baseURL!,
      path.resolve(__dirname, baseJobPath),
      path.join(tmpPath, 'convert-job')
    );

    await page.goto(`tree/${tmpPath}`);
  });

  test('success', async ({ page }) => {
    // use VDK menu
    await page.menu.open('VDK');
    await page.locator('#jp-vdk-menu').getByText('Convert').click();
    await page.locator('div').filter({ hasText: 'Convert' });

    // fill the dialog
    await page.getByLabel('Path to job directory:').click();
    const serverPath1 = await page.getServerRoot();
    await page
      .getByLabel('Path to job directory:')
      .fill(serverPath1 + `/tests-convert-job-convert-job-success/convert-job`);
    await page.getByRole('button', { name: 'OK' }).click();

    // agree to continue
    await page
      .locator('div')
      .filter({ hasText: 'Are you sure you want to convert the Data Job' });
    await page.getByRole('button', { name: 'OK' }).click();
    await page.locator('div').filter({ hasText: 'Directory not found' });
    await page.getByRole('button', { name: 'Dismiss' }).click();

    // get message that the job was converted successfully
    await page
      .locator('div')
      .filter({ hasText: 'convert-job was converted to notebook' });
    await page.getByRole('button', { name: 'OK' }).click();

    // select kernel for the newly created notebook
    await page.locator('div').filter({ hasText: 'Select Kernel' });
    await page.getByText('Select kernel for: "Untitled.ipynb"');
    await page.getByRole('button', { name: 'Select', exact: true }).click();

    // go through the notebook content - guide
    await page.locator('pre').filter({
      hasText:
        '### Please go through this guide before continuing with the data job run and dev'
    });
    await page
      .locator('pre')
      .filter({ hasText: '#### Introduction and Preparations' });
    await page.locator('pre').filter({ hasText: '#### Tips:' });

    // go through ipython configuration
    await page
      .locator('pre')
      .filter({ hasText: '%reload_ext vdk.plugin.ipython' })
      .click();
    await page.locator('pre').filter({ hasText: '%reload_VDK' }).click();
    await page
      .locator('pre')
      .filter({ hasText: 'job_input = VDK.get_initialized_job_input()' })
      .click();

    // go through steps
    await page.locator('pre').filter({ hasText: '#### 10_drop_table.sql' });
    await page
      .getByRole('region', { name: 'notebook content' })
      .locator('pre')
      .filter({
        hasText:
          'job_input.execute_query("""DROP TABLE IF EXISTS backup_employees;'
      });
    await page
      .getByRole('region', { name: 'notebook content' })
      .locator('pre')
      .filter({ hasText: '""")' });

    await page.locator('pre').filter({ hasText: '#### 20_create_table.sql' });
    await page
      .getByRole('region', { name: 'notebook content' })
      .locator('pre')
      .filter({
        hasText: 'job_input.execute_query("""CREATE TABLE backup_employees ('
      });
    await page
      .getByRole('region', { name: 'notebook content' })
      .locator('pre')
      .filter({ hasText: 'EmployeeId INTEGER,' });
    await page
      .getByRole('region', { name: 'notebook content' })
      .locator('pre')
      .filter({ hasText: 'LastName NVARCHAR,' });
    await page
      .getByRole('region', { name: 'notebook content' })
      .locator('pre')
      .filter({ hasText: 'FirstName NVARCHAR,' });
    await page
      .getByRole('region', { name: 'notebook content' })
      .locator('pre')
      .filter({ hasText: 'ReportsTo INTEGER,' });
    await page
      .getByRole('region', { name: 'notebook content' })
      .locator('pre')
      .filter({ hasText: 'BirthDate NVARCHAR,' });
    await page
      .getByRole('region', { name: 'notebook content' })
      .locator('pre')
      .filter({ hasText: 'Address NVARCHAR,' });
    await page
      .getByRole('region', { name: 'notebook content' })
      .locator('pre')
      .filter({ hasText: 'Country NVARCHAR,' });
    await page
      .getByRole('region', { name: 'notebook content' })
      .locator('pre')
      .filter({ hasText: 'PostalCode NVARCHAR,' });
    await page
      .getByRole('region', { name: 'notebook content' })
      .locator('pre')
      .filter({ hasText: 'Phone NVARCHAR,' });
    await page
      .getByRole('region', { name: 'notebook content' })
      .locator('pre')
      .filter({ hasText: 'Fax NVARCHAR,' });
    await page
      .getByRole('region', { name: 'notebook content' })
      .locator('pre')
      .filter({ hasText: 'Email NVARCHAR' });
    await page
      .getByRole('region', { name: 'notebook content' })
      .locator('pre')
      .filter({ hasText: ');' });
    await page
      .getByRole('region', { name: 'notebook content' })
      .locator('pre')
      .filter({ hasText: '""")' });

    await page.locator('pre').filter({ hasText: '#### 30_ingest_to_table.py' });
    await page
      .getByRole('region', { name: 'notebook content' })
      .locator('pre')
      .filter({ hasText: 'import sqlite3' });
    await page
      .getByRole('region', { name: 'notebook content' })
      .locator('pre')
      .filter({ hasText: 'def run(job_input):' });
    await page
      .getByRole('region', { name: 'notebook content' })
      .locator('pre')
      .filter({ hasText: 'db_connection = sqlite3.connect(' });
    await page
      .getByRole('region', { name: 'notebook content' })
      .locator('pre')
      .filter({ hasText: '"chinook.db"' });
    await page
      .getByRole('region', { name: 'notebook content' })
      .locator('pre')
      .filter({
        hasText:
          ') # if chinook.db file is not in your current directory, replace "chinook.db"'
      });
    await page
      .getByRole('region', { name: 'notebook content' })
      .locator('pre')
      .filter({ hasText: 'cursor = db_connection.cursor()' });
    await page
      .getByRole('region', { name: 'notebook content' })
      .locator('pre')
      .filter({ hasText: 'cursor.execute("SELECT * FROM employees")' });
    await page
      .getByRole('region', { name: 'notebook content' })
      .locator('pre')
      .filter({ hasText: 'job_input.send_tabular_data_for_ingestion(' });
    await page
      .getByRole('region', { name: 'notebook content' })
      .locator('pre')
      .filter({ hasText: 'cursor,' });
    await page
      .getByRole('region', { name: 'notebook content' })
      .locator('pre')
      .filter({
        hasText:
          'column_names=[column_info[0] for column_info in cursor.description],'
      });
    await page
      .getByRole('region', { name: 'notebook content' })
      .locator('pre')
      .filter({ hasText: 'destination_table="backup_employees",' });
    await page
      .getByRole('region', { name: 'notebook content' })
      .locator('pre')
      .filter({ hasText: ')' });
  });
});
