#!/usr/bin/env python3
"""Build a Markdown course corpus from the raw PDFs under data/.

Directory layout produced:

    data/corpus/
    ├── README.md
    ├── manifest.csv
    ├── 01_绪论/ ... 08_排序/
    ├── 90_习题代码/
    └── 91_试卷/

Each converted PDF keeps its own module-level Markdown file so that Open WebUI
can retrieve and cite by chapter/module, and Markdown heading-based chunking
stays predictable.

Usage (run with the conda env that has pypdf installed):
    python scripts/build_corpus.py
"""

from __future__ import annotations

import csv
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path

from pypdf import PdfReader

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data"
OUT_DIR = DATA_DIR / "corpus"
MANIFEST_PATH = OUT_DIR / "manifest.csv"

CN_NUM = {
    "一": 1,
    "二": 2,
    "三": 3,
    "四": 4,
    "五": 5,
    "六": 6,
    "七": 7,
    "八": 8,
    "九": 9,
    "十": 10,
}

CHAPTER_DIR_RE = re.compile(r"^第([一二三四五六七八九十]+)章\s*(.*)$")
NOISE_REPLACEMENTS = [
    ("【公众号：研料库，料最全】", ""),
    ("【公众号:研料库,料最全】", ""),
    ("王道考研/CSKAOYAN.COM", ""),
    ("王道考研/CSKAOYAN.com", ""),
    ("WWW.CSKAOYAN.COM", ""),
    ("www.cskaoyan.com", ""),
    ("CSKAOYAN.COM", ""),
    ("研料库，料最全", ""),
    ("研料库", ""),
    ("b站：我头发还多还能学", ""),
]


def chapter_info(dir_name: str) -> tuple[int, str] | None:
    """Return (chapter_number, chapter_title) for names like '第一章 绪论'."""
    m = CHAPTER_DIR_RE.match(dir_name.strip())
    if not m:
        return None
    chinese_num = m.group(1)
    number = 0
    if chinese_num == "十":
        number = 10
    elif "十" in chinese_num:
        parts = chinese_num.split("十")
        number = CN_NUM.get(parts[0], 0) * 10
        if parts[1]:
            number += CN_NUM.get(parts[1], 0)
    else:
        number = CN_NUM.get(chinese_num, 0)
    return number, m.group(2).strip() or dir_name.strip()


def sanitize_stem(stem: str) -> str:
    """Clean a PDF file name into a readable module name."""
    name = unicodedata.normalize("NFKC", stem)
    for old, new in NOISE_REPLACEMENTS:
        name = name.replace(old, new)
    name = re.sub(r"[（(]\s*学员版\s*[)）]", "", name)
    name = re.sub(r"\s+", " ", name).strip(" _-")
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", name)
    return name


def sanitize_markdown_path(name: str) -> str:
    return re.sub(r"[^\w\u4e00-\u9fff.\-+~]+", "_", name, flags=re.UNICODE)


def clean_page_text(raw: str) -> str:
    """Normalize and remove repeated course-watermark noise."""
    text = unicodedata.normalize("NFKC", raw)
    for old, new in NOISE_REPLACEMENTS:
        text = text.replace(old, new)
    lines: list[str] = []
    for line in text.splitlines():
        line = line.replace("\u3000", " ").strip()
        if not line:
            lines.append("")
            continue
        line = re.sub(r"[ \t]+", " ", line)
        # Drop leftover watermark-like standalone lines.
        stripped = line.strip(" 　·-—*")
        if re.fullmatch(r"(王道考研|WWW\.CSKAOYAN\.COM|CSKAOYAN\.COM|研料库|b站[:：]?我头发还多还能学)", stripped, re.I):
            continue
        lines.append(line)
    # Collapse repeated blank lines and repeated identical lines.
    out: list[str] = []
    for line in lines:
        if not line:
            if out and out[-1] != "":
                out.append("")
        elif not out or out[-1] != line:
            out.append(line)
    return "\n".join(out).strip()


def extract_pdf(pdf: Path) -> tuple[list[str], int]:
    """Return cleaned per-page text and page count."""
    reader = PdfReader(str(pdf))
    texts: list[str] = []
    for page in reader.pages:
        raw = page.extract_text() or ""
        texts.append(clean_page_text(raw))
    return texts, len(reader.pages)


def classify(pdf: Path) -> tuple[str, str | None, str]:
    """Return (source_type, chapter_name_or_None, output_dir_name)."""
    rel = pdf.relative_to(DATA_DIR)
    parts = list(rel.parts)
    if parts[0] == "PPT":
        if len(parts) == 2:
            return "试卷", None, "91_试卷"
        chapter = parts[1]
        info = chapter_info(chapter)
        if info is None:
            return "课件", None, "99_其他课件"
        num, title = info
        return "课件", chapter, f"{num:02d}_{title}"
    if parts[0] == "习题":
        return "习题代码", None, "90_习题代码"
    if parts[0] == "参考书籍":
        return "参考教材", None, "99_参考教材"
    return "其他", None, "99_其他"


def render_markdown(
    pdf: Path,
    title: str,
    source_type: str,
    chapter_name: str | None,
    page_texts: list[str],
) -> str:
    rel = pdf.relative_to(REPO_ROOT)
    heading = title
    if chapter_name:
        heading = f"{chapter_name} · {title}"
    lines = [
        "---",
        f"source_type: {source_type}",
        "course: 数据结构",
        f"chapter: {chapter_name or '-'}",
        f"module: {title}",
        f"source: {rel.as_posix()}",
        f"pages: {len(page_texts)}",
        f"generated: {date.today().isoformat()}",
        "---",
        "",
        f"# {heading}",
        "",
        f"> 类型：{source_type}｜课程：数据结构｜共 {len(page_texts)} 页",
        f"> 原始文件：`{rel.as_posix()}`",
        "> 说明：本文件由 PDF 文字层自动提取生成，公式、图形与代码排版可能失真，关键内容请以原始 PDF 为准。",
        "",
    ]
    for i, text in enumerate(page_texts, start=1):
        if not text:
            continue
        lines.append(f"## 第 {i} 页")
        lines.append("")
        lines.append(text)
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def build() -> None:
    if not DATA_DIR.exists():
        sys.exit(f"data dir not found: {DATA_DIR}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, str]] = []
    skipped: list[str] = []
    generated: list[Path] = []
    chapter_counts: dict[str, int] = {}

    pdfs = sorted(DATA_DIR.rglob("*.pdf"))
    for pdf in pdfs:
        rel = pdf.relative_to(DATA_DIR)
        if rel.parts[0] == "corpus":
            continue
        source_type, chapter_name, out_dir_name = classify(pdf)
        stem = sanitize_stem(pdf.stem)
        title = stem
        if not title:
            title = pdf.name.removesuffix(".pdf")

        try:
            page_texts, page_count = extract_pdf(pdf)
        except Exception as exc:  # keep going; record the failure
            rows.append(
                {
                    "source": pdf.relative_to(REPO_ROOT).as_posix(),
                    "type": source_type,
                    "chapter": chapter_name or "",
                    "module": title,
                    "target": "",
                    "pages": "",
                    "text_pages": "",
                    "empty_pages": "",
                    "chars": "",
                    "status": f"failed: {exc.__class__.__name__}: {exc}",
                }
            )
            skipped.append(f"{rel.as_posix()} -> FAILED")
            continue

        if source_type == "参考教材" and sum(len(t) for t in page_texts) < 200:
            # Scanned book without usable text layer: do not emit an empty doc.
            rows.append(
                {
                    "source": pdf.relative_to(REPO_ROOT).as_posix(),
                    "type": source_type,
                    "chapter": chapter_name or "",
                    "module": title,
                    "target": "",
                    "pages": str(page_count),
                    "text_pages": str(sum(1 for t in page_texts if t)),
                    "empty_pages": str(sum(1 for t in page_texts if not t)),
                    "chars": str(sum(len(t) for t in page_texts)),
                    "status": "skipped_scanned_no_text_layer",
                }
            )
            continue

        out_dir = OUT_DIR / out_dir_name
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{sanitize_markdown_path(title)}.md"
        if out_path.exists():
            rows.append(
                {
                    "source": pdf.relative_to(REPO_ROOT).as_posix(),
                    "type": source_type,
                    "chapter": chapter_name or "",
                    "module": title,
                    "target": out_path.relative_to(REPO_ROOT).as_posix(),
                    "pages": str(page_count),
                    "text_pages": str(sum(1 for t in page_texts if t)),
                    "empty_pages": str(sum(1 for t in page_texts if not t)),
                    "chars": str(sum(len(t) for t in page_texts)),
                    "status": "skipped_already_exists",
                }
            )
            continue

        content = render_markdown(pdf, title, source_type, chapter_name, page_texts)
        out_path.write_text(content, encoding="utf-8")
        generated.append(out_path)

        chars = sum(len(t) for t in page_texts)
        rows.append(
            {
                "source": pdf.relative_to(REPO_ROOT).as_posix(),
                "type": source_type,
                "chapter": chapter_name or "",
                "module": title,
                "target": out_path.relative_to(REPO_ROOT).as_posix(),
                "pages": str(page_count),
                "text_pages": str(sum(1 for t in page_texts if t)),
                "empty_pages": str(sum(1 for t in page_texts if not t)),
                "chars": str(chars),
                "status": "ok",
            }
        )
        key = chapter_name or source_type
        chapter_counts[key] = chapter_counts.get(key, 0) + 1

    with MANIFEST_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "source",
                "type",
                "chapter",
                "module",
                "target",
                "pages",
                "text_pages",
                "empty_pages",
                "chars",
                "status",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"PDFs scanned: {len(pdfs)}")
    print(f"Markdown generated: {len(generated)}")
    print(f"Skipped/failed: {len(rows) - len(generated)}")
    for line in skipped:
        print("  " + line)
    print(f"Manifest: {MANIFEST_PATH.relative_to(REPO_ROOT).as_posix()}")


if __name__ == "__main__":
    build()
