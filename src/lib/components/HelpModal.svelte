<script lang="ts">
	import DOMPurify from 'dompurify';
	import { marked } from 'marked';
	import { getContext } from 'svelte';

	import { getHelpDocumentation } from '$lib/apis/help';

	import Modal from './common/Modal.svelte';
	import XMark from '$lib/components/icons/XMark.svelte';

	const i18n = getContext('i18n');

	export let show = false;

	type HelpDocument = {
		title: string;
		content: string;
	};

	let helpDocument: HelpDocument | null = null;
	let error = false;

	const init = async () => {
		if (helpDocument || error) {
			return;
		}

		helpDocument = await getHelpDocumentation().catch(() => {
			error = true;
			return null;
		});
	};

	$: if (show) {
		init();
	}
</script>

<Modal
	bind:show
	size="lg"
	className="bg-white dark:bg-gray-900 rounded-3xl overflow-hidden"
	containerClassName="p-3"
>
	<div class="flex max-h-[70vh] flex-col">
		<div
			class="flex shrink-0 items-start justify-between gap-4 px-4 pb-2.5 pt-3.5 dark:text-white text-black"
		>
			<div class="min-w-0">
				<h2 class="m-0 truncate text-base font-normal">
					{helpDocument?.title ?? $i18n.t('Help')}
				</h2>
			</div>

			<button
				class="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl text-gray-400 transition hover:bg-gray-100 hover:text-gray-700 dark:text-gray-500 dark:hover:bg-white/10 dark:hover:text-gray-200"
				on:click={() => (show = false)}
				aria-label={$i18n.t('Close')}
			>
				<XMark className={'size-4'} />
			</button>
		</div>

		<div
			class="min-h-0 flex-1 overflow-y-auto px-4 py-2 text-gray-700 scrollbar-hidden dark:text-gray-100"
		>
			{#if helpDocument}
				<div class="markdown-prose max-w-none">
					<!-- eslint-disable-next-line svelte/no-at-html-tags -->
					{@html DOMPurify.sanitize(marked.parse(helpDocument.content, { async: false }) as string)}
				</div>
			{:else if error}
				<div class="flex flex-col items-center justify-center gap-3 py-16 text-center">
					<p class="text-sm text-gray-500 dark:text-gray-400">{$i18n.t('Error')}</p>
					<button
						on:click={() => {
							error = false;
							init();
						}}
						class="text-sm font-normal text-gray-700 transition hover:text-black dark:text-gray-300 dark:hover:text-white"
					>
						{$i18n.t('Retry')}
					</button>
				</div>
			{:else}
				<div class="flex items-center justify-center py-16 text-sm text-gray-400 dark:text-gray-500">
					{$i18n.t('Loading...')}
				</div>
			{/if}
		</div>
	</div>
</Modal>
