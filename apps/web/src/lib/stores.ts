import { writable } from 'svelte/store';
import type { UserResponse } from './api/queries';

/**
 * Current authenticated user store
 * This is session-only and will be set on login/signup
 */
export const currentUser = writable<UserResponse | null>(null);

