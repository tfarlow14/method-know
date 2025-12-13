<script lang="ts">
	import { QueryClientProvider } from '@tanstack/svelte-query';
	import { queryClient } from './lib/query-client';
	import Router from './components/Router.svelte';
</script>

<QueryClientProvider client={queryClient}>
	<Router />
</QueryClientProvider>

