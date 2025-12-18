<script lang="ts">
	import { Check } from '@lucide/svelte';
	import { Button } from '$lib/components/ui/button';
	import { goto } from '../lib/router';

	interface Props {
		isOpen?: boolean;
		message: string;
		actionLabel?: string;
		actionUrl?: string;
		onClose?: () => void;
	}

	let { isOpen = $bindable(false), message, actionLabel, actionUrl, onClose = () => {} }: Props = $props();

	function handleAction() {
		if (actionUrl) {
			goto(actionUrl);
		}
		isOpen = false;
		onClose();
	}

	function handleClose() {
		isOpen = false;
		onClose();
	}

	$effect(() => {
		if (isOpen) {
			const timer = setTimeout(() => {
				handleClose();
			}, 7000);
			return () => clearTimeout(timer);
		}
	});
</script>

{#if isOpen}
	<!-- Banner -->
	<div class="fixed left-0 right-0 top-[140px] z-50 flex justify-center">
		<div class="max-w-[1440px] w-full mx-auto px-[52px]">
			<div class="bg-white border border-[#cbd5e1] rounded-[6px] p-6 flex items-center justify-between gap-4">
				<div class="flex gap-2 items-center">
					<Check class="w-9 h-9 text-[#0f172a] shrink-0" />
					<p class="text-lg font-semibold leading-7 text-[#0f172a]">
						{message}
					</p>
				</div>
				{#if actionLabel && actionUrl}
					<Button
						type="button"
						onclick={handleAction}
						class="h-auto rounded-md bg-[#0f172a] hover:bg-[#0f172a]/90 font-medium text-sm leading-6 px-4 py-2 text-white shrink-0"
					>
						{actionLabel}
					</Button>
				{/if}
			</div>
		</div>
	</div>
{/if}

