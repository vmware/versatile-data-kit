

import { RouterState, RouteSegments, RouteState } from './route.model';

describe('Route Classes', () => {
    describe('RouteSegments', () => {
        it('should verify instance is created', () => {
            // When
            const instance = new RouteSegments(
                'domain/context',
                {},
                {},
                {},
                null,
                null);

            // Then
            expect(instance).toBeDefined();
        });

        describe('Statics::', () => {
            describe('Methods::', () => {
                describe('|of|', () => {
                    it('should verify factory method will create instance', () => {
                        // When
                        const instance = RouteSegments.of('domain/context',
                            {},
                            {},
                            null,
                            null);

                        // Then
                        expect(instance).toBeInstanceOf(RouteSegments);
                    });
                });

                describe('|empty|', () => {
                    it('should verify will create empty instance with default values', () => {
                        // When
                        const instance = RouteSegments.empty();

                        // Then
                        expect(instance).toBeInstanceOf(RouteSegments);
                        expect(instance.params).toEqual({});
                        expect(instance.queryParams).toEqual({});
                        expect(instance.routePath).toEqual('');
                    });
                });
            });
        });

        describe('Methods::', () => {
            describe('|getData|', () => {
                it('should verify will return param', () => {
                    // Given
                    const routeSegments = RouteSegments.of(
                        'bill/105/view',
                        { paramKey: 'prime' },
                        { billId: '105' },
                        {},
                        RouteSegments.of(
                            'entity/17/explore',
                            { deferredLoad: true },
                            { entityId: '17' },
                            null,
                            RouteSegments.of(
                                'domain/context',
                                null,
                                null,
                                null,
                                null,
                                'domain/context'
                            ),
                            'entity/:entityId/explore'
                        ),
                        'bill/:billId/view'
                    );

                    // When
                    const param1 = routeSegments.getData('randomParam');
                    const param2 = routeSegments.getData<string>('paramKey');
                    const param3 = routeSegments.getData<boolean>('deferredLoad');

                    // Then
                    expect(param1).toBeUndefined();
                    expect(param2).toEqual('prime');
                    expect(param3).toEqual(true);
                });
            });

            describe('|getParam|', () => {
                it('should verify will return param', () => {
                    // Given
                    const routeSegments = RouteSegments.of(
                        'bill/105',
                        {},
                        { billId: '105' },
                        {},
                        RouteSegments.of(
                            'entity/17',
                            {},
                            { entityId: '17' },
                            {},
                            null,
                            'entity/:entityId'
                        ),
                        'bill/:billId'
                    );

                    // When
                    const param1 = routeSegments.getParam('randomParam');
                    const param2 = routeSegments.getParam('billId');
                    const param3 = routeSegments.getParam('entityId');

                    // Then
                    expect(param1).toBeUndefined();
                    expect(param2).toEqual('105');
                    expect(param3).toEqual('17');
                });
            });

            describe('|getQueryParam|', () => {
                it('should verify will return queryParam', () => {
                    // Given
                    const routeSegments = RouteSegments.of(
                        'bill/105',
                        {},
                        { billId: '105' },
                        { search: 'test-team', activeUser: 'aUser' },
                        RouteSegments.of(
                            'entity/17',
                            {},
                            { entityId: '17' },
                            { search: 'test-team', activeUser: 'aUser' },
                            RouteSegments.of(
                                'domain/context',
                                {},
                                {},
                                { search: 'test-team', activeUser: 'aUser' },
                                null,
                                'domain/context'
                            ),
                            'entity/:entityId'
                        ),
                        'bill/:billId'
                    );

                    // When
                    const queryParam1 = routeSegments.getQueryParam('entityId');
                    const queryParam2 = routeSegments.getQueryParam('search');
                    const queryParam3 = routeSegments.getQueryParam('activeUser');

                    // Then
                    expect(queryParam1).toBeUndefined();
                    expect(queryParam2).toEqual('test-team');
                    expect(queryParam3).toEqual('aUser');
                });
            });
        });

        describe('Getters/Setters::', () => {
            describe('|GET -> routePathSegments|', () => {
                it('should verify will return routePathSegments', () => {
                    // Given
                    const routeSegments = RouteSegments.of(
                        'bill/105/view',
                        {},
                        null,
                        null,
                        RouteSegments.of(
                            'entity/17/explore',
                            {},
                            null,
                            null,
                            RouteSegments.of(
                                'domain/context',
                                null,
                                null,
                                null,
                                null,
                                'domain/context'
                            ),
                            'entity/:entityId/explore'
                        ),
                        'bill/:billId/view'
                    );

                    // When
                    const routePathSegments = routeSegments.routePathSegments;

                    // Then
                    expect(routePathSegments).toEqual(['domain/context', 'entity/17/explore', 'bill/105/view']);
                });
            });

            describe('|GET -> configPathSegments|', () => {
                it('should verify will return configPathSegments', () => {
                    // Given
                    const routeSegments = RouteSegments.of(
                        'bill/105/view',
                        {},
                        null,
                        null,
                        RouteSegments.of(
                            'entity/17/explore',
                            {},
                            null,
                            null,
                            RouteSegments.of(
                                'domain/context',
                                null,
                                null,
                                null,
                                null,
                                'domain/context'
                            ),
                            'entity/:entityId/explore'
                        ),
                        'bill/:billId/view'
                    );

                    // When
                    const configPathSegments = routeSegments.configPathSegments;

                    // Then
                    expect(configPathSegments).toEqual(['domain/context', 'entity/:entityId/explore', 'bill/:billId/view']);
                });
            });
        });
    });

    describe('RouteState', () => {
        let routeState: RouteState;
        let routeSegments: RouteSegments;

        beforeEach(() => {
            routeSegments = RouteSegments.of(
                'bill/105/view',
                {},
                null,
                { 'test_search*': '^test-team$', 'test_@active-user': '%aUser%' },
                RouteSegments.of(
                    'entity/17/explore',
                    {},
                    null,
                    null,
                    RouteSegments.of(
                        'domain/context',
                        {},
                        null,
                        null,
                        null,
                        'domain/context'
                    ),
                    'entity/:entityId/explore'
                ),
                'bill/:billId/view'
            );

            routeState = RouteState.of(
                routeSegments,
                'domain/context/entity/17/explore/bill/105/view'
            );
        });

        it('should verify instance is created', () => {
            // When
            const instance = new RouteState(
                new RouteSegments(
                    'domain/context',
                    {},
                    {},
                    null,
                    null),
                'domain/context'
            );

            // Then
            expect(instance).toBeDefined();
        });

        describe('Statics::', () => {
            describe('Methods::', () => {
                describe('|of|', () => {
                    it('should verify factory method will create instance', () => {
                        // When
                        const instance = RouteState.of(
                            new RouteSegments(
                                'domain/context',
                                {},
                                {},
                                null,
                                null),
                            'domain/context'
                        );

                        // Then
                        expect(instance).toBeInstanceOf(RouteState);
                    });
                });

                describe('|empty|', () => {
                    it('should verify will create empty instance with default values', () => {
                        // When
                        const instance = RouteState.empty();

                        // Then
                        expect(instance).toBeInstanceOf(RouteState);
                        expect(instance.routeSegments).toEqual(RouteSegments.empty());
                        expect(instance.url).toEqual('');
                    });
                });
            });
        });

        describe('Getters/Setters::', () => {
            describe('|GET -> absoluteRoutePath|', () => {
                it('should verify will return location', () => {
                    // When
                    const location = routeState.absoluteRoutePath;

                    // Then
                    expect(location).toEqual('/domain/context/entity/17/explore/bill/105/view');
                });
            });

            describe('|GET -> routePath|', () => {
                it('should verify will return routePath', () => {
                    // When
                    const routePath = routeState.routePath;

                    // Then
                    expect(routePath).toEqual('bill/105/view');
                });
            });

            describe('|GET -> routePathSegments|', () => {
                it('should verify will return routePathSegments', () => {
                    // When
                    const routePathSegments = routeState.routePathSegments;

                    // Then
                    expect(routePathSegments).toEqual(['domain/context', 'entity/17/explore', 'bill/105/view']);
                });
            });

            describe('|GET -> configPath|', () => {
                it('should verify will return configPath', () => {
                    // When
                    const configPath = routeState.configPath;

                    // Then
                    expect(configPath).toEqual('bill/:billId/view');
                });
            });

            describe('|GET -> absoluteConfigPath|', () => {
                it('should verify will return absoluteConfigPath', () => {
                    // When
                    const absoluteConfigPath = routeState.absoluteConfigPath;

                    // Then
                    expect(absoluteConfigPath).toEqual('/domain/context/entity/:entityId/explore/bill/:billId/view');
                });
            });

            describe('|GET -> configPathSegments|', () => {
                it('should verify will return configPathSegments', () => {
                    // When
                    const configPathSegments = routeState.configPathSegments;

                    // Then
                    expect(configPathSegments).toEqual(['domain/context', 'entity/:entityId/explore', 'bill/:billId/view']);
                });
            });

            describe('|GET -> queryParams|', () => {
                it('should verify will return queryParams', () => {
                    // When
                    const queryParams = routeState.queryParams;

                    // Then
                    expect(queryParams).toBe(routeState.routeSegments.queryParams);
                });
            });
        });

        describe('Methods::', () => {
            describe('|serializeQueryParams|', () => {
                it('should verify will serialize queryParams in string', () => {
                    // When
                    const query = routeState.serializeQueryParams();

                    // Then
                    expect(query).toEqual('test_search*=%5Etest-team%24&test_%40active-user=%25aUser%25');
                });

                it('should verify will return empty string when no queryParams', () => {
                    // Given
                    routeState = RouteState.of(
                        RouteSegments.of(
                            routeState.routeSegments.routePath,
                            routeState.routeSegments.data,
                            routeState.routeSegments.params,
                            {},
                            routeState.routeSegments.parent,
                            routeState.routeSegments.configPath
                        ),
                        routeState.url
                    );

                    // When
                    const query = routeState.serializeQueryParams();

                    // Then
                    expect(query).toEqual('');
                });
            });

            describe('|getUrl|', () => {
                it('should verify will return correct value', () => {
                    // When
                    const url = routeState.getUrl();

                    // Then
                    expect(url).toEqual(
                        '/domain/context/entity/17/explore/bill/105/view?test_search*=%5Etest-team%24&test_%40active-user=%25aUser%25'
                    );
                });
            });

            describe('|getData|', () => {
                it('should verify will invoke correct methods', () => {
                    // Given
                    const getDataSpy = spyOn(RouteSegments.prototype, 'getData').and.returnValue('loading');

                    // When
                    const data = routeState.getData('primeKey');

                    // Then
                    expect(getDataSpy).toHaveBeenCalledWith('primeKey');
                    expect(data).toEqual('loading');
                });
            });

            describe('|getParam|', () => {
                it('should verify will invoke correct methods', () => {
                    // Given
                    const getParamSpy = spyOn(RouteSegments.prototype, 'getParam').and.returnValue('test-value');

                    // When
                    const param = routeState.getParam('random-key');

                    // Then
                    expect(getParamSpy).toHaveBeenCalledWith('random-key');
                    expect(param).toEqual('test-value');
                });
            });

            describe('|getQueryParam|', () => {
                it('should verify will invoke correct methods', () => {
                    // Given
                    const getQueryParamSpy = spyOn(RouteSegments.prototype, 'getQueryParam').and.returnValue('test-value');

                    // When
                    const queryParam = routeState.getQueryParam('random-key');

                    // Then
                    expect(getQueryParamSpy).toHaveBeenCalledWith('random-key');
                    expect(queryParam).toEqual('test-value');
                });
            });

            describe('|getParentAbsoluteRoutePath|', () => {
                it('should verify will return correct value', () => {
                    // When
                    const parentAbsoluteRoutePath = routeState.getParentAbsoluteRoutePath();

                    // Then
                    expect(parentAbsoluteRoutePath).toEqual('/domain/context/entity/17/explore');
                });
            });

            describe('|toJSON|', () => {
                it('should verify will return correct object for serialization', () => {
                    // When
                    const objForSerialize = routeState.toJSON();

                    // Then
                    expect(objForSerialize).toEqual({
                        routeSegments,
                        url: 'domain/context/entity/17/explore/bill/105/view',
                        routePath: 'bill/105/view',
                        absoluteRoutePath: '/domain/context/entity/17/explore/bill/105/view',
                        routePathSegments: ['domain/context', 'entity/17/explore', 'bill/105/view'],
                        configPath: 'bill/:billId/view',
                        absoluteConfigPath: '/domain/context/entity/:entityId/explore/bill/:billId/view',
                        configPathSegments: ['domain/context', 'entity/:entityId/explore', 'bill/:billId/view'],
                        queryParams: { 'test_search*': '^test-team$', 'test_@active-user': '%aUser%' }
                    });
                });
            });
        });
    });

    describe('RouterState', () => {
        let routeSegments: RouteSegments;
        let routeState: RouteState;
        let routerState: RouterState;
        let previousRouterState: RouterState;

        beforeEach(() => {
            routeSegments = RouteSegments.of(
                'bill/105/view',
                {},
                null,
                { 'test_search*': '^test-team$', 'test_@active-user': '%aUser%' },
                RouteSegments.of(
                    'entity/17/explore',
                    {},
                    null,
                    null,
                    RouteSegments.of(
                        'domain/context',
                        {},
                        null,
                        null,
                        null,
                        'domain/context'
                    ),
                    'entity/:entityId/explore'
                ),
                'bill/:billId/view'
            );

            routeState = RouteState.of(
                routeSegments,
                'domain/context/entity/17/explore/bill/105/view'
            );

            routerState = RouterState.of(
                routeState,
                15
            );

            previousRouterState = RouterState.of(
                RouteState.empty(),
                14
            );
            previousRouterState.previousStates.push(
                RouterState.of(
                    RouteState.empty(),
                    13
                ),
                RouterState.of(
                    RouteState.empty(),
                    12
                ),
                RouterState.of(
                    RouteState.empty(),
                    11
                )
            );
        });

        it('should verify instance is created', () => {
            // When
            const instance = new RouterState(
                new RouteState(
                    new RouteSegments(
                        'domain/context',
                        {},
                        {},
                        null,
                        null),
                    'domain/context'
                ),
                8
            );

            // Then
            expect(instance).toBeDefined();
        });

        describe('Statics::', () => {
            describe('Methods::', () => {
                describe('|of|', () => {
                    it('should verify factory method will create instance', () => {
                        // When
                        const instance = RouterState.of(
                            new RouteState(
                                new RouteSegments(
                                    'domain/context',
                                    {},
                                    {},
                                    null,
                                    null),
                                'domain/context'
                            ),
                            11
                        );

                        // Then
                        expect(instance).toBeInstanceOf(RouterState);
                    });
                });

                describe('|empty|', () => {
                    it('should verify will create empty instance with default values', () => {
                        // When
                        const instance = RouterState.empty();

                        // Then
                        expect(instance).toBeInstanceOf(RouterState);
                        expect(instance.state).toEqual(RouteState.empty());
                        expect(instance.navigationId).toEqual(null);
                        expect(instance.previousStates).toEqual([]);
                    });
                });
            });
        });

        describe('Methods::', () => {
            describe('|getPrevious|', () => {
                beforeEach(() => {
                    routerState.previousStates.push(
                        ...previousRouterState.previousStates
                    );
                    previousRouterState.previousStates.length = 0;
                    routerState.previousStates.unshift(previousRouterState);
                });

                it('should verify will return the first before current as default', () => {
                    // When
                    const previous = routerState.getPrevious();

                    // Then
                    expect(previous).toBe(previousRouterState);
                });

                it('should verify will return the first before current for index 0', () => {
                    // When
                    const previous = routerState.getPrevious(0);

                    // Then
                    expect(previous).toBe(previousRouterState);
                });

                it('should verify will return the third before current for index 2', () => {
                    // When
                    const previous = routerState.getPrevious(2);

                    // Then
                    expect(previous).toBe(routerState.previousStates[2]);
                });

                it('should verify will return null for number less than 0', () => {
                    // When
                    const previous = routerState.getPrevious(-1);

                    // Then
                    expect(previous).toBe(null);
                });

                it('should verify will return the first before current for index not a number', () => {
                    // When
                    const previous = routerState.getPrevious(null);

                    // Then
                    expect(previous).toBe(previousRouterState);
                });

                it('should verify will return null for index that is out of bound of stored States', () => {
                    // When
                    const previous = routerState.getPrevious(4);

                    // Then
                    expect(previous).toBe(null);
                });
            });

            describe('|appendPrevious|', () => {
                it('should verify will add previousStates to current one', () => {
                    // Given
                    const firstElement = RouterState.of(RouteState.empty(), 14);
                    const forthElement = RouterState.of(RouteState.empty(), 11);

                    // When
                    routerState.appendPrevious(previousRouterState);

                    // Then
                    expect(routerState.previousStates.length).toEqual(4);
                    expect(routerState.previousStates[0]).toEqual(firstElement);
                    expect(routerState.previousStates[3]).toEqual(forthElement);
                });

                it('should verify will pop the oldest one and will unshift the new one when buffer has 10 elements', () => {
                    // Given
                    previousRouterState.previousStates.push(
                        RouterState.of(
                            RouteState.empty(),
                            10
                        ),
                        RouterState.of(
                            RouteState.empty(),
                            9
                        ),
                        RouterState.of(
                            RouteState.empty(),
                            8
                        ),
                        RouterState.of(
                            RouteState.empty(),
                            7
                        ),
                        RouterState.of(
                            RouteState.empty(),
                            6
                        ),
                        RouterState.of(
                            RouteState.empty(),
                            5
                        ),
                        RouterState.of(
                            RouteState.empty(),
                            4
                        )
                    );

                    // Then 1
                    expect(routerState.previousStates.length).toEqual(0);
                    expect(routerState.previousStates[0]).toBeUndefined();
                    expect(previousRouterState.navigationId).toEqual(14);
                    expect(previousRouterState.previousStates[0]).toEqual(
                        RouterState.of(RouteState.empty(), 13)
                    );
                    expect(previousRouterState.previousStates[9]).toEqual(
                        RouterState.of(RouteState.empty(), 4)
                    );

                    // When
                    routerState.appendPrevious(previousRouterState);

                    // Then 2
                    expect(routerState.previousStates.length).toEqual(10);
                    expect(routerState.previousStates[0]).toEqual(
                        RouterState.of(RouteState.empty(), 14)
                    );
                    expect(routerState.previousStates[9]).toEqual(
                        RouterState.of(RouteState.empty(), 5)
                    );
                });

                it(`should verify won't add new state when previousState has same navigationId like current`, () => {
                    // Given
                    routerState = RouterState.of(
                        RouteState.empty(),
                        14
                    );

                    // Then 1
                    expect(routerState.previousStates.length).toEqual(0);
                    expect(previousRouterState.previousStates.length).toEqual(3);
                    expect(previousRouterState.previousStates[0]).toEqual(
                        RouterState.of(RouteState.empty(), 13)
                    );
                    expect(previousRouterState.previousStates[2]).toEqual(
                        RouterState.of(RouteState.empty(), 11)
                    );

                    // When
                    routerState.appendPrevious(previousRouterState);

                    // Then 2
                    expect(routerState.previousStates.length).toEqual(3);
                    expect(routerState.navigationId).toEqual(14);
                    expect(routerState.previousStates[0]).toEqual(
                        RouterState.of(RouteState.empty(), 13)
                    );
                    expect(routerState.previousStates[2]).toEqual(
                        RouterState.of(RouteState.empty(), 11)
                    );
                });
            });
        });
    });
});
