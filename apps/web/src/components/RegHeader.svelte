<script lang="ts">
	import { BookMarked } from "@lucide/svelte";
	
	export let title = "Welcome Back";
	export let subtitle = "Share and discover valuable learning resources";
</script>

<style>
	:global(.icon-white svg) {
		stroke: white !important;
		fill: none !important;
	}
</style>

<div class="flex flex-col items-center mb-8">
	<div class="relative flex items-center justify-center mb-[13px]">
		<div class="w-[66px] h-[66px] rounded-full bg-slate-900 flex items-center justify-center icon-white">
			<BookMarked class="w-[37px] h-[37px]" stroke-width="2" />
		</div>
	</div>
	<h2 class="text-3xl font-semibold leading-9 tracking-[-0.225px] text-slate-900 text-center mb-2">
		{title}
	</h2>
	<h4 class="text-xl font-normal leading-7 tracking-[-0.1px] text-slate-900 text-center">
		{subtitle}
	</h4>
</div>

