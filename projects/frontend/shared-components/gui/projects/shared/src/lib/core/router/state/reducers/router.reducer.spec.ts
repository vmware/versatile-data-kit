

import { RouterStateSnapshot, RoutesRecognized } from '@angular/router';

import { ROUTER_NAVIGATION, RouterNavigationAction } from '@ngrx/router-store';

import { RouterState, RouteState } from '../../model';

import { routerReducer } from './router.reducer';

describe('routerReducer', () => {
    it('should verify will invoke correct methods', () => {
        // Given
        const navigateAction: RouterNavigationAction<RouteState> = {
            type: ROUTER_NAVIGATION,
            payload: {
                routerState: RouteState.empty(),
                event: new RoutesRecognized(5, 'domain/context', 'domain/context', {} as RouterStateSnapshot)
            }
        };
        const storedRouterStateStub = jasmine.createSpyObj<RouterState>('routerState', ['appendPrevious']);
        const newRouterStateStub = jasmine.createSpyObj<RouterState>('routerState', ['appendPrevious']);
        const factoryMethodSpy = spyOn(RouterState, 'of').and.returnValue(newRouterStateStub);

        // When
        const value = routerReducer(storedRouterStateStub, navigateAction);

        // Then
        expect(value).toBe(newRouterStateStub);
        expect(factoryMethodSpy).toHaveBeenCalledWith(navigateAction.payload.routerState, navigateAction.payload.event.id);
        expect(newRouterStateStub.appendPrevious).toHaveBeenCalledWith(storedRouterStateStub);
    });
});
