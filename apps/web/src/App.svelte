<script lang="ts">
	import { onMount } from 'svelte';
	import { QueryClientProvider } from '@tanstack/svelte-query';
	import { queryClient } from './lib/query-client';
	import Router from './components/Router.svelte';
	import { isAuthenticated } from './lib/auth';
	import { currentUser } from './lib/stores';
	import { userQueries } from './lib/api/queries';
	import { apiGet } from './lib/api/client';
	import type { UserResponse } from './lib/api/queries';

	onMount(async () => {
		// Fetch current user on app initialization if authenticated
		if (isAuthenticated()) {
			try {
				const user = await apiGet<UserResponse>('/users/me');
				currentUser.set(user);
			} catch (error) {
				// Token is invalid/expired, clear user store
				// The API client will handle redirecting to login
				currentUser.set(null);
			}
		}
	});
</script>

<QueryClientProvider client={queryClient}>
	<Router />
</QueryClientProvider>

