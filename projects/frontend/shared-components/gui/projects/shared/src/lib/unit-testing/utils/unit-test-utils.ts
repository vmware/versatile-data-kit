/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/* eslint-disable @typescript-eslint/naming-convention,@typescript-eslint/no-explicit-any */

/**
 * ** Fake method to mock methods.
 *
 * e.g.
 *      .and.callFake(CallFake)
 *
 *
 */
export const CallFake = (..._args: any[]): any => {
	// No-op.
};

/**
 * ** Utility to trigger keyboard event from some HTMLElement.
 */
export const triggerKeyboardEvent = (
	el: HTMLElement,
	type: string,
	keyCode: string
) => {
	const e = new KeyboardEvent(type, {
		code: keyCode,
		bubbles: true,
		cancelable: true
	});

	el.dispatchEvent(e);
};
