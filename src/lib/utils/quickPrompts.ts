export type QuickPrompt = {
	id: string;
	label: string;
	prompt: string;
};

export const QUICK_PROMPTS: QuickPrompt[] = [
	{ id: 'summarize', label: '总结内容', prompt: '请总结以下内容，并列出3个关键结论：' },
	{
		id: 'translate',
		label: '翻译为中文',
		prompt: '请将以下内容翻译成中文，保持原意和专业术语准确：'
	},
	{ id: 'polish', label: '优化表达', prompt: '请优化以下内容的表达，使其更加清晰、简洁和专业：' }
];

export const buildQuickPromptText = (current: string, prefix: string): string =>
	current && current.trim() !== '' ? `${prefix}\n${current}` : prefix;
