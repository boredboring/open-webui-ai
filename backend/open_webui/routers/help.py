from __future__ import annotations

import pkgutil
from pathlib import Path

from fastapi import APIRouter, HTTPException, status

router = APIRouter()

HELP_DOCUMENT_FILENAME = 'help.md'
HELP_DOCUMENT_TITLE_FALLBACK = 'System Help'


def load_help_documentation() -> str:
    content = pkgutil.get_data('open_webui', HELP_DOCUMENT_FILENAME)
    if content is None:
        path = Path(__file__).resolve().parent.parent / HELP_DOCUMENT_FILENAME
        content = path.read_bytes()
    return content.decode('utf-8')


def extract_title(content: str) -> str:
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith('# '):
            return stripped[2:].strip()
    return HELP_DOCUMENT_TITLE_FALLBACK


@router.get('/')
async def get_help_documentation():
    try:
        content = load_help_documentation()
    except Exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Help documentation not found')

    return {'title': extract_title(content), 'content': content}
