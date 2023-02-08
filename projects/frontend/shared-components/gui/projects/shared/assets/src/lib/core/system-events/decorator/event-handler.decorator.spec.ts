

import { SystemEventHandler } from './event-handler.decorator';
import { SYSTEM_EVENTS_METADATA_KEY } from './models';

describe('SystemEventHandler', () => {
    let event: string;
    let event2: string;
    // eslint-disable-next-line @typescript-eslint/ban-types
    let constructor: Function;
    // eslint-disable-next-line @typescript-eslint/ban-types
    let target: { constructor: Function };
    let propertyKey: string;
    let propertyKey2: string;
    let descriptor: PropertyDescriptor;
    let descriptor2: PropertyDescriptor;

    beforeEach(() => {
        class TestClazz {
        }

        event = 'SE_Register_User';
        event2 = 'SE_Unregister_User';
        constructor = TestClazz.prototype.constructor;
        target = { constructor };
        propertyKey = '_eventHandlerRegister';
        propertyKey2 = 'eventHandleUnregister';
        descriptor = { value: () => Promise.resolve(true) };
        descriptor2 = { value: () => Promise.resolve(true) };
    });

    it('should verify will record metadata with Reflect to Constructor', () => {
        // Then 1
        expect(Reflect.hasMetadata(SYSTEM_EVENTS_METADATA_KEY, constructor)).toBeFalse();

        // When
        SystemEventHandler(event, null)(target, propertyKey, descriptor);

        // Then 2
        expect(Reflect.hasMetadata(SYSTEM_EVENTS_METADATA_KEY, constructor)).toBeTrue();
        expect(Reflect.getMetadata(SYSTEM_EVENTS_METADATA_KEY, constructor)).toEqual([{
            handler: descriptor.value,
            events: event,
            filterExpression: null
        }]);
    });

    it('should verify will add metadata on existing with Reflect to Constructor', () => {
        // Then 1
        expect(Reflect.hasMetadata(SYSTEM_EVENTS_METADATA_KEY, constructor)).toBeFalse();

        // When
        SystemEventHandler(event, null)(target, propertyKey, descriptor);
        SystemEventHandler(event2, null)(target, propertyKey2, descriptor2);

        // Then 2
        expect(Reflect.hasMetadata(SYSTEM_EVENTS_METADATA_KEY, constructor)).toBeTrue();
        expect(Reflect.getMetadata(SYSTEM_EVENTS_METADATA_KEY, constructor)).toEqual([
            { handler: descriptor.value, events: event, filterExpression: null },
            { handler: descriptor2.value, events: event2, filterExpression: null }
        ]);
    });
});
