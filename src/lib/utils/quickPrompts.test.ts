import { describe, expect, it } from 'vitest';
import { buildQuickPromptText, QUICK_PROMPTS } from './quickPrompts';

describe('quickPrompts', () => {
	it('prepends the prefix and keeps existing content on the next line', () => {
		expect(buildQuickPromptText('原内容', '请总结以下内容，并列出3个关键结论：')).toBe(
			'请总结以下内容，并列出3个关键结论：\n原内容'
		);
	});

	it('returns only the prefix when the current text is empty or blank', () => {
		expect(buildQuickPromptText('', '请将以下内容翻译成中文，保持原意和专业术语准确：')).toBe(
			'请将以下内容翻译成中文，保持原意和专业术语准确：'
		);
		expect(buildQuickPromptText('   ', '请优化以下内容的表达，使其更加清晰、简洁和专业：')).toBe(
			'请优化以下内容的表达，使其更加清晰、简洁和专业：'
		);
	});

	it('exposes the three required quick prompts', () => {
		expect(QUICK_PROMPTS.map((p) => p.label)).toEqual(['总结内容', '翻译为中文', '优化表达']);
	});
});
