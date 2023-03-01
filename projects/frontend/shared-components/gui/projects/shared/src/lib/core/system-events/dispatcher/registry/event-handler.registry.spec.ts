/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { SystemEventHandlerRegistry } from './event-handler.registry';

class TestClazz {}

describe('SystemEventHandlerRegistry', () => {
	describe('Statics::', () => {
		describe('Getters::()', () => {
			describe('|instance|', () => {
				it('should verify will return always same Repository instance', () => {
					// When
					const r1 = SystemEventHandlerRegistry.instance;
					const r2 = SystemEventHandlerRegistry.instance;
					const r3 = SystemEventHandlerRegistry.instance;

					// Then
					expect(r2).toBe(r1);
					expect(r3).toBe(r2);
				});
			});
		});

		describe('Methods::()', () => {
			describe('|register|', () => {
				it('should verify will execute register and execute methods in Registry instance', () => {
					// Given
					// @ts-ignore
					const spyRegister = spyOn<SystemEventHandlerRegistry, any>(
						SystemEventHandlerRegistry.instance,
						'register'
					).and.callThrough();
					// @ts-ignore
					const spyExecute = spyOn<SystemEventHandlerRegistry, any>(
						SystemEventHandlerRegistry.instance,
						'execute'
					).and.callThrough();
					const handler = () => Promise.resolve(true);
					const handlerClassInstance = {};

					// When
					SystemEventHandlerRegistry.register(
						'SE_Send_Email',
						handler,
						handlerClassInstance
					);

					// Then
					// @ts-ignore
					expect(spyRegister).toHaveBeenCalledWith(
						'SE_Send_Email',
						handler,
						handlerClassInstance,
						null
					);
					// @ts-ignore
					expect(spyExecute).toHaveBeenCalledWith(
						'SE_Send_Email',
						handler,
						jasmine.any(Function),
						handlerClassInstance,
						null
					);
				});

				it('should verify will register handler in Registry', () => {
					// Given
					const event = 'SE_Create_Job';
					const handlerRef = () => Promise.resolve(false);
					const clazzInstance = new TestClazz();

					// When
					SystemEventHandlerRegistry.register(event, handlerRef, clazzInstance);

					// Then
					// eslint-disable-next-line @typescript-eslint/dot-notation
					const registry = SystemEventHandlerRegistry.instance['handlers'];
					const handlers = registry.get(event);
					expect(Array.from(handlers.values())).toContain({
						handlerRef,
						handlerFilterExpression: null,
						handlerClassInstance: clazzInstance
					});
				});
			});

			describe('|unregister|', () => {
				it('should verify will execute unregister and execute methods in Registry instance', () => {
					// Given
					// @ts-ignore
					const spyUnregister = spyOn<SystemEventHandlerRegistry, any>(
						SystemEventHandlerRegistry.instance,
						'unregister'
					).and.callThrough();
					// @ts-ignore
					const spyExecute = spyOn<SystemEventHandlerRegistry, any>(
						SystemEventHandlerRegistry.instance,
						'execute'
					).and.callThrough();
					const event = 'SE_Delete_Job';
					const handler = () => Promise.resolve(true);

					// When
					SystemEventHandlerRegistry.unregister(event, handler);

					// Then
					// @ts-ignore
					expect(spyUnregister).toHaveBeenCalledWith(event, handler);
					// @ts-ignore
					expect(spyExecute).toHaveBeenCalledWith(
						event,
						handler,
						jasmine.any(Function)
					);
				});

				it('should verify will remove handler in Registry after it is added', () => {
					// Given
					// eslint-disable-next-line @typescript-eslint/dot-notation
					const registry = SystemEventHandlerRegistry.instance['handlers'];
					const event = 'SE_Update_Job';
					const handlerRef = () => Promise.resolve(true);
					const clazzInstance = new TestClazz();

					// When 1
					SystemEventHandlerRegistry.register(event, handlerRef, clazzInstance);

					// Then 1
					const handlers = registry.get(event);
					expect(Array.from(handlers.values())).toContain({
						handlerRef,
						handlerFilterExpression: null,
						handlerClassInstance: clazzInstance
					});

					// When 2
					SystemEventHandlerRegistry.unregister(event, handlerRef);

					// Then 2
					// eslint-disable-next-line @typescript-eslint/dot-notation
					expect(Array.from(handlers.values())).not.toContain({
						handlerRef,
						handlerFilterExpression: null,
						handlerClassInstance: clazzInstance
					});
				});
			});

			describe('|findHandlerByReference|', () => {
				it('should verify will find Handler by its reference', () => {
					// Given
					const event = 'SE_Notify_Users';
					const handlerRef = () => Promise.resolve(true);
					const clazzInstance = new TestClazz();

					// When
					SystemEventHandlerRegistry.register(event, handlerRef, clazzInstance);
					const record = SystemEventHandlerRegistry.findHandlerByReference(
						event,
						handlerRef,
						clazzInstance
					);

					// Then
					expect(record).toEqual({
						active: true,
						handlerRef,
						handlerRecord: {
							handlerRef,
							handlerFilterExpression: null,
							handlerClassInstance: clazzInstance
						}
					});
				});
			});

			describe('|getPreparedArrayOfHandlers|', () => {
				it('should verify will return empty Array when there is no Handlers for Event', () => {
					// Given
					const event = 'SE_Clean_Jobs';

					// When
					const handlers =
						SystemEventHandlerRegistry.getPreparedArrayOfHandlers(event);

					// Then
					expect(handlers).toEqual([]);
				});

				it('should verify will return 3 handlers for given Event', () => {
					// Given
					const event = 'SE_Log_Incident';
					const handlerRef1 = () => Promise.resolve(true);
					const handlerRef2 = () => Promise.resolve(true);
					const handlerRef3 = () => Promise.resolve(true);
					const clazzInstance = new TestClazz();

					SystemEventHandlerRegistry.register(
						event,
						handlerRef1,
						clazzInstance
					);
					SystemEventHandlerRegistry.register(
						event,
						handlerRef2,
						clazzInstance
					);
					SystemEventHandlerRegistry.register(
						event,
						handlerRef3,
						clazzInstance
					);

					// When
					const handlers =
						SystemEventHandlerRegistry.getPreparedArrayOfHandlers(event);

					// Then
					expect(handlers).toEqual([
						{
							handlerRef: handlerRef1,
							handlerClassInstance: clazzInstance,
							handlerFilterExpression: null
						},
						{
							handlerRef: handlerRef2,
							handlerClassInstance: clazzInstance,
							handlerFilterExpression: null
						},
						{
							handlerRef: handlerRef3,
							handlerClassInstance: clazzInstance,
							handlerFilterExpression: null
						}
					]);
				});

				it('should verify will return 3 handlers in reverse order for given Event', () => {
					// Given
					const event = 'SE_Clean_Session';
					const handlerRef11 = () => Promise.resolve(true);
					const handlerRef22 = () => Promise.resolve(true);
					const handlerRef33 = () => Promise.resolve(true);
					const clazzInstance = new TestClazz();

					SystemEventHandlerRegistry.register(
						event,
						handlerRef11,
						clazzInstance
					);
					SystemEventHandlerRegistry.register(
						event,
						handlerRef22,
						clazzInstance
					);
					SystemEventHandlerRegistry.register(
						event,
						handlerRef33,
						clazzInstance
					);

					// When
					const handlers =
						SystemEventHandlerRegistry.getPreparedArrayOfHandlers(event, true);

					// Then
					expect(handlers).toEqual([
						{
							handlerRef: handlerRef33,
							handlerClassInstance: clazzInstance,
							handlerFilterExpression: null
						},
						{
							handlerRef: handlerRef22,
							handlerClassInstance: clazzInstance,
							handlerFilterExpression: null
						},
						{
							handlerRef: handlerRef11,
							handlerClassInstance: clazzInstance,
							handlerFilterExpression: null
						}
					]);
				});
			});
		});
	});
});
