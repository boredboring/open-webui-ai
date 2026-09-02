import { WEBUI_API_BASE_URL } from '$lib/constants';

export const getHelpDocumentation = async () => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/help/`, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json'
		}
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.error(err);
			error = err;
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};
