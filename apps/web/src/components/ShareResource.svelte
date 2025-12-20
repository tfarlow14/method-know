<script lang="ts">
	import { createMutation, createQuery, useQueryClient } from '@tanstack/svelte-query';
	import { resourceMutations, tagMutations, tagQueries, type ResourceInput, type ResourceType, RESOURCE_TYPES, type Resource } from '../lib/api/queries';
	import { Button } from '$lib/components/ui/button';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';
	import { X } from '@lucide/svelte';
	import { Loader2 } from '@lucide/svelte';
	import CodeEditor from './CodeEditor.svelte';

	interface Props {
		isOpen?: boolean;
		onClose?: () => void;
		resource?: Resource | null;
		onSuccess?: (isEdit: boolean) => void;
	}

	let { isOpen = $bindable(false), onClose = () => {}, resource = null, onSuccess }: Props = $props();

	const queryClient = useQueryClient();

	// Form state
	let resourceType = $state<ResourceType>(RESOURCE_TYPES.ARTICLE);
	let title = $state('');
	let description = $state('');
	let url = $state('');
	let code = $state('');
	let author = $state('');
	let tagInput = $state('');
	let selectedTags = $state<Array<{ id?: string; name: string; isNew?: boolean }>>([]);
	let isTagDropdownOpen = $state(false);
	let tagSearchQuery = $state('');

	// Fetch existing tags
	const tagsQuery = createQuery(() => tagQueries.all());
	const tags = $derived(tagsQuery.data?.tags || []);

	// Filter tags based on search query and exclude already selected
	const filteredTags = $derived.by(() => {
		const query = tagSearchQuery.toLowerCase().trim();
		const selectedTagNames = new Set(selectedTags.map(t => t.name.toLowerCase()));
		
		return tags.filter(tag => {
			const isNotSelected = !selectedTagNames.has(tag.name.toLowerCase());
			const matchesQuery = !query || tag.name.toLowerCase().includes(query);
			return isNotSelected && matchesQuery;
		});
	});

	// Tag creation mutation (used only when submitting resource)
	const createTagMutation = createMutation(() => ({
		...tagMutations.create()
	}));

	// Resource creation mutation
	const createResourceMutation = createMutation(() => ({
		...resourceMutations.create(),
		onSuccess: () => {
			// Reset form
			resourceType = RESOURCE_TYPES.ARTICLE;
			title = '';
			description = '';
			url = '';
			code = '';
			tagInput = '';
			tagSearchQuery = '';
			selectedTags = [];
			isTagDropdownOpen = false;
			// Invalidate queries to refresh lists
			queryClient.invalidateQueries({ queryKey: ['resources'] });
			queryClient.invalidateQueries({ queryKey: ['tags'] });
			// Close modal
			onClose();
			// Notify parent of success
			onSuccess?.(false);
		}
	}));

	// Resource update mutation
	const updateResourceMutation = createMutation(() => ({
		...resourceMutations.update(),
		onSuccess: () => {
			// Reset form
			resourceType = RESOURCE_TYPES.ARTICLE;
			title = '';
			description = '';
			url = '';
			code = '';
			author = '';
			tagInput = '';
			tagSearchQuery = '';
			selectedTags = [];
			isTagDropdownOpen = false;
			// Invalidate queries to refresh lists
			queryClient.invalidateQueries({ queryKey: ['resources'] });
			queryClient.invalidateQueries({ queryKey: ['tags'] });
			// Close modal
			onClose();
			// Notify parent of success
			onSuccess?.(true);
		}
	}));

	// Check if we're in edit mode
	const isEditMode = $derived(!!resource);
	const editingResourceId = $derived(resource?.id || null);

	function handleAddTag(tagName?: string) {
		const nameToAdd = (tagName || tagSearchQuery).trim();
		if (!nameToAdd) return;

		// Check if tag already exists
		const existingTag = tags.find(t => t.name.toLowerCase() === nameToAdd.toLowerCase());
		if (existingTag) {
			// Add existing tag if not already selected
			if (!selectedTags.find(t => t.id === existingTag.id || t.name === existingTag.name)) {
				selectedTags = [...selectedTags, existingTag];
				tagSearchQuery = '';
				isTagDropdownOpen = false;
			}
		} else {
			// Add as new tag (not yet created in database)
			if (!selectedTags.find(t => t.name.toLowerCase() === nameToAdd.toLowerCase())) {
				selectedTags = [...selectedTags, { name: nameToAdd, isNew: true }];
				tagSearchQuery = '';
				isTagDropdownOpen = false;
			}
		}
	}

	function handleSelectTag(tag: { id?: string; name: string }) {
		if (!selectedTags.find(t => t.id === tag.id || t.name === tag.name)) {
			selectedTags = [...selectedTags, tag];
			tagSearchQuery = '';
			isTagDropdownOpen = false;
		}
	}

	function handleRemoveTag(tagToRemove: { id?: string; name: string }) {
		selectedTags = selectedTags.filter(t => 
			t.id !== tagToRemove.id && t.name !== tagToRemove.name
		);
	}

	async function handleSubmit() {
		if (!title.trim() || !description.trim()) {
			return;
		}

		// Validate type-specific fields
		if (resourceType === RESOURCE_TYPES.ARTICLE && !url.trim()) {
			return;
		}
		if (resourceType === RESOURCE_TYPES.CODE_SNIPPET && !code.trim()) {
			return;
		}

		try {
			// First, create any new tags
			const newTagNames = selectedTags.filter(t => t.isNew).map(t => t.name);
			const createdTags: Array<{ id: string; name: string }> = [];

			for (const tagName of newTagNames) {
				const newTag = await createTagMutation.mutateAsync({ name: tagName });
				createdTags.push(newTag);
			}

			// Get all tag IDs (existing + newly created)
			const tagIds = selectedTags
				.map(tag => {
					if (tag.isNew) {
						// Find the newly created tag
						const createdTag = createdTags.find(t => t.name === tag.name);
						return createdTag?.id;
					} else {
						// Use existing tag ID
						const existingTag = tags.find(t => t.name === tag.name);
						return existingTag?.id || tag.id;
					}
				})
				.filter((id): id is string => !!id);

			// Build resource input based on type
			let resourceInput: ResourceInput;
			
			if (resourceType === RESOURCE_TYPES.ARTICLE) {
				resourceInput = {
					type: RESOURCE_TYPES.ARTICLE,
					title: title.trim(),
					description: description.trim(),
					url: url.trim(),
					tag_ids: tagIds
				};
			} else if (resourceType === RESOURCE_TYPES.CODE_SNIPPET) {
				resourceInput = {
					type: RESOURCE_TYPES.CODE_SNIPPET,
					title: title.trim(),
					description: description.trim(),
					code: code.trim(),
					tag_ids: tagIds
				};
			} else 			if (resourceType === RESOURCE_TYPES.BOOK) {
				resourceInput = {
					type: RESOURCE_TYPES.BOOK,
					title: title.trim(),
					description: description.trim(),
					author: author.trim() || undefined,
					tag_ids: tagIds
				};
			} else {
				resourceInput = {
					type: RESOURCE_TYPES.COURSE,
					title: title.trim(),
					description: description.trim(),
					author: author.trim() || undefined,
					tag_ids: tagIds
				};
			}

			// Create or update the resource
			if (isEditMode && editingResourceId) {
				await updateResourceMutation.mutateAsync({
					id: editingResourceId,
					data: resourceInput
				});
			} else {
				await createResourceMutation.mutateAsync(resourceInput);
			}
		} catch (error) {
			// Error handling is done by the mutation
			console.error(`Error ${isEditMode ? 'updating' : 'creating'} resource:`, error);
		}
	}

	function handleCancel() {
		// Reset form
		resourceType = RESOURCE_TYPES.ARTICLE;
		title = '';
		description = '';
		url = '';
		code = '';
		author = '';
		tagInput = '';
		tagSearchQuery = '';
		selectedTags = [];
		isTagDropdownOpen = false;
		onClose();
	}


	// Check if form is valid
	const isFormValid = $derived.by(() => {
		if (!title.trim() || !description.trim()) return false;
		if (resourceType === RESOURCE_TYPES.ARTICLE && !url.trim()) return false;
		if (resourceType === RESOURCE_TYPES.CODE_SNIPPET && !code.trim()) return false;
		return true;
	});

	// Close dropdown when clicking outside
	function handleClickOutside(event: MouseEvent) {
		const target = event.target as HTMLElement;
		if (!target.closest('.tag-dropdown-container')) {
			isTagDropdownOpen = false;
		}
	}

	// Add click outside listener
	$effect(() => {
		if (isTagDropdownOpen) {
			document.addEventListener('click', handleClickOutside);
			return () => document.removeEventListener('click', handleClickOutside);
		}
	});

	// Populate form when resource is provided (edit mode)
	$effect(() => {
		if (resource && isOpen) {
			resourceType = resource.type as ResourceType;
			title = resource.title;
			description = resource.description;
			
			if (resource.type === RESOURCE_TYPES.ARTICLE && 'url' in resource) {
				url = resource.url || '';
			} else if (resource.type === RESOURCE_TYPES.COURSE && 'url' in resource) {
				url = resource.url || '';
			} else if (resource.type === RESOURCE_TYPES.CODE_SNIPPET && 'code' in resource) {
				code = resource.code || '';
			}
			
			// Populate author for Book and Course
			if ((resource.type === RESOURCE_TYPES.BOOK || resource.type === RESOURCE_TYPES.COURSE) && 'author' in resource) {
				author = resource.author || '';
			}
			
			// Populate tags from resource
			selectedTags = resource.tags.map(tag => ({
				id: tag.id,
				name: tag.name
			}));
		} else if (!resource && isOpen) {
			// Reset form when opening in create mode
			resourceType = RESOURCE_TYPES.ARTICLE;
			title = '';
			description = '';
			url = '';
			code = '';
			author = '';
			selectedTags = [];
			tagSearchQuery = '';
			isTagDropdownOpen = false;
		}
	});
</script>

{#if isOpen}
	<!-- Backdrop -->
	<div 
		class="fixed inset-0 z-40"
		onclick={handleCancel}
		role="button"
		tabindex="-1"
	></div>

	<!-- Modal -->
	<div class="fixed right-[52px] top-[117px] w-[511px] h-[85vh] bg-white border border-slate-100 rounded-md shadow-lg z-50 flex flex-col p-4 gap-4 overflow-hidden">
		<!-- Header -->
		<div class="flex items-center justify-between shrink-0">
			<h2 class="text-lg font-semibold leading-7 text-slate-900">
				{isEditMode ? 'Edit resource' : 'Share a resource'}
			</h2>
			<button
				onclick={handleCancel}
				class="w-6 h-6 flex items-center justify-center cursor-pointer hover:bg-slate-100 rounded"
				aria-label="Close"
			>
				<X class="w-5 h-5 text-slate-900" />
			</button>
		</div>

		{#if !isEditMode}
			<p class="text-base font-normal leading-7 text-slate-900 shrink-0">
				Contribute to the knowledge base by sharing valuable content
			</p>
		{/if}

		<!-- Form -->
		<form 
			class="flex flex-col gap-4 flex-1 min-h-0 overflow-hidden"
			onsubmit={(e) => {
				e.preventDefault();
				handleSubmit();
			}}
		>
			<!-- Scrollable content area -->
			<div class="flex flex-col gap-4 flex-1 min-h-0 overflow-y-auto pr-1">
			<!-- Resource Type (only show in create mode) -->
			{#if !isEditMode}
				<div class="flex flex-col gap-1.5 shrink-0">
					<Label for="resource-type" class="text-sm font-medium leading-5 text-slate-900">
						Resource Type
					</Label>
					<select
						id="resource-type"
						bind:value={resourceType}
						class="h-auto w-full rounded-md border border-slate-300 text-base leading-6 pl-3 pr-10 py-2 bg-white box-border focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-transparent"
					>
						<option value={RESOURCE_TYPES.ARTICLE}>Article</option>
						<option value={RESOURCE_TYPES.CODE_SNIPPET}>Code Snippet</option>
						<option value={RESOURCE_TYPES.BOOK}>Book</option>
						<option value={RESOURCE_TYPES.COURSE}>Course</option>
					</select>
				</div>
			{/if}

			<!-- Title -->
			<div class="flex flex-col gap-1.5 shrink-0">
				<Label for="title" class="text-sm font-medium leading-5 text-slate-900">
					Title
				</Label>
				<Input
					id="title"
					type="text"
					bind:value={title}
					placeholder="Enter a descriptive title"
					required
					class="h-auto w-full rounded-md border-slate-300 placeholder:text-slate-400 text-base leading-6 pl-3 pr-3 py-2 bg-white box-border"
				/>
			</div>

			<!-- Description -->
			<div class="flex flex-col gap-1.5 shrink-0">
				<Label for="description" class="text-sm font-medium leading-5 text-slate-900">
					Description
				</Label>
				<textarea
					id="description"
					bind:value={description}
					placeholder="Provide a detailed description"
					required
					rows="4"
					class="w-full rounded-md border border-slate-300 placeholder:text-slate-400 text-base leading-6 pl-3 pr-3 py-2 bg-white box-border resize-none focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-transparent"
				></textarea>
			</div>

			<!-- Author (for Book and Course) -->
			{#if resourceType === RESOURCE_TYPES.BOOK || resourceType === RESOURCE_TYPES.COURSE}
				<div class="flex flex-col gap-1.5 shrink-0">
					<Label for="author" class="text-sm font-medium leading-5 text-slate-900">
						Author
					</Label>
					<Input
						id="author"
						type="text"
						bind:value={author}
						placeholder="Enter author name"
						class="h-auto w-full rounded-md border-slate-300 placeholder:text-slate-400 text-base leading-6 pl-3 pr-3 py-2 bg-white box-border"
					/>
				</div>
			{/if}

			<!-- Tags -->
			<div class="flex flex-col gap-1.5 shrink-0 tag-dropdown-container relative">
				<Label for="tags" class="text-sm font-medium leading-5 text-slate-900">
					Tags
				</Label>
				<div class="flex gap-2 relative">
					<div class="flex-1 relative">
						<div 
							class="min-h-[42px] w-full rounded-md border border-slate-300 bg-white box-border flex flex-wrap items-center gap-1.5 px-2 py-1.5 cursor-text focus-within:ring-2 focus-within:ring-slate-900 focus-within:border-transparent"
							onclick={() => {
								const input = document.getElementById('tags-input') as HTMLInputElement;
								input?.focus();
							}}
						>
							{#each selectedTags as tag}
								<span class="bg-slate-900 px-2 py-0.5 rounded-full text-xs font-medium leading-5 text-white h-[22px] flex items-center gap-1 shrink-0">
									{tag.name}
									<button
										type="button"
										onclick={(e) => {
											e.stopPropagation();
											handleRemoveTag(tag);
										}}
										class="ml-0.5 hover:text-slate-300 flex items-center text-white"
										aria-label="Remove tag"
									>
										<X class="w-3 h-3" />
									</button>
								</span>
							{/each}
							<input
								id="tags-input"
								type="text"
								bind:value={tagSearchQuery}
								onfocus={() => isTagDropdownOpen = true}
								onkeydown={(e) => {
									if (e.key === 'Enter') {
										e.preventDefault();
										if (tagSearchQuery.trim()) {
											handleAddTag(tagSearchQuery);
										}
									} else if (e.key === 'Escape') {
										isTagDropdownOpen = false;
									} else if (e.key === 'Backspace' && !tagSearchQuery && selectedTags.length > 0) {
										// Remove last tag on backspace when input is empty
										handleRemoveTag(selectedTags[selectedTags.length - 1]);
									}
								}}
								placeholder={selectedTags.length === 0 ? "Search or create tags" : ""}
								class="flex-1 min-w-[120px] outline-none text-base leading-6 text-slate-900 placeholder:text-slate-400 bg-transparent border-none"
							/>
						</div>
						{#if isTagDropdownOpen && (filteredTags.length > 0 || tagSearchQuery.trim())}
							<div class="absolute z-50 w-full mt-1 bg-white border border-slate-300 rounded-md shadow-lg max-h-60 overflow-y-auto">
								{#if filteredTags.length > 0}
									{#each filteredTags as tag}
										<button
											type="button"
											onclick={() => handleSelectTag(tag)}
											class="w-full text-left px-3 py-2 hover:bg-slate-100 text-sm text-slate-900"
										>
											{tag.name}
										</button>
									{/each}
								{/if}
								{#if tagSearchQuery.trim() && !tags.find(t => t.name.toLowerCase() === tagSearchQuery.toLowerCase().trim())}
									<button
										type="button"
										onclick={() => handleAddTag(tagSearchQuery)}
										class="w-full text-left px-3 py-2 hover:bg-slate-100 text-sm text-slate-600 border-t border-slate-200"
									>
										Add "{tagSearchQuery.trim()}"
									</button>
								{/if}
							</div>
						{/if}
					</div>
				</div>
			</div>

			<!-- URL (conditional for article and course) -->
			{#if resourceType === RESOURCE_TYPES.ARTICLE || resourceType === RESOURCE_TYPES.COURSE}
				<div class="flex flex-col gap-1.5 shrink-0">
					<Label for="url" class="text-sm font-medium leading-5 text-slate-900">
						{resourceType === RESOURCE_TYPES.ARTICLE ? 'Article URL' : 'Course URL'}
					</Label>
					<Input
						id="url"
						type="url"
						bind:value={url}
						placeholder="example.com/article"
						required={resourceType === RESOURCE_TYPES.ARTICLE}
						class="h-auto w-full rounded-md border-slate-300 placeholder:text-slate-400 text-base leading-6 pl-3 pr-3 py-2 bg-white box-border"
					/>
				</div>
			{/if}

			<!-- Code (conditional) -->
			{#if resourceType === RESOURCE_TYPES.CODE_SNIPPET}
				<div class="flex flex-col gap-1.5 shrink-0">
					<Label for="code" class="text-sm font-medium leading-5 text-slate-900">
						Code
					</Label>
					<div class="h-[300px] w-full">
						<CodeEditor
							bind:code={code}
							language="auto"
							theme="dark"
							readOnly={false}
						/>
					</div>
				</div>
			{/if}

			</div>

			<!-- Fixed footer with buttons -->
			<div class="shrink-0 flex flex-col gap-4 pt-4 border-t border-slate-200">
				<div class="flex gap-4">
					<Button
						type="button"
						onclick={handleCancel}
						class="flex-1 h-auto rounded-md border border-black/10 bg-white hover:bg-slate-50 font-medium text-sm leading-6 px-4 py-2 text-black"
					>
						Cancel
					</Button>
					<Button
						type="submit"
						disabled={!isFormValid || createResourceMutation.isPending || updateResourceMutation.isPending}
						class="flex-1 h-auto rounded-md bg-slate-900 hover:bg-slate-900/90 font-medium text-sm leading-6 px-4 py-2 text-white disabled:opacity-50 disabled:cursor-not-allowed"
					>
						{#if createResourceMutation.isPending || updateResourceMutation.isPending}
							<Loader2 class="mr-2 h-4 w-4 animate-spin inline" />
							{isEditMode ? 'Saving...' : 'Sharing...'}
						{:else}
							{isEditMode ? 'Save Changes' : 'Share'}
						{/if}
					</Button>
				</div>
			</div>
		</form>
	</div>
{/if}

