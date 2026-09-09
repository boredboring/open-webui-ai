import { existsSync, rmSync } from 'node:fs';

const cacheDir = 'node_modules/.vite';

if (existsSync(cacheDir)) {
	rmSync(cacheDir, { recursive: true, force: true });
	console.log('Removed Vite cache:', cacheDir);
} else {
	console.log('No Vite cache to clean:', cacheDir);
}
