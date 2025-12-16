import { writable } from 'svelte/store';
import type { UserResponse } from './api/queries';


export const currentUser = writable<UserResponse | null>(null);

