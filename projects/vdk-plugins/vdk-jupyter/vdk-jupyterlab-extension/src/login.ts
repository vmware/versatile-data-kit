/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { requestAPI } from './handler';

export async function startLogin() {
  const redirect_url = await requestAPI<any>(
    'login?' + 'origin=' + encodeURIComponent(window.location.origin),
    {
      method: 'GET'
    }
  );
  console.log('open login window with redirect url: ' + redirect_url);
  const oauthWindow = window.open(
    redirect_url,
    'oauthWindow',
    'width=800,height=500'
  );
  if (oauthWindow == null) {
    console.log('Failed to open OAuth2 login window');
    return;
  }
}
