/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import {
  fetchTokenLocation,
  getTokenFromLocation,
  sendTokenToServer,
  setupTokenCheckInterval
} from '../tokenUpdate';
import { requestAPI } from '../handler';

// Mocking requestAPI
jest.mock('../handler', () => ({
  requestAPI: jest.fn()
}));

let store: { [key: string]: string } = {};
const mockLocalStorage = (function () {
  return {
    getItem: jest.fn(key => {
      return store[key] || null;
    }),
    setItem: jest.fn((key, value) => {
      console.log(
        `Setting key "${key}" with value "${value}" in mock localStorage.`
      );
      store[key] = value;
    }),
    clear: jest.fn(() => {
      store = {};
    })
  };
})();

Object.defineProperty(window, 'localStorage', {
  value: mockLocalStorage
});
Object.defineProperty(window.top, 'localStorage', {
  value: mockLocalStorage
});

describe('VDK Access Token Handling', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    jest.restoreAllMocks();
    jest.useFakeTimers();
    mockLocalStorage.clear();
  });
  afterEach(() => {
    jest.clearAllMocks();
    jest.restoreAllMocks();
    mockLocalStorage.clear();
  });

  it('fetches token location', async () => {
    (requestAPI as jest.Mock).mockResolvedValue({
      storageType: 'localStorage',
      key: 'token',
      valuePath: 'path'
    });

    const location = await fetchTokenLocation();

    expect(location).toEqual({
      storageType: 'localStorage',
      key: 'token',
      valuePath: 'path'
    });
    expect(requestAPI).toHaveBeenCalledWith('vdkAccessTokenLocation', {
      method: 'GET'
    });
  });

  it('handles errors when fetching token location', async () => {
    (requestAPI as jest.Mock).mockRejectedValue(
      new Error('Failed fetch token location request')
    );

    await expect(fetchTokenLocation()).rejects.toThrow(
      'Failed fetch token location request'
    );

    expect(requestAPI).toHaveBeenCalledWith('vdkAccessTokenLocation', {
      method: 'GET'
    });
  });

  it('gets token from localStorage', async () => {
    mockLocalStorage.setItem(
      'whatever',
      JSON.stringify({ token: { path: 'myToken' } })
    );

    const token = await getTokenFromLocation({
      storageType: 'localStorage',
      key: 'whatever',
      valuePath: 'token.path'
    });

    expect(token).toEqual('myToken');
  });

  it('handles non-existent token paths in localStorage', async () => {
    mockLocalStorage.setItem('token', JSON.stringify({}));

    const token = await getTokenFromLocation({
      storageType: 'localStorage',
      key: 'token',
      valuePath: 'path'
    });

    expect(token).toBeNull();
  });

  it('sends token to server', async () => {
    (requestAPI as jest.Mock).mockResolvedValue(true);

    await sendTokenToServer('myToken');

    expect(requestAPI).toHaveBeenCalledWith('vdkAccessToken', {
      body: JSON.stringify({ token: 'myToken' }),
      method: 'POST'
    });
  });

  it('handles errors when sending token to server', async () => {
    (requestAPI as jest.Mock).mockRejectedValue(
      new Error('Failed sending token request')
    );

    const consoleErrorSpy = jest
      .spyOn(console, 'error')
      .mockImplementation(() => {});
    await sendTokenToServer('myToken');
    consoleErrorSpy.mockRestore();

    expect(requestAPI).toHaveBeenCalledWith('vdkAccessToken', {
      body: JSON.stringify({ token: 'myToken' }),
      method: 'POST'
    });
  });

  it('sets up token check interval if initial token location is found', async () => {
    (requestAPI as jest.Mock).mockName('requestAPI').mockResolvedValue({
      storageType: 'localStorage',
      key: 'token_key',
      valuePath: 'path'
    });

    // let getItemCounter = 0
    // mockLocalStorage.getItem.mockImplementation((key) => {
    //   if (key === 'token_key') {
    //     if (getItemCounter == 0) {
    //       getItemCounter++;
    //       return JSON.stringify( { path: 'myToken' } ) ;
    //     } else {
    //       return JSON.stringify( { path: 'myTokenUpdated' } ) ;
    //     }
    //   } else {
    //     return store[key] || null
    //   }
    // })
    mockLocalStorage.setItem('token_key', JSON.stringify({ path: 'myToken' }));

    await setupTokenCheckInterval();

    expect(requestAPI).toHaveBeenCalledWith('vdkAccessTokenLocation', {
      method: 'GET'
    });

    expect(requestAPI as jest.Mock).toHaveBeenCalledWith('vdkAccessToken', {
      body: JSON.stringify({ token: 'myToken' }),
      method: 'POST'
    });
  });
});
