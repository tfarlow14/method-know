<script lang="ts">
	import { Card, CardContent } from '$lib/components/ui/card';
	import { ExternalLink, Code, BookOpen, CircleUser, Newspaper, Pencil, Trash2, GraduationCap, BookOpenText } from '@lucide/svelte';
	import type { Resource } from '../lib/api/queries';
	import { RESOURCE_TYPES } from '../lib/api/queries';

	interface Props {
		resource: Resource;
		showActions?: boolean;
		showUser?: boolean;
		userName?: string;
		onEdit?: (resource: Resource) => void;
		onDelete?: (resource: Resource) => void;
	}

	let { resource, showActions = false, showUser = true, userName, onEdit, onDelete }: Props = $props();

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
</script>

<Card class="bg-white border border-slate-900/12 rounded-2xl p-4 flex flex-col h-full">
	<CardContent class="pt-2.5 pb-0 px-0 flex flex-col flex-1 min-h-0">
		<div class="flex flex-col gap-[10px] h-full">
			<!-- Header with type badge and actions -->
			<div class="flex items-center justify-between shrink-0">
				<div class="bg-white border border-slate-900/15 rounded-full flex gap-2 h-7 items-center justify-center px-2">
					<svelte:component this={getResourceTypeIcon(resource)} class="w-5 h-5 text-black" />
					<span class="text-sm font-medium leading-[14px] text-black">
						{getResourceTypeName(resource)}
					</span>
				</div>
				{#if showActions}
					<div class="flex gap-2.5 items-center">
						<button 
							class="w-6 h-6 cursor-pointer"
							onclick={() => onEdit?.(resource)}
							aria-label="Edit resource"
						>
							<Pencil class="w-6 h-6 text-slate-900" />
						</button>
						<button 
							class="w-6 h-6 cursor-pointer"
							onclick={() => onDelete?.(resource)}
							aria-label="Delete resource"
						>
							<Trash2 class="w-6 h-6 text-slate-900" />
						</button>
					</div>
				{/if}
			</div>

			<!-- Title -->
			<h3 class="text-lg font-semibold leading-7 text-slate-900 shrink-0">
				{resource.title}
			</h3>

			<!-- Middle content area - grows to fill space -->
			<div class="flex flex-col gap-[10px] flex-1 min-h-0">
				<!-- Description and Link -->
				<div class="flex flex-col gap-[10px]">
					<p class="text-base font-normal leading-7 text-slate-900">
						{resource.description}
					</p>
					{#if resource.type === RESOURCE_TYPES.ARTICLE && resource.url}
						<a
							href={resource.url}
							target="_blank"
							rel="noopener noreferrer"
							class="flex gap-2 items-center text-base font-bold leading-7 text-slate-900 underline"
						>
							<ExternalLink class="w-5 h-5" />
							View article
						</a>
					{:else if (resource.type === RESOURCE_TYPES.BOOK || resource.type === RESOURCE_TYPES.COURSE) && 'author' in resource}
						<div class="flex gap-2 items-center">
							<BookOpenText class="w-5 h-5 text-slate-900" />
							<span class="text-base font-normal leading-7 text-slate-900">
								by {(resource as any).author || 'Unknown'}
							</span>
						</div>
					{/if}
				</div>
			</div>

			<!-- Tags - bottom aligned with space above -->
			{#if resource.tags && resource.tags.length > 0}
				<div class="flex flex-wrap gap-2.5 pt-1 pb-2 shrink-0">
					{#each resource.tags as tag}
						<span class="bg-white border border-slate-900/15 px-2 py-1 rounded-full text-xs font-medium leading-5 text-black h-[22px] flex items-center">
							{tag.name}
						</span>
					{/each}
				</div>
			{/if}

			<!-- Footer with user and date - fixed to bottom -->
			{#if showUser}
				<div class="shrink-0">
					<!-- Divider -->
					<div class="h-px bg-slate-200 w-full mb-[10px]"></div>
					<!-- Footer content -->
					<div class="flex items-center justify-between">
						<div class="flex gap-1 items-center">
							<CircleUser class="w-9 h-9 text-slate-900" />
							<span class="text-base font-normal leading-7 text-slate-900">
								{userName || 'You'}
							</span>
						</div>
						<span class="text-base font-normal leading-7 text-black/50 text-center">
							{formatDate(resource)}
						</span>
					</div>
				</div>
			{/if}
		</div>
	</CardContent>
</Card>

