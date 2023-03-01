/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { TIE_SWAGGER_DOC_LOCATION, UrlUtil } from './url.util';

const TEST_VALUE_NO_FORWARD_SLASH = 'https://some_value';

const TEST_VALUE_WITH_FORWARD_SLASH = 'https://some_value/';

describe('UrlUtil', () => {
	it('normalize Endpoint with Empty input', () => {
		expect(UrlUtil.normalizeEndpoint(null)).toEqual('');
	});

	it('normalize Endpoint with no Forward Slash at the end', () => {
		expect(UrlUtil.normalizeEndpoint(TEST_VALUE_NO_FORWARD_SLASH)).toEqual(
			TEST_VALUE_WITH_FORWARD_SLASH
		);
	});

	it('normalize Endpoint with Forward Slash at the end', () => {
		expect(UrlUtil.normalizeEndpoint(TEST_VALUE_WITH_FORWARD_SLASH)).toEqual(
			TEST_VALUE_WITH_FORWARD_SLASH
		);
	});

	it('constructTieSwaggerUiEndpoint with Empty Input', () => {
		expect(UrlUtil.constructTieSwaggerUiEndpoint(null)).toEqual(
			TIE_SWAGGER_DOC_LOCATION
		);
	});

	it('constructTieSwaggerUiEndpoint with Valid Input', () => {
		expect(
			UrlUtil.constructTieSwaggerUiEndpoint(TEST_VALUE_WITH_FORWARD_SLASH)
		).toEqual(TEST_VALUE_WITH_FORWARD_SLASH + TIE_SWAGGER_DOC_LOCATION);
	});
});
