<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '../lib/router';
	import { isAuthenticated, clearAuthToken } from '../lib/auth';
	import { currentUser } from '../lib/stores';
	import { createQuery } from '@tanstack/svelte-query';
	import { resourceQueries, tagQueries, userQueries, type ResourceCollection, type Resource } from '../lib/api/queries';
	import { Card, CardContent } from '$lib/components/ui/card';
	import { Button } from '$lib/components/ui/button';
	import { Input } from '$lib/components/ui/input';
	import { Loader2, ExternalLink, Code, BookOpen, LogOut, Search, BookMarked, CircleUser, Newspaper, Pencil, Trash2, GraduationCap, BookOpenText } from '@lucide/svelte';

	let searchQuery = $state('');
	let selectedTypes = $state<Set<string>>(new Set(['article', 'code_snippet', 'learning_resource']));
	let selectedTags = $state<Set<string>>(new Set());
	
	// Get current user from Svelte store
	const currentUserId = $derived($currentUser?.id || null);

	function handleSignOut() {
		clearAuthToken();
		currentUser.set(null); // Clear user from store
		goto('/login');
	}

	function handleShareResource() {
		// TODO: Navigate to share resource page
		console.log('Share resource clicked');
	}

	// Fetch resources, tags, and users
	const resourcesQuery = createQuery(() => resourceQueries.all());
	const tagsQuery = createQuery(() => tagQueries.all());
	const usersQuery = createQuery(() => userQueries.all());

	// Log API errors to console
	$effect(() => {
		if (resourcesQuery.isError && resourcesQuery.error) {
			console.error('API Error loading resources:', resourcesQuery.error);
		}
		if (tagsQuery.isError && tagsQuery.error) {
			console.error('API Error loading tags:', tagsQuery.error);
		}
		if (usersQuery.isError && usersQuery.error) {
			console.error('API Error loading users:', usersQuery.error);
		}
	});

	// Get user name from resource (returns first name only)
	function getUserName(resource: Resource): string {
		// Use user info from resource if available (preferred)
		if (resource.user) {
			return resource.user.first_name;
		}
		// Fallback to current user if it's the logged-in user
		if (isOwnResource(resource) && $currentUser) {
			return $currentUser.first_name;
		}
		// Fallback to querying users list (shouldn't be needed if user is populated)
		if (usersQuery.data && resource.user.id) {
			const users = (usersQuery.data as { users: Array<{ id: string; first_name: string; last_name: string }> }).users;
			const user = users.find(u => String(u.id) === String(resource.user.id));
			return user ? user.first_name : 'Unknown';
		}
		return 'Unknown';
	}

	// Create tag ID to name mapping
	const tagIdToNameMap = $derived.by(() => {
		if (!tagsQuery.data) return new Map<string, string>();
		const tags = (tagsQuery.data as { tags: Array<{ id?: string; name: string }> }).tags;
		const map = new Map<string, string>();
		tags.forEach(tag => {
			// Map by ID if available (normalize to string for comparison)
			if (tag.id) {
				map.set(String(tag.id), tag.name);
			}
			// Also map by name as fallback
			map.set(String(tag.name), tag.name);
		});
		return map;
	});

	// Get total resources count (before filtering)
	const totalResourcesCount = $derived.by(() => {
		if (!resourcesQuery.data) return 0;
		const data = resourcesQuery.data as ResourceCollection;
		return data.resources?.length || 0;
	});

	// Check if any filters are applied
	const hasActiveFilters = $derived.by(() => {
		const hasSearch = searchQuery.trim().length > 0;
		// Check if all default types are selected (default state)
		const allDefaultTypesSelected = selectedTypes.size === 3 && 
			selectedTypes.has('article') && 
			selectedTypes.has('code_snippet') && 
			selectedTypes.has('learning_resource');
		const hasTypeFilter = !allDefaultTypesSelected;
		const hasTagFilter = selectedTags.size > 0;
		return hasSearch || hasTypeFilter || hasTagFilter;
	});

	// Filter resources
	const filteredResources = $derived.by(() => {
		if (!resourcesQuery.data) return [];
		const data = resourcesQuery.data as ResourceCollection;
		let resources = data.resources || [];

		// Filter by search query
		if (searchQuery.trim()) {
			const query = searchQuery.toLowerCase();
			resources = resources.filter(r => 
				r.title.toLowerCase().includes(query) || 
				r.description.toLowerCase().includes(query)
			);
		}

		// Filter by type
		if (selectedTypes.size > 0) {
			resources = resources.filter(r => {
				if (r.type === 'article') return selectedTypes.has('article');
				if (r.type === 'code_snippet') return selectedTypes.has('code_snippet');
				if (r.type === 'book' || r.type === 'course') return selectedTypes.has('learning_resource');
				return false;
			});
		}

		// Filter by tags
		if (selectedTags.size > 0) {
			resources = resources.filter(r => 
				r.tags.some(tag => {
					const tagId = tag.id ? String(tag.id) : tag.name;
					return selectedTags.has(tagId) || selectedTags.has(tag.name);
				})
			);
		}

		return resources;
	});

	// Get all unique tags from resources
	const allTags = $derived.by(() => {
		if (!resourcesQuery.data) return [];
		const data = resourcesQuery.data as ResourceCollection;
		const tagSet = new Set<string>();
		(data.resources || []).forEach(r => {
			r.tags.forEach(tag => {
				if (tag.id) tagSet.add(String(tag.id));
				tagSet.add(tag.name);
			});
		});
		return Array.from(tagSet);
	});

	// Toggle resource type filter
	function toggleType(type: string) {
		if (selectedTypes.has(type)) {
			selectedTypes.delete(type);
		} else {
			selectedTypes.add(type);
		}
		selectedTypes = new Set(selectedTypes);
	}

	// Toggle tag filter
	function toggleTag(tagId: string) {
		if (selectedTags.has(tagId)) {
			selectedTags.delete(tagId);
		} else {
			selectedTags.add(tagId);
		}
		selectedTags = new Set(selectedTags);
	}

	// Get resource type display name
	function getResourceTypeName(resource: Resource): string {
		if (resource.type === 'article') return 'Article';
		if (resource.type === 'code_snippet') return 'Code Snippet';
		if (resource.type === 'book') return 'Book';
		if (resource.type === 'course') return 'Course';
		return 'Learning Resource';
	}

	// Get resource type icon
	function getResourceTypeIcon(resource: Resource) {
		if (resource.type === 'article') return Newspaper;
		if (resource.type === 'code_snippet') return Code;
		if (resource.type === 'book') return BookOpenText;
		if (resource.type === 'course') return GraduationCap;
		return BookOpen;
	}

	// Format date (placeholder - resources don't have created_at yet)
	function formatDate(resource: Resource): string {
		// TODO: Use actual created_at when available
		return 'Today';
	}

	// Check if resource is owned by current user
	function isOwnResource(resource: Resource): boolean {
		if (!currentUserId || !resource.user.id) return false;
		return String(resource.user.id) === String(currentUserId);
	}

	onMount(() => {
		// Redirect to login if not authenticated
		if (!isAuthenticated()) {
			goto('/login');
		}
	});
</script>

<div class="min-h-screen bg-[#fcfcfc]">
	<!-- Navigation Header -->
	<nav class="bg-white shadow-[0px_4px_4px_0px_rgba(0,0,0,0.08)]">
		<div class="max-w-[1440px] mx-auto px-12 py-4">
			<div class="flex justify-between items-center">
				<div class="flex items-center gap-2">
					<div class="relative w-12 h-12">
						<div class="w-12 h-12 rounded-full bg-slate-900 flex items-center justify-center">
							<BookMarked class="w-[26px] h-[26px] text-white" stroke-width="2" />
						</div>
					</div>
					<h1 class="text-xl font-semibold leading-7 tracking-[-0.1px] text-slate-900">Method Know</h1>
				</div>
				<div class="flex items-center gap-4">
					<Button
						onclick={handleShareResource}
						class="bg-slate-900 hover:bg-slate-900/90 text-white px-4 py-2 rounded-md text-sm font-medium leading-6 h-auto"
					>
						Share Resource
					</Button>
					<button
						onclick={handleSignOut}
						class="flex items-center gap-1 cursor-pointer"
					>
						<CircleUser class="w-9 h-9 text-slate-900" />
						<span class="text-base leading-7 text-slate-900">
							{$currentUser ? $currentUser.first_name : 'User'}
						</span>
					</button>
				</div>
			</div>
		</div>
	</nav>

	<!-- Main Content -->
	<main class="max-w-[1440px] mx-auto px-[52px] py-0">
		<div class="pt-[74px] pb-0">
			<div class="flex gap-8 items-start">
				<!-- Left Sidebar - Filters -->
				<aside class="w-[240px] shrink-0">
					<Card class="bg-white border border-slate-900/12 rounded-2xl p-4 h-[680px]">
						<div class="flex flex-col gap-[10px]">
							<h3 class="text-lg font-semibold leading-7 text-slate-900">Filters</h3>
							
							<!-- Resource Type Filters -->
							<div class="flex flex-col gap-[10px]">
								<p class="text-base font-normal leading-7 text-slate-900">Resource Type</p>
								<label class="flex gap-2 items-start cursor-pointer">
									<input
										type="checkbox"
										checked={selectedTypes.has('article')}
										onchange={() => toggleType('article')}
										class="w-[14px] h-[14px] rounded border border-gray-300 mt-0.5"
									/>
									<span class="text-sm font-medium leading-[14px] text-black">Articles</span>
								</label>
								<label class="flex gap-2 items-start cursor-pointer">
									<input
										type="checkbox"
										checked={selectedTypes.has('code_snippet')}
										onchange={() => toggleType('code_snippet')}
										class="w-[14px] h-[14px] rounded border border-gray-300 mt-0.5"
									/>
									<span class="text-sm font-medium leading-[14px] text-black">Code Snippets</span>
								</label>
								<label class="flex gap-2 items-start cursor-pointer">
									<input
										type="checkbox"
										checked={selectedTypes.has('learning_resource')}
										onchange={() => toggleType('learning_resource')}
										class="w-[14px] h-[14px] rounded border border-gray-300 mt-0.5"
									/>
									<span class="text-sm font-medium leading-[14px] text-black">Learning Resources</span>
								</label>
							</div>

							<!-- Tags Filters -->
							<div class="flex flex-col gap-[10px] w-full">
								<p class="text-base font-normal leading-7 text-slate-900">Tags</p>
								{#if tagsQuery.data}
									{@const tags = (tagsQuery.data as { tags: Array<{ id?: string; name: string }> }).tags}
									<div class="flex flex-wrap gap-2.5">
										{#each tags as tag}
											{@const tagId = tag.id || tag.name}
											{@const isSelected = selectedTags.has(tagId)}
											<button
												onclick={() => toggleTag(tagId)}
												class="bg-white border {isSelected ? 'border-slate-900' : 'border-slate-900/15'} px-2 py-1 rounded-full text-xs font-medium leading-5 text-black h-[22px] flex items-center cursor-pointer hover:border-slate-900/30 transition-colors"
											>
												{tag.name}
											</button>
										{/each}
									</div>
								{:else if tagsQuery.isLoading}
									<div class="text-sm text-slate-400">Loading tags...</div>
								{/if}
							</div>
						</div>
					</Card>
				</aside>

				<!-- Main Content Area -->
				<div class="flex-1 flex flex-col gap-4">
					<!-- Header Section -->
					<div class="flex flex-col gap-[10px]">
						<h2 class="text-3xl font-semibold leading-9 tracking-[-0.225px] text-slate-900">Discover Resources</h2>
						<p class="text-xl font-normal leading-7 tracking-[-0.1px] text-slate-900">Explore shared knowledge from our community</p>
						
						<!-- Search Input -->
						<div class="flex flex-col gap-1.5">
							<div class="relative flex-1">
								<div class="absolute left-3 top-1/2 -translate-y-1/2">
									<Search class="w-6 h-6 text-slate-400" />
								</div>
								<Input
									type="text"
									bind:value={searchQuery}
									placeholder="Search resource..."
									class="pl-12 pr-14 py-2 h-auto rounded-md border-slate-300 placeholder:text-slate-400 text-base leading-6 bg-white"
								/>
							</div>
						</div>
					</div>

					<!-- Resources Count -->
					<div class="flex items-center justify-start">
						<p class="text-base font-normal leading-7 text-slate-900">
							{#if hasActiveFilters}
								{filteredResources.length} out of {totalResourcesCount} resource{totalResourcesCount !== 1 ? 's' : ''} showing
							{:else}
								{filteredResources.length} resource{filteredResources.length !== 1 ? 's' : ''} found
							{/if}
						</p>
					</div>

					<!-- Resources Grid -->
					{#if resourcesQuery.isLoading}
						<div class="flex justify-center items-center py-12">
							<Loader2 class="h-8 w-8 animate-spin text-slate-900" />
						</div>
					{:else if resourcesQuery.isError}
						<Card class="border-red-500">
							<CardContent class="pt-6">
								<p class="text-sm font-medium text-red-800">
									Error loading resources: {resourcesQuery.error?.message || 'Unknown error'}
								</p>
							</CardContent>
						</Card>
					{:else if filteredResources.length > 0}
						<div class="flex flex-col gap-4 h-[649px] overflow-y-auto">
							{#each Array(Math.ceil(filteredResources.length / 2)) as _, rowIndex}
								{@const startIdx = rowIndex * 2}
								{@const rowResources = filteredResources.slice(startIdx, startIdx + 2)}
								<div class="flex gap-4">
									{#each rowResources as resource}
										{@const TypeIcon = getResourceTypeIcon(resource)}
										<Card class="flex-1 bg-white border border-slate-900/12 rounded-2xl p-4">
											<CardContent class="pt-2.5 pb-0 px-0">
												<div class="flex flex-col gap-[10px]">
													<!-- Header with type badge and actions -->
													<div class="flex items-center justify-between">
														<div class="bg-white border border-slate-900/15 rounded-full flex gap-2 h-7 items-center justify-center px-2">
															<TypeIcon class="w-5 h-5 text-black" />
															<span class="text-sm font-medium leading-[14px] text-black">
																{getResourceTypeName(resource)}
															</span>
														</div>
														{#if isOwnResource(resource)}
															<div class="flex gap-2.5 items-center">
																<button class="w-6 h-6 cursor-pointer">
																	<Pencil class="w-6 h-6 text-slate-900" />
																</button>
																<button class="w-6 h-6 cursor-pointer">
																	<Trash2 class="w-6 h-6 text-slate-900" />
																</button>
															</div>
														{/if}
													</div>

													<!-- Title -->
													<h3 class="text-lg font-semibold leading-7 text-slate-900">
														{resource.title}
													</h3>

													<!-- Description and Link -->
													<div class="flex flex-col gap-[10px]">
														<p class="text-base font-normal leading-7 text-slate-900">
															{resource.description}
														</p>
														{#if resource.type === 'article' && resource.url}
															<a
																href={resource.url}
																target="_blank"
																rel="noopener noreferrer"
																class="flex gap-2 items-center text-base font-bold leading-7 text-slate-900 underline"
															>
																<ExternalLink class="w-5 h-5" />
																View article
															</a>
														{:else if (resource.type === 'book' || resource.type === 'course') && 'author' in resource}
															<div class="flex gap-2 items-center">
																<BookOpenText class="w-5 h-5 text-slate-900" />
																<span class="text-base font-normal leading-7 text-slate-900">
																	by {(resource as any).author || 'Unknown'}
																</span>
															</div>
														{/if}
													</div>

													<!-- Tags -->
													{#if resource.tags && resource.tags.length > 0}
														<div class="flex flex-wrap gap-2.5 pt-1 pb-2">
															{#each resource.tags as tag}
																<span class="bg-white border border-slate-900/15 px-2 py-1 rounded-full text-xs font-medium leading-5 text-black h-[22px] flex items-center">
																	{tag.name}
																</span>
															{/each}
														</div>
													{/if}

													<!-- Divider -->
													<div class="h-px bg-slate-200 w-full"></div>

													<!-- Footer with user and date -->
													<div class="flex items-center justify-between">
														<div class="flex gap-1 items-center">
															<CircleUser class="w-9 h-9 text-slate-900" />
															<span class="text-base font-normal leading-7 text-slate-900">
																{isOwnResource(resource) ? 'You' : getUserName(resource)}
															</span>
														</div>
														<span class="text-base font-normal leading-7 text-black/50 text-center">
															{formatDate(resource)}
														</span>
													</div>
												</div>
											</CardContent>
										</Card>
									{/each}
								</div>
							{/each}
						</div>
					{:else}
						<Card>
							<CardContent class="pt-6 text-center">
								<p class="text-base font-normal leading-7 text-slate-900">No resources found</p>
								<p class="text-sm font-normal leading-7 text-slate-900/70 mt-2">
									Be the first to share a resource with the community!
								</p>
							</CardContent>
						</Card>
					{/if}
				</div>
			</div>
		</div>
	</main>
</div>

