import { beforeEach, describe, expect, it, vi } from 'vitest';

vi.mock('$lib/constants', () => ({
	WEBUI_API_BASE_URL: '/api/v1'
}));

import { getHelpDocumentation } from './index';

describe('getHelpDocumentation', () => {
	beforeEach(() => {
		vi.unstubAllGlobals();
	});

	it('fetches the help document from /api/v1/help', async () => {
		const fetchMock = vi.fn().mockResolvedValue({
			ok: true,
			json: async () => ({ title: 'Help', content: '# Help\n\nContent' })
		});
		vi.stubGlobal('fetch', fetchMock);

		const result = await getHelpDocumentation();

		expect(fetchMock).toHaveBeenCalledWith('/api/v1/help/', {
			method: 'GET',
			headers: { 'Content-Type': 'application/json' }
		});
		expect(result).toEqual({ title: 'Help', content: '# Help\n\nContent' });
	});

	it('rejects when the request is not ok', async () => {
		vi.stubGlobal(
			'fetch',
			vi.fn().mockResolvedValue({
				ok: false,
				json: async () => ({ detail: 'not found' })
			})
		);

		await expect(getHelpDocumentation()).rejects.toEqual({ detail: 'not found' });
	});
});
