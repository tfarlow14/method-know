<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '../lib/router';
	import { isAuthenticated, clearAuthToken } from '../lib/auth';
	import { currentUser } from '../lib/stores';
	import { createQuery, createMutation, useQueryClient } from '@tanstack/svelte-query';
	import { resourceQueries, resourceMutations, tagQueries, type ResourceCollection, type Resource, RESOURCE_TYPES } from '../lib/api/queries';
	import { Card, CardContent } from '$lib/components/ui/card';
	import { Button } from '$lib/components/ui/button';
	import { Input } from '$lib/components/ui/input';
	import { Loader2, ExternalLink, Code, BookOpen, LogOut, Search, BookMarked, CircleUser, Newspaper, Pencil, Trash2, GraduationCap, BookOpenText } from '@lucide/svelte';
	import ShareResource from '../components/ShareResource.svelte';
	import UserDropdown from '../components/UserDropdown.svelte';
	import ResourceCard from '../components/ResourceCard.svelte';
	import DeleteResourceModal from '../components/DeleteResourceModal.svelte';
	import SuccessBanner from '../components/SuccessBanner.svelte';
	import FiltersSidebar from '../components/FiltersSidebar.svelte';

	let searchQuery = $state('');
	let selectedTypes = $state<Set<string>>(new Set([RESOURCE_TYPES.ARTICLE, RESOURCE_TYPES.CODE_SNIPPET, 'learning_resource']));
	let selectedTags = $state<Set<string>>(new Set());
	let isShareResourceOpen = $state(false);
	let isUserDropdownOpen = $state(false);
	let userButtonRef: HTMLButtonElement | null = $state(null);
	let editingResource: Resource | null = $state(null);
	let deletingResource: Resource | null = $state(null);
	let isDeleteModalOpen = $state(false);
	let showSuccessBanner = $state(false);
	let successBannerMessage = $state('');
	let successBannerActionLabel = $state<string | undefined>(undefined);
	let successBannerActionUrl = $state<string | undefined>(undefined);
	
	// Get current user from Svelte store
	const currentUserId = $derived($currentUser?.id || null);
	const queryClient = useQueryClient();

	function handleSignOut() {
		clearAuthToken();
		currentUser.set(null); // Clear user from store
		goto('/login');
	}

	function handleShareResource() {
		isShareResourceOpen = true;
	}

	function handleCloseShareResource() {
		isShareResourceOpen = false;
		editingResource = null;
	}

	function handleResourceSuccess(isEdit: boolean) {
		if (isEdit) {
			successBannerMessage = 'Resource updated!';
			successBannerActionLabel = undefined;
			successBannerActionUrl = undefined;
		} else {
			successBannerMessage = 'New resource successfully added!';
			successBannerActionLabel = 'View Your Resources';
			successBannerActionUrl = '/your-resources';
		}
		showSuccessBanner = true;
	}

	function handleEditResource(resource: Resource) {
		editingResource = resource;
		isShareResourceOpen = true;
	}

	function handleDeleteResource(resource: Resource) {
		deletingResource = resource;
		isDeleteModalOpen = true;
	}

	function handleCloseDeleteModal() {
		isDeleteModalOpen = false;
		deletingResource = null;
	}

	// Delete resource mutation
	const deleteResourceMutation = createMutation(() => ({
		...resourceMutations.delete(),
		onSuccess: () => {
			// Invalidate queries to refresh lists
			queryClient.invalidateQueries({ queryKey: ['resources'] });
			handleCloseDeleteModal();
		},
		onError: (error) => {
			console.error('Error deleting resource:', error);
			// Keep modal open on error so user can try again or cancel
		}
	}));

	function handleConfirmDelete(resource: Resource) {
		if (resource?.id) {
			deleteResourceMutation.mutate(resource.id);
		} else {
			console.error('Cannot delete resource: missing ID', resource);
		}
	}

	function toggleUserDropdown(event: MouseEvent) {
		event.stopPropagation();
		isUserDropdownOpen = !isUserDropdownOpen;
	}

	function handleClickOutside(event: MouseEvent) {
		const target = event.target as HTMLElement;
		if (!target.closest('.user-dropdown-container')) {
			isUserDropdownOpen = false;
		}
	}

	function handleUserDropdownLogout() {
		handleSignOut();
	}

	// Add click outside listener for user dropdown
	$effect(() => {
		if (isUserDropdownOpen) {
			document.addEventListener('click', handleClickOutside);
			return () => document.removeEventListener('click', handleClickOutside);
		}
	});

	// Fetch resources and tags
	const resourcesQuery = createQuery(() => resourceQueries.all());
	const tagsQuery = createQuery(() => tagQueries.all());

	// Log API errors to console
	$effect(() => {
		if (resourcesQuery.isError && resourcesQuery.error) {
			console.error('API Error loading resources:', resourcesQuery.error);
		}
		if (tagsQuery.isError && tagsQuery.error) {
			console.error('API Error loading tags:', tagsQuery.error);
		}
	});

	// Get user name from resource (returns first name only)
	function getUserName(resource: Resource): string {
		// Resources always include user data from the backend
		if (resource.user?.first_name) {
			return resource.user.first_name;
		}
		// Fallback to current user if it's the logged-in user's resource
		if (isOwnResource(resource) && $currentUser) {
			return $currentUser.first_name;
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
			selectedTypes.has(RESOURCE_TYPES.ARTICLE) && 
			selectedTypes.has(RESOURCE_TYPES.CODE_SNIPPET) && 
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
				if (r.type === RESOURCE_TYPES.ARTICLE) return selectedTypes.has(RESOURCE_TYPES.ARTICLE);
				if (r.type === RESOURCE_TYPES.CODE_SNIPPET) return selectedTypes.has(RESOURCE_TYPES.CODE_SNIPPET);
				if (r.type === RESOURCE_TYPES.BOOK || r.type === RESOURCE_TYPES.COURSE) return selectedTypes.has('learning_resource');
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
		if (resource.type === RESOURCE_TYPES.ARTICLE) return 'Article';
		if (resource.type === RESOURCE_TYPES.CODE_SNIPPET) return 'Code Snippet';
		if (resource.type === RESOURCE_TYPES.BOOK) return 'Book';
		if (resource.type === RESOURCE_TYPES.COURSE) return 'Course';
		return 'Learning Resource';
	}

	// Get resource type icon
	function getResourceTypeIcon(resource: Resource) {
		if (resource.type === RESOURCE_TYPES.ARTICLE) return Newspaper;
		if (resource.type === RESOURCE_TYPES.CODE_SNIPPET) return Code;
		if (resource.type === RESOURCE_TYPES.BOOK) return BookOpenText;
		if (resource.type === RESOURCE_TYPES.COURSE) return GraduationCap;
		return BookOpen;
	}

	// Format date from created_at timestamp
	function formatDate(resource: Resource): string {
		if (!resource.created_at) {
			return 'Unknown';
		}
		
		const date = new Date(resource.created_at);
		const now = new Date();
		
		// Get date strings in YYYY-MM-DD format for accurate day comparison
		const dateStr = date.toLocaleDateString('en-CA'); // Returns YYYY-MM-DD format
		const nowStr = now.toLocaleDateString('en-CA');
		
		if (dateStr === nowStr) {
			return 'Today';
		}
		
		// Calculate difference in days
		const dateStart = new Date(date.getFullYear(), date.getMonth(), date.getDate());
		const nowStart = new Date(now.getFullYear(), now.getMonth(), now.getDate());
		const diffMs = nowStart.getTime() - dateStart.getTime();
		const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
		
		if (diffDays === 1) {
			return 'Yesterday';
		} else if (diffDays > 1) {
			return `${diffDays} days ago`;
		} else {
			// If diffDays is 0 or negative (same day or future), show as "Today"
			return 'Today';
		}
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
				<a href="/" class="flex items-center gap-2 cursor-pointer hover:opacity-80 transition-opacity">
					<div class="relative w-12 h-12">
						<div class="w-12 h-12 rounded-full bg-slate-900 flex items-center justify-center">
							<BookMarked class="w-[26px] h-[26px] text-white" stroke-width="2" />
						</div>
					</div>
					<h1 class="text-xl font-semibold leading-7 tracking-[-0.1px] text-slate-900">Method Know</h1>
				</a>
				<div class="flex items-center gap-4">
					<Button
						onclick={handleShareResource}
						class="bg-slate-900 hover:bg-slate-900/90 text-white px-4 py-2 rounded-md text-sm font-medium leading-6 h-auto"
					>
						Share Resource
					</Button>
					<div class="relative user-dropdown-container">
						<button
							bind:this={userButtonRef}
							onclick={toggleUserDropdown}
							class="flex items-center gap-1 cursor-pointer"
						>
							<CircleUser class="w-9 h-9 text-slate-900" />
							<span class="text-base leading-7 text-slate-900">
								{$currentUser ? $currentUser.first_name : 'User'}
							</span>
						</button>
						<UserDropdown
							bind:isOpen={isUserDropdownOpen}
							onClose={() => isUserDropdownOpen = false}
							onlogout={handleUserDropdownLogout}
						/>
					</div>
				</div>
			</div>
		</div>
	</nav>

	<!-- Main Content -->
	<main class="max-w-[1440px] mx-auto px-[52px] py-0">
		<div class="pt-[74px] pb-0">
			<div class="flex flex-col">
				<!-- Header Section -->
				<div class="flex flex-col gap-[10px]">
					<h2 class="text-3xl font-semibold leading-9 tracking-[-0.225px] text-slate-900 text-left">Discover Resources</h2>
					<p class="text-xl font-normal leading-7 tracking-[-0.1px] text-slate-900 text-left">Explore shared knowledge from our community</p>
				</div>
				
				<!-- Search Input -->
				<div class="flex flex-col gap-[6px] mt-[10px]">
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

				<!-- Spacer between search and filters/content -->
				<div class="h-[44px]"></div>

				<!-- Filters and Content Layout -->
				<div class="flex gap-[32px] items-start">
					<!-- Left Sidebar - Filters -->
					<aside class="w-[240px] shrink-0">
						<FiltersSidebar
							selectedTypes={selectedTypes}
							selectedTags={selectedTags}
							onTypeToggle={toggleType}
							onTagToggle={toggleTag}
						/>
					</aside>

					<!-- Main Content Area -->
					<div class="flex-1 flex flex-col gap-[16px]">
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
							<div class="h-[649px] overflow-y-auto scrollbar-hide pb-[31px]">
								<div class="grid grid-cols-2 gap-4 items-start">
									{#each filteredResources as resource}
										<ResourceCard
											{resource}
											showActions={isOwnResource(resource)}
											showUser={true}
											userName={isOwnResource(resource) ? 'You' : getUserName(resource)}
											onEdit={handleEditResource}
											onDelete={handleDeleteResource}
										/>
									{/each}
								</div>
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
		</div>
	</main>

	<!-- Share Resource Modal -->
	<ShareResource 
		isOpen={isShareResourceOpen} 
		onClose={handleCloseShareResource}
		resource={editingResource}
		onSuccess={handleResourceSuccess}
	/>

	<!-- Delete Resource Modal -->
	<DeleteResourceModal
		isOpen={isDeleteModalOpen}
		resource={deletingResource}
		onClose={handleCloseDeleteModal}
		onConfirm={handleConfirmDelete}
		isDeleting={deleteResourceMutation.isPending}
	/>

	<!-- Success Banner -->
	<SuccessBanner
		isOpen={showSuccessBanner}
		message={successBannerMessage}
		actionLabel={successBannerActionLabel}
		actionUrl={successBannerActionUrl}
		onClose={() => showSuccessBanner = false}
	/>
</div>

