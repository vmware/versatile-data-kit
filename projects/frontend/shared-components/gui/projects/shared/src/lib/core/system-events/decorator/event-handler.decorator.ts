/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/* eslint-disable prefer-arrow/prefer-arrow-functions,
                  @typescript-eslint/naming-convention,
                  max-len
*/

import 'reflect-metadata';

import { Expression } from '../../../common';

import { SystemEvent } from '../event';
import {
	SystemEventHandlerRef,
	SystemEventMetadataRecords
} from '../dispatcher/models';

import { SYSTEM_EVENTS_METADATA_KEY } from './models';

/**
 * ** Decorator to register method as SystemEvent Handler.
 *
 *   - Annotation should be added before method declaration.
 *   - It will annotate method as Handler for provided SystemEvent or SystemEvents.
 *   - Optionally filter expression could be provide to filter Handler execution only when expression requirements are met.
 *   - Depends of the SystemEvent Handler should return Promise or not.
 *        - Blocking SystemEvents require Promise, Non-Blocking doesn't.
 *        - Recommended is every Handler to return Promise to avoid Runtime exception in signature change on Invoker side.
 *   - For Dispatcher and Handler Class decorator read JSDoc {@link SystemEventDispatcher} {@link SystemEventHandlerClass}
 *
 * @example
 *
 *   `@Injectable()`
 *   `@SystemEventHandlerClass()`
 *    export class LoggerService {
 *
 *      // some properties, methods
 *
 *     `@SystemEventHandler('SE_Log')` // NON-BLOCKING SystemEvent
 *      public _logHandler(payload: { message: string }, eventId?: SystemEvent): void {
 *        // Do something
 *      }
 *    }
 *
 *   `@Injectable`
 *   `@SystemEventHandlerClass()`
 *    export class DataJobService {
 *      constructor(private readonly httpClient: HttpClient) {}
 *
 *     `@SystemEventHandler('SE_Create_Job')` // BLOCKING SystemEvent
 *      public _createJobHandler(payload: { baseUrl: string; jobName: string; jobCreator: string }): Promise<boolean> {
 *
 *        // Do something
 *
 *        // Possibility to make asynchronous calls,
 *        // while Invoker is waiting until every Handler is executed,
 *        // and execution flow is returned
 *        return this
 *                  .httpClient
 *                  .post(`${baseUrl}/create`, {jobName, jobCreator})
 *                  .pipe(
 *                    map((v) => !!v) // do some transformation and return boolean
 *                  )
 *                  .toPromise(); // cast to Promise
 *      }
 *    }
 *
 *   `@Injectable()`
 *   `@SystemEventHandlerClass()`
 *    export class DataJobManageService {
 *      constructor(private readonly httpClient: HttpClient) {}
 *
 *     `@SystemEventHandler(['SE_Create_Job', 'SE_Update_Job'])` // BLOCKING SystemEvents
 *      public _createOrUpdateJobHandler(payload: { baseUrl: string; jobName: string; jobCreator?: string; data?: any }, eventId: SystemEvent): Promise<boolean> {
 *
 *        // Do something
 *
 *        let url: string;
 *        let payloadData: { jobName: string; jobCreator?: string; data?: any }
 *
 *        if (eventId === 'SE_Create_Job') {
 *          url = `${baseUrl}/create`;
 *          payloadData = { jobName, jobCreator };
 *        } else {
 *          url = `${baseUrl}/update`
 *          payloadData = { jobName, data };
 *        }
 *
 *        // Possibility to make asynchronous calls,
 *        // while Invoker is waiting until every Handler is executed,
 *        // and execution flow is returned
 *        return this
 *                  .httpClient
 *                  .post(url, payloadData)
 *                  .pipe(
 *                    map((v) => !!v) // do some transformation and return boolean
 *                  )
 *                  .toPromise(); // cast to Promise
 *      }
 *    }
 *
 *
 */
export function SystemEventHandler(
	knownEvents: SystemEvent | SystemEvent[],
	filterExpression?: Expression
): MethodDecorator {
	return (target, propertyKey, descriptor) => {
		if (!descriptor || !knownEvents) {
			return;
		}

		let metadataRecords: SystemEventMetadataRecords = [];

		if (Reflect.hasMetadata(SYSTEM_EVENTS_METADATA_KEY, target.constructor)) {
			// eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
			metadataRecords = Reflect.getMetadata(
				SYSTEM_EVENTS_METADATA_KEY,
				target.constructor
			);
			metadataRecords.push({
				handler: descriptor.value as unknown as SystemEventHandlerRef,
				events: knownEvents,
				filterExpression
			});

			Reflect.defineMetadata(
				SYSTEM_EVENTS_METADATA_KEY,
				metadataRecords,
				target.constructor,
				propertyKey
			);

			return;
		}

		metadataRecords.push({
			handler: descriptor.value as unknown as SystemEventHandlerRef,
			events: knownEvents,
			filterExpression
		});

		Reflect.defineMetadata(
			SYSTEM_EVENTS_METADATA_KEY,
			metadataRecords,
			target.constructor
		);
	};
}
