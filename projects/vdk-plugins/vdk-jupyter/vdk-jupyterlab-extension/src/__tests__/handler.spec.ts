/*
 * Copyright 2023-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { ServerConnection } from '@jupyterlab/services';
import { requestAPI } from '../handler';

jest.mock('@jupyterlab/services', () => {
  const originalModule = jest.requireActual('@jupyterlab/services');
  const mockServerConnection = {
    makeSettings: jest.fn(
      () => ({ baseUrl: 'https://example.com' }) as ServerConnection.ISettings
    ),
    makeRequest: jest.fn(() =>
      Promise.resolve(new Response(JSON.stringify({ message: 'OK' })))
    )
  };
  return {
    ...originalModule,
    ServerConnection: mockServerConnection
  };
});

describe('requestAPI', () => {
  it('calls makeRequest with the correct URL', async () => {
    const response = await requestAPI('test-endpoint');
    expect(ServerConnection.makeRequest).toHaveBeenCalledWith(
      'https://example.com/vdk-jupyterlab-extension/test-endpoint',
      {},
      { baseUrl: 'https://example.com' }
    );
    expect(response).toEqual({ message: 'OK' });
  });

  it('throws a NetworkError when makeRequest throws an error', async () => {
    const mockError = new Error('Network error');
    (ServerConnection.makeRequest as jest.Mock).mockImplementationOnce(() =>
      Promise.reject(mockError)
    );
    await expect(requestAPI('test-endpoint')).rejects.toThrow(mockError);
  });

  it('throws a ResponseError when the response is not OK', async () => {
    const mockResponse = new Response(JSON.stringify({ error: 'Not OK' }), {
      status: 400
    });
    (ServerConnection.makeRequest as jest.Mock).mockImplementationOnce(() =>
      Promise.resolve(mockResponse)
    );
    await expect(requestAPI('test-endpoint')).rejects.toThrow(
      new Error('Bad Request')
    );
  });

  it('parses the response as JSON when the response body is not empty', async () => {
    const mockResponse = new Response(JSON.stringify({ message: 'OK' }));
    (ServerConnection.makeRequest as jest.Mock).mockImplementationOnce(() =>
      Promise.resolve(mockResponse)
    );
    const response = await requestAPI('test-endpoint');
    expect(response).toEqual({ message: 'OK' });
  });

  it('does not parse the response as JSON when the response body is empty', async () => {
    const mockResponse = new Response('', { status: 204 });
    (ServerConnection.makeRequest as jest.Mock).mockImplementationOnce(() =>
      Promise.resolve(mockResponse)
    );
    const response = await requestAPI('test-endpoint');
    expect(response).toEqual('');
  });
});
