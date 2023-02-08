

/* eslint-disable @typescript-eslint/no-inferrable-types */

/**
 * ** Status constant for Initialized.
 */
export const INITIALIZED = 'Initialized';

/**
 * ** Status constant for Idle.
 */
export const IDLE = 'Idle';

/**
 * ** Status constant for Loading.
 */
export const LOADING = 'Loading';

/**
 * ** Status constant for Loaded.
 */
export const LOADED = 'Loaded';

/**
 * ** Status constant for Failed.
 */
export const FAILED = 'Failed';

/**
 * ** Status types.
 */
export type StatusType = typeof INITIALIZED | typeof IDLE | typeof LOADING | typeof LOADED | typeof FAILED;
