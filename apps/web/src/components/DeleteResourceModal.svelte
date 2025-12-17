<script lang="ts">
	import { Button } from '$lib/components/ui/button';
	import { Loader2 } from '@lucide/svelte';
	import type { Resource } from '../lib/api/queries';

	interface Props {
		isOpen?: boolean;
		resource?: Resource | null;
		onClose?: () => void;
		onConfirm?: (resource: Resource) => void;
		isDeleting?: boolean;
	}

	let { isOpen = $bindable(false), resource = null, onClose = () => {}, onConfirm, isDeleting = false }: Props = $props();

	function handleCancel() {
		isOpen = false;
		onClose();
	}

	function handleConfirm() {
		if (resource && onConfirm) {
			onConfirm(resource);
			// Don't close the modal here - let the parent handle it after mutation succeeds
		}
	}
</script>

{#if isOpen}
	<!-- Backdrop -->
	<div 
		class="fixed inset-0 bg-black/30 z-50"
		onclick={handleCancel}
		role="button"
		tabindex="-1"
	></div>

	<!-- Modal -->
	<div class="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 bg-white border border-[#cbd5e1] rounded-[6px] shadow-[0px_4px_6px_0px_rgba(0,0,0,0.09)] z-50 p-6 flex flex-col gap-4 w-[464px]">
		<!-- Content -->
		<div class="flex flex-col gap-2">
			<h2 class="text-lg font-semibold leading-7 text-[#0f172a]">
				Are you sure you want to delete this resource?
			</h2>
			<p class="text-sm font-normal leading-5 text-[#64748b]">
				This action cannot be undone. This will permanently delete your resource and remove your data from our servers.
			</p>
		</div>

		<!-- Buttons -->
		<div class="flex gap-2 justify-end">
			<Button
				type="button"
				onclick={handleCancel}
				class="h-auto rounded-md border border-[#e2e8f0] bg-white hover:bg-slate-50 font-medium text-sm leading-6 px-4 py-2 text-[#0f172a]"
			>
				Cancel
			</Button>
			<Button
				type="button"
				onclick={handleConfirm}
				disabled={isDeleting}
				class="h-auto rounded-md bg-[#0f172a] hover:bg-[#0f172a]/90 font-medium text-sm leading-6 px-4 py-2 text-white disabled:opacity-50 disabled:cursor-not-allowed"
			>
				{#if isDeleting}
					<Loader2 class="mr-2 h-4 w-4 animate-spin inline" />
					Deleting...
				{:else}
					Continue
				{/if}
			</Button>
		</div>
	</div>
{/if}

