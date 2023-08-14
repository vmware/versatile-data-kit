/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { requestAPI } from './handler';

export type TokenLocation = {
  /**
   * The type of the storage. For now just localStorage
   */
  storageType: string;
  /**
   * The key where the token is stored
   */
  key: string;
  /**
   * The path in the value (json) to the actual token
   */
  valuePath: string;
};

export async function fetchTokenLocation(): Promise<TokenLocation | null> {
  const data = await requestAPI<any>('vdkAccessTokenLocation', {
    method: 'GET'
  });
  if (data) {
    return data;
  } else {
    console.log('No token location from the server returned.');
    return null;
  }
}

function safeJSONParse<T = any>(value: string | null): T | null {
  try {
    return JSON.parse(value || 'null');
  } catch {
    return null;
  }
}

export async function getTokenFromLocation(
  location: TokenLocation
): Promise<string | null> {
  if (location.storageType === 'localStorage') {
    let item = safeJSONParse(window.top.localStorage.getItem(location.key));
    let pathParts = location.valuePath.split('.');
    return pathParts.reduce((current, key) => {
      return current && key in current ? current[key] : null;
    }, item);
  }
  return null;
}

export async function sendTokenToServer(token: string): Promise<void> {
  try {
    await requestAPI<any>('vdkAccessToken', {
      body: JSON.stringify({ token }),
      method: 'POST'
    });
  } catch (error) {
    console.error("Couldn't send token to server", error);
  }
}

export const CHECK_INTERVAL_MS = 60000;

async function getTokenLocationFromCacheOrFetch(): Promise<TokenLocation | null> {
  const tokenLocationString = window.localStorage.getItem(
    'vdk.cache.tokenLocation'
  );
  if (tokenLocationString) {
    return safeJSONParse(tokenLocationString);
  }

  const fetchedTokenLocation = await fetchTokenLocation();
  if (fetchedTokenLocation) {
    window.localStorage.setItem(
      'vdk.cache.tokenLocation',
      JSON.stringify(fetchedTokenLocation)
    );
  }

  return fetchedTokenLocation;
}

async function sendTokenIfNew(token: string) {
  const cachedToken = window.localStorage.getItem('vdk.cache.token');
  if (token !== cachedToken) {
    console.debug('New VDK token found. Sending it to the server');
    await sendTokenToServer(token);
    console.debug('Sent VDK token to the server');
    window.localStorage.setItem('vdk.cache.token', token);
  }
}

/**
 * Checks for the presence of a token and sends it to the server if found.
 *
 * This function fetches the token location, retrieves the token from the specified location,
 * and sends the token to the server.
 *
 * @returns {Promise<string>} - Returns the token location. If the token is not found then we should not schedule regular update.
 */
async function checkToken() {
  const tokenLocation = await getTokenLocationFromCacheOrFetch();
  console.debug('Checking VDK token location:', JSON.stringify(tokenLocation));

  if (tokenLocation) {
    const token = await getTokenFromLocation(tokenLocation);
    if (token) {
      await sendTokenIfNew(token);
    }
  }

  return tokenLocation;
}

/**
 * Setups regularly to update the access token from the parent
 */
export async function setupTokenCheckInterval() {
  const initialTokenLocation = await checkToken(); // Run immediately

  if (initialTokenLocation) {
    console.log(
      'Initial token location is ' + JSON.stringify(initialTokenLocation)
    );
    console.log(
      'Schedule regular update every ' + CHECK_INTERVAL_MS + ' milliseconds'
    );
    setInterval(checkToken, CHECK_INTERVAL_MS);
  } else {
    console.log('No token location. Disable regular token update');
  }
}
