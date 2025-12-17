<script lang="ts">
	import { BookMarked, LogOut } from '@lucide/svelte';
	import { createEventDispatcher } from 'svelte';
	import { goto } from '../lib/router';

	interface Props {
		isOpen?: boolean;
		onClose?: () => void;
	}

	let { isOpen = $bindable(false), onClose = () => {} }: Props = $props();

	const dispatch = createEventDispatcher();

	function handleSharedResources(event: MouseEvent) {
		event.stopPropagation();
		goto('/your-resources');
		isOpen = false;
		onClose();
	}

	function handleLogOut(event: MouseEvent) {
		event.stopPropagation();
		dispatch('logout');
		isOpen = false;
		onClose();
	}
</script>

{#if isOpen}
	<div
		class="absolute right-0 top-full mt-2 w-[224px] bg-white border border-[#f1f5f9] rounded-[6px] shadow-[0px_4px_6px_0px_rgba(0,0,0,0.09)] z-50 user-dropdown-container"
		role="menu"
		aria-orientation="vertical"
	>
		<!-- My Account -->
		<div class="p-[5px]">
			<div class="w-full flex items-center px-[8px] py-[6px]">
				<p class="flex-1 font-semibold text-[14px] leading-[20px] text-[#334155]">
					My Account
				</p>
			</div>
		</div>

		<!-- Divider -->
		<div class="h-px bg-[#f1f5f9] w-full"></div>

		<!-- Your Shared Resources -->
		<div class="p-[5px]">
			<button
				onclick={handleSharedResources}
				class="w-full flex items-center gap-[8px] px-[8px] py-[6px] text-left hover:bg-slate-50 transition-colors rounded"
				role="menuitem"
			>
				<BookMarked class="w-[10.667px] h-[10.667px] text-[#334155] shrink-0" />
				<p class="flex-1 font-medium text-[14px] leading-[20px] text-[#334155]">
					Your Shared Resources
				</p>
			</button>
		</div>

		<!-- Divider -->
		<div class="h-px bg-[#f1f5f9] w-full"></div>

		<!-- Log out -->
		<div class="p-[5px]">
			<button
				onclick={handleLogOut}
				class="w-full flex items-center gap-[8px] px-[8px] py-[6px] text-left hover:bg-slate-50 transition-colors rounded"
				role="menuitem"
			>
				<LogOut class="w-[10.667px] h-[10.667px] text-[#334155] shrink-0" />
				<p class="flex-1 font-medium text-[14px] leading-[20px] text-[#334155]">
					Log out
				</p>
			</button>
		</div>
	</div>
{/if}

