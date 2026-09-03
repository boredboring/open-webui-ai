from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient

from open_webui.routers import course
from open_webui.routers.course import (
    DEFAULT_CORPUS_DIR,
    _is_safe_corpus_path,
    _parse_frontmatter,
    router,
)
from open_webui.utils.auth import get_verified_user


def test_default_corpus_dir_points_to_repo_data_corpus():
    assert DEFAULT_CORPUS_DIR.name == "corpus"
    assert DEFAULT_CORPUS_DIR.parent.name == "data"
    assert DEFAULT_CORPUS_DIR.exists()


def make_client(user=None) -> TestClient:
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_verified_user] = lambda: user or SimpleNamespace(role="user")
    return TestClient(app)


def test_parse_frontmatter_reads_course_fields(tmp_path):
    md = tmp_path / "sample.md"
    md.write_text(
        """---
source_type: 课件
course: 数据结构
chapter: 第一章 绪论
module: 1.1_数据结构的基本概念
---
# Title
""",
        encoding="utf-8",
    )
    meta = _parse_frontmatter(md)
    assert meta["source_type"] == "课件"
    assert meta["chapter"] == "第一章 绪论"
    assert meta["module"] == "1.1_数据结构的基本概念"


def test_corpus_file_listing_groups_markdown_by_directory(tmp_path, monkeypatch):
    monkeypatch.setattr(course, "CORPUS_DIR", tmp_path)
    (tmp_path / "01_绪论").mkdir()
    (tmp_path / "01_绪论" / "1.1_数据结构的基本概念.md").write_text(
        "---\nsource_type: 课件\nchapter: 第一章 绪论\n---\n# 内容\n", encoding="utf-8"
    )
    (tmp_path / "README.md").write_text("# readme\n", encoding="utf-8")

    client = make_client(user=SimpleNamespace(role="admin"))
    response = client.get("/corpus/files")
    assert response.status_code == 200
    data = response.json()
    assert data["exists"] is True
    assert data["total"] == 1
    assert data["items"][0]["path"] == "01_绪论/1.1_数据结构的基本概念.md"
    assert data["items"][0]["directory"] == "01_绪论"
    assert data["items"][0]["source_type"] == "课件"


def test_verified_user_can_list_corpus(tmp_path, monkeypatch):
    monkeypatch.setattr(course, "CORPUS_DIR", tmp_path)
    client = make_client(user=SimpleNamespace(role="user"))
    response = client.get("/corpus/files")
    assert response.status_code == 200
    assert response.json()["total"] == 0


def test_safe_corpus_path_rejects_traversal(tmp_path, monkeypatch):
    monkeypatch.setattr(course, "CORPUS_DIR", tmp_path)
    (tmp_path / "01_绪论").mkdir()
    safe = _is_safe_corpus_path("01_绪论/1.1.md")
    assert safe == (tmp_path / "01_绪论" / "1.1.md").resolve()

    for bad in ["../secret.md", "/etc/passwd", "..\\secret.md", "C:/Windows/win.ini"]:
        try:
            _is_safe_corpus_path(bad)
        except Exception:
            continue
        raise AssertionError(f"traversal should be rejected: {bad}")
