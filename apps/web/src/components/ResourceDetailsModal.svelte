<script lang="ts">
	import { X, Code, Newspaper, BookOpenText, GraduationCap, ExternalLink, Copy, Check } from '@lucide/svelte';
	import { Button } from '$lib/components/ui/button';
	import type { Resource } from '../lib/api/queries';
	import { RESOURCE_TYPES } from '../lib/api/queries';
	import CodeEditor from './CodeEditor.svelte';

	interface Props {
		isOpen?: boolean;
		resource: Resource | null;
		onClose?: () => void;
	}

	let { isOpen = $bindable(false), resource, onClose = () => {} }: Props = $props();
	let copied = $state(false);

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
		return BookOpenText;
	}

	// Format date helper (reuse from Dashboard)
	function formatDateHelper(resource: Resource): string {
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

	// Get user name
	function getUserName(resource: Resource): string {
		if (resource.user?.first_name && resource.user?.last_name) {
			return `${resource.user.first_name} ${resource.user.last_name}`;
		}
		return resource.user?.first_name || 'Unknown';
	}

	// Copy code to clipboard
	async function handleCopyCode() {
		if (resource && 'code' in resource && resource.code) {
			try {
				await navigator.clipboard.writeText(resource.code);
				copied = true;
				setTimeout(() => {
					copied = false;
				}, 2000);
			} catch (err) {
				console.error('Failed to copy code:', err);
			}
		}
	}

	function handleClose() {
		isOpen = false;
		onClose();
	}
</script>

{#if isOpen && resource}
	<!-- Backdrop -->
	<div 
		class="fixed inset-0 z-40"
		onclick={handleClose}
		role="button"
		tabindex="-1"
	></div>

	<!-- Modal -->
	<div class="fixed right-[52px] top-[117px] w-[518px] h-[888px] bg-white border border-slate-100 rounded-md shadow-lg z-50 flex flex-col p-4 gap-4 overflow-hidden">
		<!-- Header -->
		<div class="flex items-center justify-between shrink-0">
			<div class="bg-white border border-slate-900/15 flex gap-2 h-7 items-center justify-center px-2 rounded-full">
				<svelte:component this={getResourceTypeIcon(resource)} class="w-5 h-5 text-black" />
				<span class="text-sm font-medium leading-[14px] text-black">
					{getResourceTypeName(resource)}
				</span>
			</div>
			<button
				onclick={handleClose}
				class="w-6 h-6 flex items-center justify-center cursor-pointer hover:bg-slate-100 rounded"
				aria-label="Close"
			>
				<X class="w-6 h-6 text-slate-900" />
			</button>
		</div>

		<!-- Title -->
		<h2 class="text-lg font-semibold leading-7 text-slate-900 shrink-0">
			{resource.title}
		</h2>

		<!-- Description -->
		<p class="text-base font-normal leading-7 text-slate-900 shrink-0">
			{resource.description}
		</p>

		<!-- Link (for articles) -->
		{#if resource.type === RESOURCE_TYPES.ARTICLE && 'url' in resource && resource.url}
			<a
				href={resource.url}
				target="_blank"
				rel="noopener noreferrer"
				class="flex gap-2 items-center text-base font-bold leading-7 text-slate-900 underline shrink-0"
			>
				<ExternalLink class="w-5 h-5" />
				View article
			</a>
		{/if}

		<!-- Author (for Book and Course) -->
		{#if (resource.type === RESOURCE_TYPES.BOOK || resource.type === RESOURCE_TYPES.COURSE) && 'author' in resource && resource.author}
			<div class="flex gap-2 items-center shrink-0">
				<BookOpenText class="w-5 h-5 text-slate-900" />
				<span class="text-base font-normal leading-7 text-slate-900">
					by {resource.author}
				</span>
			</div>
		{/if}

		<!-- Tags -->
		{#if resource.tags && resource.tags.length > 0}
			<div class="flex flex-wrap gap-2.5 shrink-0">
				{#each resource.tags as tag}
					<span class="bg-white border border-slate-900/15 px-2 py-1 rounded-full text-xs font-medium leading-5 text-black h-[22px] flex items-center">
						{tag.name}
					</span>
				{/each}
			</div>
		{/if}

		<!-- Code Block (only for code snippets) -->
		{#if resource.type === RESOURCE_TYPES.CODE_SNIPPET && 'code' in resource && resource.code}
			<div class="bg-black rounded-[10px] flex-1 min-h-0 overflow-hidden">
				<CodeEditor
					code={resource.code}
					language="auto"
					theme="dark"
					readOnly={true}
				/>
			</div>
		{:else}
			<!-- Spacer for non-code resources -->
			<div class="flex-1"></div>
		{/if}

		<!-- Copy Code Button (only for code snippets) -->
		{#if resource.type === RESOURCE_TYPES.CODE_SNIPPET && 'code' in resource && resource.code}
			<Button
				type="button"
				onclick={handleCopyCode}
				class="w-full h-auto rounded-md bg-slate-900 hover:bg-slate-900/90 font-medium text-sm leading-6 px-4 py-2 text-white shrink-0 flex items-center justify-center gap-2"
			>
				{#if copied}
					<Check class="w-4 h-4" />
					<span>Copied!</span>
				{:else}
					<Copy class="w-4 h-4" />
					<span>Copy Code Snippet</span>
				{/if}
			</Button>
		{/if}
	</div>
{/if}

