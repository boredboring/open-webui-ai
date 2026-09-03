import { WEBUI_API_BASE_URL } from '$lib/constants';

export const getCorpusFiles = async (token: string) => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/course/corpus/files`, {
		method: 'GET',
		headers: {
			Accept: 'application/json',
			authorization: `Bearer ${token}`
		}
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			error = err.detail || err.message || err;
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const importCorpusFiles = async (token: string, knowledgeId: string, files: string[]) => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/course/corpus/import`, {
		method: 'POST',
		headers: {
			Accept: 'application/json',
			'Content-Type': 'application/json',
			authorization: `Bearer ${token}`
		},
		body: JSON.stringify({
			knowledge_id: knowledgeId,
			files
		})
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			error = err.detail || err.message || err;
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};
