<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '../lib/router';
	import { isAuthenticated, clearAuthToken } from '../lib/auth';
	import { currentUser } from '../lib/stores';
	import { createQuery, createMutation, useQueryClient } from '@tanstack/svelte-query';
	import { resourceQueries, resourceMutations, type ResourceCollection, type Resource, RESOURCE_TYPES } from '../lib/api/queries';
	import { Button } from '$lib/components/ui/button';
	import { Input } from '$lib/components/ui/input';
	import { Card, CardContent } from '$lib/components/ui/card';
	import { Loader2, Search, BookMarked, CircleUser } from '@lucide/svelte';
	import ShareResource from '../components/ShareResource.svelte';
	import UserDropdown from '../components/UserDropdown.svelte';
	import ResourceCard from '../components/ResourceCard.svelte';
	import FiltersSidebar from '../components/FiltersSidebar.svelte';
	import DeleteResourceModal from '../components/DeleteResourceModal.svelte';
	import SuccessBanner from '../components/SuccessBanner.svelte';
	import ResourceDetailsModal from '../components/ResourceDetailsModal.svelte';

	let searchQuery = $state('');
	let selectedTypes = $state<Set<string>>(new Set([RESOURCE_TYPES.ARTICLE, RESOURCE_TYPES.CODE_SNIPPET, 'learning_resource']));
	let selectedTags = $state<Set<string>>(new Set());
	let isShareResourceOpen = $state(false);
	let isUserDropdownOpen = $state(false);
	let userButtonRef: HTMLButtonElement | null = $state(null);
	let editingResource: Resource | null = $state(null);
	let deletingResource: Resource | null = $state(null);
	let isDeleteModalOpen = $state(false);
	let viewingResource: Resource | null = $state(null);
	let isDetailsModalOpen = $state(false);
	let showSuccessBanner = $state(false);
	let successBannerMessage = $state('');
	let successBannerActionLabel = $state<string | undefined>(undefined);
	let successBannerActionUrl = $state<string | undefined>(undefined);
	
	// Get current user from Svelte store
	const currentUserId = $derived($currentUser?.id || null);
	const queryClient = useQueryClient();

	function handleSignOut() {
		clearAuthToken();
		currentUser.set(null);
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
			successBannerActionLabel = undefined;
			successBannerActionUrl = undefined;
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

	function handleViewResource(resource: Resource) {
		viewingResource = resource;
		isDetailsModalOpen = true;
	}

	function handleCloseDetailsModal() {
		isDetailsModalOpen = false;
		viewingResource = null;
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

	// Log API errors to console
	$effect(() => {
		if (resourcesQuery.isError && resourcesQuery.error) {
			console.error('API Error loading resources:', resourcesQuery.error);
		}
	});

	// Filter resources to only show current user's resources
	const filteredResources = $derived.by(() => {
		if (!resourcesQuery.data || !currentUserId) return [];
		const data = resourcesQuery.data as ResourceCollection;
		let resources = (data.resources || []).filter(r => {
			// Only show resources owned by current user
			if (!r.user?.id) return false;
			return String(r.user.id) === String(currentUserId);
		});

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
					<h2 class="text-3xl font-semibold leading-9 tracking-[-0.225px] text-slate-900 text-left">Your resources</h2>
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
							placeholder="Search resource by title or description..."
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
								{filteredResources.length} resource{filteredResources.length !== 1 ? 's' : ''} you've added
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
											showActions={true}
											showUser={true}
											userName="You"
											onEdit={handleEditResource}
											onDelete={handleDeleteResource}
											onClick={handleViewResource}
										/>
									{/each}
								</div>
							</div>
						{:else}
							<Card>
								<CardContent class="pt-6 text-center">
									<p class="text-base font-normal leading-7 text-slate-900">No resources found</p>
									<p class="text-sm font-normal leading-7 text-slate-900/70 mt-2">
										Share your first resource to get started!
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

	<!-- Resource Details Modal -->
	<ResourceDetailsModal
		isOpen={isDetailsModalOpen}
		resource={viewingResource}
		onClose={handleCloseDetailsModal}
	/>
</div>

