"""Course corpus APIs for the 实训 AI 平台.

These endpoints expose the server-side Markdown corpus under
``<repo>/data/corpus`` to the frontend and import selected files into an
Open WebUI knowledge base using the same storage/vector pipeline as a normal
file upload.

Routes:
    GET  /api/v1/course/corpus/files
    POST /api/v1/course/corpus/import

The corpus root can be overridden with ``COURSE_CORPUS_DIR`` (for deployments
where the repository data directory is not co-located with the backend).
"""

from __future__ import annotations

import os
import re
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.datastructures import Headers

from open_webui.internal.db import get_async_session
from open_webui.models.files import Files
from open_webui.models.knowledge import Knowledges
from open_webui.routers.files import upload_file_handler
from open_webui.utils.auth import get_verified_user

router = APIRouter()

DEFAULT_CORPUS_DIR = Path(__file__).resolve().parents[3] / "data" / "corpus"
CORPUS_DIR = Path(os.getenv("COURSE_CORPUS_DIR") or DEFAULT_CORPUS_DIR).expanduser().resolve()


def _parse_frontmatter(path: Path) -> dict[str, Any]:
    """Read source_type/chapter/module from the Markdown YAML header."""
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as f:
            head = f.read(2048)
    except OSError:
        return {}
    if not head.startswith("---"):
        return {}
    meta: dict[str, Any] = {}
    for line in head.splitlines()[1:]:
        if line.startswith("---"):
            break
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip().lower()
        value = value.strip().strip("'\"")
        if key in {"source_type", "chapter", "module", "course"} and value and value != "-":
            meta[key] = value
    return meta


def _is_safe_corpus_path(rel_text: str) -> Path:
    """Resolve a client-supplied relative path and make sure it stays in corpus."""
    cleaned = rel_text.replace("\\", "/").strip()
    if not cleaned or cleaned.startswith("/") or re.match(r"^[A-Za-z]:", cleaned):
        raise HTTPException(status_code=400, detail=f"非法文件路径: {rel_text}")
    target = (CORPUS_DIR / cleaned).resolve()
    try:
        target.relative_to(CORPUS_DIR)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"文件路径超出语料目录: {rel_text}")
    return target


@router.get("/corpus/files")
async def get_corpus_files(user=Depends(get_verified_user)) -> dict[str, Any]:
    """Return the Markdown files available under the configured corpus root."""
    if not CORPUS_DIR.is_dir():
        return {
            "root": str(CORPUS_DIR),
            "exists": False,
            "total": 0,
            "items": [],
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    items: list[dict[str, Any]] = []
    for path in sorted(CORPUS_DIR.rglob("*.md")):
        if path.name == "README.md":
            continue
        rel = path.relative_to(CORPUS_DIR)
        parts = rel.parts
        directory = parts[0] if len(parts) > 1 else ""
        stat = path.stat()
        meta = _parse_frontmatter(path)
        items.append(
            {
                "path": rel.as_posix(),
                "filename": path.name,
                "directory": directory,
                "source_type": meta.get("source_type", ""),
                "chapter": meta.get("chapter", ""),
                "module": meta.get("module", ""),
                "size_bytes": stat.st_size,
                "modified_at": int(stat.st_mtime * 1000),
            }
        )

    return {
        "root": str(CORPUS_DIR),
        "exists": True,
        "total": len(items),
        "items": items,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


class CorpusImportForm(BaseModel):
    knowledge_id: str = Field(..., min_length=1)
    files: list[str] = Field(default_factory=list, max_length=500)


@router.post("/corpus/import")
async def import_corpus_files(
    request: Request,
    form_data: CorpusImportForm,
    user=Depends(get_verified_user),
    db: AsyncSession = Depends(get_async_session),
) -> dict[str, Any]:
    """Import selected corpus Markdown files into an existing knowledge base."""
    if not form_data.files:
        raise HTTPException(status_code=400, detail="请至少选择一个文件")

    knowledge = await Knowledges.get_knowledge_by_id(id=form_data.knowledge_id, db=db)
    if not knowledge:
        raise HTTPException(status_code=404, detail="知识库不存在")
    if user.role != "admin" and knowledge.user_id != user.id:
        raise HTTPException(status_code=403, detail="无权向该知识库导入文件")

    existing_files = await Knowledges.get_files_by_id(knowledge_id=form_data.knowledge_id, db=db)
    existing_names = {file.filename for file in existing_files}

    requested = []
    seen: set[str] = set()
    for rel_text in form_data.files:
        target = _is_safe_corpus_path(rel_text)
        if not target.is_file():
            raise HTTPException(status_code=404, detail=f"语料文件不存在: {rel_text}")
        posix = target.relative_to(CORPUS_DIR).as_posix()
        if posix in seen:
            continue
        seen.add(posix)
        requested.append((posix, target))

    imported: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    failed: list[dict[str, Any]] = []

    for posix, target in requested:
        if target.name in existing_names:
            skipped.append({"path": posix, "reason": "已在知识库中"})
            continue
        try:
            content = target.read_bytes()
            upload = UploadFile(
                file=BytesIO(content),
                filename=target.name,
                headers=Headers({"content-type": "text/markdown"}),
            )
            result = await upload_file_handler(
                request=request,
                file=upload,
                metadata={"knowledge_id": form_data.knowledge_id},
                process=True,
                process_in_background=False,
                user=user,
                db=db,
            )
            file_id = result.get("id") if isinstance(result, dict) else result.id

            # upload_file_handler can swallow processing errors and still return
            # {"status": True}; verify the durable file status and KB link here.
            db_file = await Files.get_file_by_id(id=file_id)
            linked = await Knowledges.has_file(
                knowledge_id=form_data.knowledge_id,
                file_id=file_id,
            )
            status = ((db_file.data or {}).get("status") if db_file and db_file.data else None)
            if status == "completed" and linked:
                imported.append({"path": posix})
            else:
                error = (
                    (db_file.data or {}).get("error")
                    if db_file and db_file.data
                    else "文件处理未完成或未关联知识库"
                )
                failed.append({"path": posix, "error": str(error or "处理状态未知")[:500]})
        except Exception as exc:
            detail = str(getattr(exc, "detail", "") or exc)
            failed.append({"path": posix, "error": detail[:500]})

    return {
        "knowledge_id": form_data.knowledge_id,
        "total": len(requested),
        "imported": imported,
        "skipped": skipped,
        "failed": failed,
    }
