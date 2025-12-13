<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '../lib/router';
	import { isAuthenticated, clearAuthToken } from '../lib/auth';
	import { createQuery } from '@tanstack/svelte-query';
	import { resourceQueries, type ResourceCollection } from '../lib/api/queries';
	import { Card, CardContent, CardHeader, CardTitle } from '$lib/components/ui/card';
	import { Button } from '$lib/components/ui/button';
	import { Loader2, ExternalLink, Code, BookOpen, LogOut } from '@lucide/svelte';

	function handleSignOut() {
		clearAuthToken();
		goto('/login');
	}

	// Fetch resources
	const resourcesQuery = createQuery(() => resourceQueries.all());

	onMount(() => {
		// Redirect to login if not authenticated
		if (!isAuthenticated()) {
			goto('/login');
		}
	});
</script>

<div class="min-h-screen bg-background">
	<!-- Navigation -->
	<nav class="bg-white border-b border-border">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
			<div class="flex justify-between items-center h-16">
				<div class="flex items-center">
					<h1 class="text-xl font-semibold text-foreground">Method Know</h1>
				</div>
				<Button
					variant="ghost"
					size="sm"
					onclick={handleSignOut}
					class="flex items-center gap-2"
				>
					<LogOut class="h-4 w-4" />
					Sign out
				</Button>
			</div>
		</div>
	</nav>

	<!-- Main Content -->
	<main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
		<div class="mb-8">
			<h2 class="text-3xl font-semibold text-foreground">Discover Resources</h2>
			<p class="mt-2 text-muted-foreground">Explore shared resources from our community</p>
		</div>

		{#if resourcesQuery.isLoading}
			<div class="flex justify-center items-center py-12">
				<Loader2 class="h-8 w-8 animate-spin text-primary" />
			</div>
		{:else if resourcesQuery.isError}
			<Card class="border-destructive">
				<CardContent class="pt-6">
					<div class="flex items-center gap-3">
						<div class="flex-shrink-0">
							<svg
								class="h-5 w-5 text-destructive"
								viewBox="0 0 20 20"
								fill="currentColor"
							>
								<path
									fill-rule="evenodd"
									d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
									clip-rule="evenodd"
								/>
							</svg>
						</div>
						<p class="text-sm font-medium text-destructive">
							Error loading resources: {resourcesQuery.error?.message || 'Unknown error'}
						</p>
					</div>
				</CardContent>
			</Card>
		{:else if resourcesQuery.isSuccess}
			{@const resourceData = resourcesQuery.data as ResourceCollection}
			{#if resourceData.resources && resourceData.resources.length > 0}
				<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
					{#each resourceData.resources as resource, index (resource.id || `resource-${index}`)}
					<Card class="hover:shadow-lg transition-shadow">
						<CardHeader>
							<div class="flex items-start justify-between gap-2">
								<CardTitle class="text-lg font-semibold">{resource.title}</CardTitle>
								<span
									class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium shrink-0 {resource.type === 'article'
										? 'bg-blue-100 text-blue-800'
										: resource.type === 'code_snippet'
											? 'bg-green-100 text-green-800'
											: 'bg-purple-100 text-purple-800'}"
								>
									{#if resource.type === 'article'}
										<BookOpen class="h-3 w-3 mr-1" />
										Article
									{:else if resource.type === 'code_snippet'}
										<Code class="h-3 w-3 mr-1" />
										Code
									{:else}
										<BookOpen class="h-3 w-3 mr-1" />
										Learning
									{/if}
								</span>
							</div>
						</CardHeader>
						<CardContent class="space-y-4">
							<p class="text-muted-foreground text-sm line-clamp-3">
								{resource.description}
							</p>
							{#if resource.type === 'article' && resource.url}
								<a
									href={resource.url}
									target="_blank"
									rel="noopener noreferrer"
									class="text-primary hover:text-primary/80 text-sm font-medium inline-flex items-center gap-1"
								>
									Read article
									<ExternalLink class="h-4 w-4" />
								</a>
							{:else if resource.type === 'code_snippet' && resource.code}
								<details class="mt-4">
									<summary class="text-sm font-medium text-foreground cursor-pointer hover:text-foreground/80">
										View code
									</summary>
									<pre
										class="mt-2 p-3 bg-muted rounded-md text-xs overflow-x-auto"
									><code>{resource.code}</code></pre>
								</details>
							{/if}
							{#if resource.tag_ids && resource.tag_ids.length > 0}
								<div class="flex flex-wrap gap-2">
									{#each resource.tag_ids as tagId}
										<span
											class="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-muted text-muted-foreground"
										>
											{tagId}
										</span>
									{/each}
								</div>
							{/if}
						</CardContent>
					</Card>
					{/each}
				</div>
			{:else}
				<Card>
					<CardContent class="pt-6 text-center">
						<p class="text-muted-foreground text-lg">No resources found</p>
						<p class="text-muted-foreground/70 text-sm mt-2">
							Be the first to share a resource with the community!
						</p>
					</CardContent>
				</Card>
			{/if}
		{:else}
			<Card>
				<CardContent class="pt-6 text-center">
					<p class="text-muted-foreground text-lg">No resources found</p>
					<p class="text-muted-foreground/70 text-sm mt-2">
						Be the first to share a resource with the community!
					</p>
				</CardContent>
			</Card>
		{/if}
	</main>
</div>

