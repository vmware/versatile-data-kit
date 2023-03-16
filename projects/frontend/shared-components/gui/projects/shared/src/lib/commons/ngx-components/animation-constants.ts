/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

// –——— CLARITY ANIMATIONS —————
// ATOMIC Animations
// primary
export const atomicPrimaryEnterCurve = 'cubic-bezier(0, 1.5, 0.5, 1)';
export const atomicPrimaryEnterTiming = 200;
export const atomicPrimaryLeaveCurve = 'cubic-bezier(0,.99,0,.99)';
export const atomicPrimaryLeaveTiming = 200;

// secondary
export const atomicSecondaryEnterCurve = 'cubic-bezier(0, 1.5, 0.5, 1)';
export const atomicSecondaryEnterTiming = 400;
export const atomicSecondaryLeaveCurve = 'cubic-bezier(0, 1.5, 0.5, 1)';
export const atomicSecondaryLeaveTiming = 100;

// COMPONENT Animations
// primary
export const componentPrimaryEnterCurve = 'cubic-bezier(0,.99,0,.99)';
export const componentPrimaryEnterTiming = 400;
export const componentPrimaryLeaveCurve = 'cubic-bezier(0,.99,0,.99)';
export const componentPrimaryLeaveTiming = 300;

// PAGE Animations
// primary
export const pagePrimaryEnterCurve = 'cubic-bezier(0,.99,0,.99)';
export const pagePrimaryEnterTiming = 250;
export const pagePrimaryLeaveCurve = 'cubic-bezier(0,.99,0,.99)';
export const pagePrimaryLeaveTiming = 200;

// PROGRESS Animations
// primary
export const progressPrimaryCurve = 'cubic-bezier(.17,.4,.8,.79)';
export const progressPrimaryTiming = 790;

// secondary
export const progressSecondaryCurve = 'cubic-bezier(.34,.01,.39,1)';
export const progressSecondaryTiming = 200;

// ICON Animations
// primary
export const linePrimaryEnterCurve = 'linear';
export const linePrimaryEnterTiming = 250;
export const linePrimaryEnterDelay = 200;

// secondary
export const lineSecondaryEnterCurve = 'linear';
export const lineSecondaryEnterTiming = 400;
export const lineSecondaryEnterDelay = 200;

// –——— NGX ONLY ANIMATIONS —————
export const DISMISS_ICON_DURATION = 300;
export const DISMISS_ICON_DELAY = 350;
export const DISMISS_ICON_CURVE = 'cubic-bezier(0, 1.2, 0.7, 1)';

export const GRADIENT_DURATION = 500;
export const GRADIENT_DELAY = 100;
export const GRADIENT_LEAVE_CURVE = 'cubic-bezier(0, 1.2, 0.7, 1)';
export const STAGGER_DURATION = 200;

// used for animation debugging
const ANIMATION_MULTIPLIER = 1;

export function multiply(value: number) {
    return value * ANIMATION_MULTIPLIER;
}
