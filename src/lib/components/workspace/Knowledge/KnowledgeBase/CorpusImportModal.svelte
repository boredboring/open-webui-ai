<script lang="ts">
	import { toast } from 'svelte-sonner';
	import { createEventDispatcher, onDestroy } from 'svelte';

	import { getCorpusFiles, importCorpusFiles } from '$lib/apis/course';
	import { searchKnowledgeFilesById } from '$lib/apis/knowledge';
	import Modal from '$lib/components/common/Modal.svelte';
	import Spinner from '$lib/components/common/Spinner.svelte';
	import Checkbox from '$lib/components/common/Checkbox.svelte';
	import XMark from '$lib/components/icons/XMark.svelte';

	const dispatch = createEventDispatcher();

	export let show = false;
	export let knowledgeId: string = '';
	export let knowledgeName = '';

	let loading = false;
	let importing = false;
	let error = '';

	let items: any[] = [];
	let existingNames = new Set<string>();
	let selected = new Set<string>();

	const load = async () => {
		if (!knowledgeId) return;

		loading = true;
		error = '';
		items = [];
		existingNames = new Set();
		selected = new Set();

		try {
			const [corpusResult, kbResult] = await Promise.all([
				getCorpusFiles(localStorage.token),
				searchKnowledgeFilesById(localStorage.token, knowledgeId).catch(() => null)
			]);

			items = corpusResult?.items ?? [];
			const existing = (kbResult?.items ?? []) as Array<{ filename: string }>;
			existingNames = new Set(existing.map((item) => item.filename));
		} catch (err) {
			error = `${err}`;
		}

		loading = false;
	};

	$: if (show) {
		load();
	}

	const groups = () => {
		const dirs = [...new Set(items.map((item) => item.directory || '未分类'))];
		return dirs.map((dir) => ({
			dir,
			files: items.filter((item) => (item.directory || '未分类') === dir)
		}));
	};

	const toggleFile = (path: string, checked: boolean) => {
		const next = new Set(selected);
		if (checked) {
			next.add(path);
		} else {
			next.delete(path);
		}
		selected = next;
	};

	const toggleGroup = (dir: string, files: any[], checked: boolean) => {
		const next = new Set(selected);
		for (const file of files) {
			if (existingNames.has(file.filename)) continue;
			if (checked) {
				next.add(file.path);
			} else {
				next.delete(file.path);
			}
		}
		selected = next;
	};

	const selectableCount = () => items.filter((item) => !existingNames.has(item.filename)).length;

	const importSelected = async () => {
		if (selected.size === 0) return;
		if (!knowledgeId) {
			toast.error('知识库 ID 为空，无法导入');
			return;
		}
		importing = true;
		try {
			const result = await importCorpusFiles(localStorage.token, knowledgeId, [...selected]);
			const importedCount = result?.imported?.length ?? 0;
			const skippedCount = result?.skipped?.length ?? 0;
			const failedCount = result?.failed?.length ?? 0;
			toast.success(`导入完成：成功 ${importedCount} 个，跳过 ${skippedCount} 个`);
			if (failedCount > 0) {
				toast.error(`导入失败 ${failedCount} 个，请在控制台查看明细`);
			}
			dispatch('imported', result);
			show = false;
		} catch (err) {
			toast.error(`${err}`);
		}
		importing = false;
	};

	onDestroy(() => {
		items = [];
		selected = new Set();
	});
</script>

<Modal size="xl" bind:show>
	<div class="flex h-full max-h-[80vh] flex-col dark:text-gray-200">
		<div
			class="flex shrink-0 items-center justify-between border-b border-gray-100 px-5 py-4 dark:border-gray-800"
		>
			<div>
				<div class="text-base font-medium">从课程语料导入</div>
				<div class="mt-0.5 text-xs text-gray-500">
					服务器 data/corpus → {knowledgeName || knowledgeId}
				</div>
			</div>
			<button
				class="rounded-lg p-1.5 text-gray-500 transition hover:bg-gray-100 dark:hover:bg-gray-800"
				on:click={() => {
					show = false;
				}}
				aria-label="关闭"
			>
				<XMark className="size-4" />
			</button>
		</div>

		{#if error}
			<div class="px-5 py-4 text-sm text-red-500">{error}</div>
		{:else if loading}
			<div class="flex flex-1 items-center justify-center gap-2 py-16 text-sm text-gray-500">
				<Spinner className="size-4" />
				正在读取服务器语料…
			</div>
		{:else if items.length === 0}
			<div class="flex flex-1 items-center justify-center py-16 text-sm text-gray-500">
				data/corpus 下暂无可导入的 Markdown 文件
			</div>
		{:else}
			<div class="flex-1 overflow-y-auto px-5 py-4">
				{#each groups() as { dir, files } (dir)}
					<div class="mb-4">
						<div class="mb-1.5 flex items-center gap-2">
							<Checkbox
								state={files.every(
									(file) => selected.has(file.path) || existingNames.has(file.filename)
								)
									? 'checked'
									: 'unchecked'}
								on:change={(e) => {
									toggleGroup(dir, files, e.detail === 'checked');
								}}
							/>
							<div class="text-sm font-medium">{dir}</div>
							<div class="text-xs text-gray-400">
								{files.length} 个文件
							</div>
						</div>
						<div class="grid grid-cols-1 gap-1 rounded-xl bg-gray-50 p-2 dark:bg-gray-900">
							{#each files as file (file.path)}
								{@const added = existingNames.has(file.filename)}
								<div
									class="flex items-center gap-2 rounded-lg px-2 py-1.5 text-xs {added
										? 'opacity-45'
										: 'hover:bg-gray-100 dark:hover:bg-gray-800'}"
								>
									<Checkbox
										disabled={added}
										state={added || selected.has(file.path) ? 'checked' : 'unchecked'}
										on:change={(e) => {
											toggleFile(file.path, e.detail === 'checked');
										}}
									/>
									<div class="min-w-0 flex-1 truncate">
										<span class="font-medium">{file.filename}</span>
										{#if file.chapter}
											<span class="ml-2 text-gray-400">{file.chapter}</span>
										{/if}
									</div>
									{#if added}
										<span class="shrink-0 text-green-600 dark:text-green-400">已导入</span>
									{:else}
										<span class="shrink-0 text-gray-400">
											{(file.size_bytes / 1024).toFixed(1)} KB
										</span>
									{/if}
								</div>
							{/each}
						</div>
					</div>
				{/each}
			</div>
		{/if}

		<div
			class="flex shrink-0 items-center justify-between border-t border-gray-100 px-5 py-3 dark:border-gray-800"
		>
			<div class="text-xs text-gray-500">
				已选择 {selected.size} / {selectableCount()} 个文件
			</div>
			<div class="flex items-center gap-2">
				{#if selectableCount() > 0}
					<button
						class="rounded-xl px-3 py-1.5 text-xs text-gray-600 transition hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800"
						on:click={() => {
							const next = new Set(selected);
							for (const file of items) {
								if (!existingNames.has(file.filename)) next.add(file.path);
							}
							selected = next;
						}}
					>
						全选
					</button>
					<button
						class="rounded-xl px-3 py-1.5 text-xs text-gray-600 transition hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800"
						on:click={() => {
							selected = new Set();
						}}
					>
						清空
					</button>
				{/if}
				<button
					class="flex items-center gap-2 rounded-xl bg-black px-4 py-1.5 text-xs text-white transition enabled:hover:opacity-80 disabled:opacity-40 dark:bg-white dark:text-black"
					disabled={selected.size === 0 || importing}
					on:click={importSelected}
				>
					{#if importing}
						<Spinner className="size-3.5" />
						正在导入并向量化…
					{:else}
						导入到知识库
					{/if}
				</button>
			</div>
		</div>
	</div>
</Modal>
