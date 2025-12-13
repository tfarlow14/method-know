<script lang="ts">
	import { location } from '../lib/router';
	import Dashboard from '../pages/Dashboard.svelte';
	import Login from '../pages/Login.svelte';
	import Signup from '../pages/Signup.svelte';

	const routes: Record<string, any> = {
		'/': Dashboard,
		'/login': Login,
		'/signup': Signup
	};

	$: currentRoute = $location;
	$: Component = routes[currentRoute] || routes['/'];
</script>

<svelte:component this={Component} />

