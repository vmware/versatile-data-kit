/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { CollectionsUtil } from '../../../utils';

import {
	BaseAction,
	BaseActionWithPayload,
	GenericAction
} from './base.actions';

describe('BaseActionWithPayload', () => {
	describe('Statics::', () => {
		describe('Methods::', () => {
			describe('|of|', () => {
				it('should verify will throw Error', () => {
					// Then
					expect(() => BaseActionWithPayload.of(null, null)).toThrowError(
						'Method have to be overridden in Subclasses.'
					);
				});
			});
		});
	});
});

describe('GenericAction', () => {
	it('should verify instance is created', () => {
		// When
		const instance = new GenericAction(null, null);

		// Then
		expect(instance).toBeDefined();
	});

	describe('Statics::', () => {
		describe('Methods::', () => {
			describe('|of|', () => {
				it('should verify factory method will create instance', () => {
					// Given
					const type = '[component] Create State';
					const payload = { state: [1, 2, 3, 4] };

					// When
					const instance = GenericAction.of(type, payload);

					// Then
					expect(instance).toBeInstanceOf(GenericAction);
					expect(instance).toBeInstanceOf(BaseActionWithPayload);
					expect(instance).toBeInstanceOf(BaseAction);

					expect(instance.type).toEqual(type);
					expect(instance.payload).toBe(payload);
				});

				it('should verify factory method will create instance with Task', () => {
					// Given
					const type = '[component] Submit Data';
					const payload = { state: [10, 20, 30, 40] };
					const task = 'patch_entity';
					const dateNowISO = new Date().toISOString();
					const taskIdentifier = `${task} __ ${dateNowISO}`;
					const dateISOSpy = spyOn(CollectionsUtil, 'dateISO').and.returnValue(
						dateNowISO
					);
					const interpolateStringSpy = spyOn(
						CollectionsUtil,
						'interpolateString'
					).and.returnValue(taskIdentifier);

					// When
					const instance = GenericAction.of(type, payload, task);

					// Then
					expect(instance).toBeInstanceOf(GenericAction);
					expect(instance).toBeInstanceOf(BaseActionWithPayload);
					expect(instance).toBeInstanceOf(BaseAction);

					expect(instance.type).toEqual(type);
					expect(instance.payload).toBe(payload);
					expect(instance.task).toEqual(taskIdentifier);
					expect(dateISOSpy).toHaveBeenCalled();
					// @ts-ignore
					expect(interpolateStringSpy).toHaveBeenCalledWith(
						'%s __ %s',
						task,
						dateNowISO
					);
				});
			});
		});
	});
});
