<script lang="ts">
	import { Card } from '$lib/components/ui/card';
	import { createQuery } from '@tanstack/svelte-query';
	import { tagQueries, RESOURCE_TYPES } from '../lib/api/queries';

	interface Props {
		selectedTypes: Set<string>;
		selectedTags: Set<string>;
		onTypeToggle: (type: string) => void;
		onTagToggle: (tagId: string) => void;
	}

	let { selectedTypes, selectedTags, onTypeToggle, onTagToggle }: Props = $props();

	const tagsQuery = createQuery(() => tagQueries.all());
</script>

<Card class="bg-white border border-slate-900/12 rounded-2xl p-4 h-[680px]">
	<div class="flex flex-col gap-[10px]">
		<h3 class="text-lg font-semibold leading-7 text-slate-900">Filters</h3>
		
		<!-- Resource Type Filters -->
		<div class="flex flex-col gap-[10px]">
			<p class="text-base font-normal leading-7 text-slate-900">Resource Type</p>
			<label class="flex gap-2 items-start cursor-pointer">
				<input
					type="checkbox"
					checked={selectedTypes.has(RESOURCE_TYPES.ARTICLE)}
					onchange={() => onTypeToggle(RESOURCE_TYPES.ARTICLE)}
					class="w-[14px] h-[14px] rounded border border-gray-300 mt-0.5 checked:bg-slate-900 checked:border-slate-900 accent-slate-900"
				/>
				<span class="text-sm font-medium leading-[14px] text-black">Articles</span>
			</label>
			<label class="flex gap-2 items-start cursor-pointer">
				<input
					type="checkbox"
					checked={selectedTypes.has(RESOURCE_TYPES.CODE_SNIPPET)}
					onchange={() => onTypeToggle(RESOURCE_TYPES.CODE_SNIPPET)}
					class="w-[14px] h-[14px] rounded border border-gray-300 mt-0.5 checked:bg-slate-900 checked:border-slate-900 accent-slate-900"
				/>
				<span class="text-sm font-medium leading-[14px] text-black">Code Snippets</span>
			</label>
			<label class="flex gap-2 items-start cursor-pointer">
				<input
					type="checkbox"
					checked={selectedTypes.has('learning_resource')}
					onchange={() => onTypeToggle('learning_resource')}
					class="w-[14px] h-[14px] rounded border border-gray-300 mt-0.5 checked:bg-slate-900 checked:border-slate-900 accent-slate-900"
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
							onclick={() => onTagToggle(tagId)}
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

