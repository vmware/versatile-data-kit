/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { iif, Observable, of, throwError } from 'rxjs';
import { catchError, map, mergeMap, switchMap, take } from 'rxjs/operators';

import { BaseActionWithPayload } from '../../../ngrx/actions';

import { ComponentService } from '../../services';
import { ComponentModel, ComponentState } from '../../model';

import { ComponentFailed } from '../actions';

/**
 * ** RXJS Operator that fetch Component Model from Store using provided ComponentService.
 *
 *      - Returns Observable<ComponentModel>
 *
 *
 */
export const getModel =
	(componentService: ComponentService) =>
	(
		source$: Observable<BaseActionWithPayload<ComponentState>>
	): Observable<ComponentModel> =>
		source$.pipe(
			extractAction,
			switchMap((action) => subscribeForModel(action, componentService))
		);

/**
 * ** RXJS Operator that fetch Component Model from Store using provided ComponentService and consume task from Action.
 *
 *      - Returns Observable<[ComponentModel, string]>
 *
 *
 */
export const getModelAndTask =
	(componentService: ComponentService) =>
	(
		source$: Observable<BaseActionWithPayload<ComponentState>>
	): Observable<[ComponentModel, string]> =>
		source$.pipe(
			extractAction,
			switchMap((action) =>
				subscribeForModel(action, componentService).pipe(
					map((model) => [model, action.task] as [ComponentModel, string])
				)
			)
		);

/**
 * ** Handle Error from some Action, ideal to use for API response.
 *
 *      - Catch error if happen, append it to Model, set status to FAILED,
 *          create instance of {@link ComponentFailed} and return stream in success state using {@link of} rjxs operator.
 *
 *
 */
export const handleActionError =
	(model: ComponentModel) =>
	(
		source$: Observable<BaseActionWithPayload<ComponentState>>
	): Observable<BaseActionWithPayload<ComponentState>> =>
		source$.pipe(
			catchError((error: unknown) =>
				of(
					ComponentFailed.of(
						model
							.withError(error as Error)
							.withStatusFailed()
							.getComponentState()
					)
				)
			)
		);

/**
 * ** Validate if Action is instance of {@link BaseActionWithPayload} and pass down the stream.
 *
 *
 */
const extractAction = (
	source$: Observable<BaseActionWithPayload<ComponentState>>
) =>
	source$.pipe(
		mergeMap((action) =>
			iif(
				() => action instanceof BaseActionWithPayload,
				of(action),
				throwError(
					new Error(
						'Unsupported Action type. It should be subclass of BaseActionWithPayload'
					)
				)
			)
		)
	);

/**
 * ** Make actual subscription to Store for ComponentModel.
 *
 *
 */
const subscribeForModel = (
	action: BaseActionWithPayload<ComponentState>,
	componentService: ComponentService
) =>
	componentService
		.getModel(action.payload.id, action.payload.routePathSegments, ['*'])
		.pipe(take(1));
