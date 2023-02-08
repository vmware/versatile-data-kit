

import { PrimitivesNil, PrimitivesNilArrays, PrimitivesNilObject } from '../../utils';

type SerializedType = PrimitivesNil | PrimitivesNilArrays | PrimitivesNilObject | unknown;

/**
 * ** This interface gives boundaries for Objects that we want to be serializable for JSON.
 *
 * @author gorankokin
 */
export interface Serializable<T extends SerializedType = SerializedType> {
    /**
     * ** Implements this method and return data you want to be serialized when JSON.stringify(...) is executed.
     */
    toJSON(): T;
}
