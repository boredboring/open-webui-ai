# -*- coding: utf-8 -*-
"""数据结构 AI 助教 · 端到端评测执行脚本（before / setup_after / after / smoke）。

用法（在能访问 DeepSeek 的环境中）:
    python run_eval.py smoke        # 快速冒烟：启动后端->刷新模型->1 次对话
    python run_eval.py before       # 优化前：16 用例跑一遍（模型现状：无知识库/无系统提示词）
    python run_eval.py setup_after  # 应用优化：建知识库+导入语料+挂载知识库/系统提示词 v0.3+检索参数
    python run_eval.py after        # 优化后：同批 16 用例再跑一遍

说明：
- 脚本会在 127.0.0.1:8080 临时拉起 Open WebUI 后端，跑完自动关闭。
- 每轮结果 JSON 输出到 docs/testing/evidence/{before,after}/<case_id>.json。
- after 阶段通过请求级 files 挂接知识库（等同 UI 中“在对话里选择知识库”），保证
  检索可复现；before 阶段不挂任何知识库。
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
import sqlite3
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

ROOT = Path(r"D:\open-webui-ai")
BACKEND = ROOT / "backend"
DATA_DIR = BACKEND / "data"
CORPUS = ROOT / "data" / "corpus"
TESTING = ROOT / "docs" / "testing"
EVIDENCE = TESTING / "evidence"
PYTHON = r"C:\Users\20174\miniconda3\envs\openwebui\python.exe"
DB = DATA_DIR / "webui.db"
SECRET = "b8e1c94f6d2a7e3f0c5d8a1b4e7f9c2d"
USER_ID = "2febe837-05ba-4e99-8c19-9140546512ad"
MODEL_ID = "123"
BASE = "http://127.0.0.1:8080"
PROMPT_V03 = TESTING.parent / "prompts" / "ds-assistant-system-prompt-v0.3.md"

CASES = json.loads((TESTING / "eval_cases.json").read_text(encoding="utf-8"))

ENV = {
    "WEBUI_SECRET_KEY": SECRET,
    "COURSE_CORPUS_DIR": str(CORPUS),
    "HF_HUB_OFFLINE": "1",
    "HF_HUB_DISABLE_XET": "1",
    "HF_HUB_DISABLE_SYMLINKS_WARNING": "1",
    "SCARF_NO_ANALYTICS": "true",
    "DO_NOT_TRACK": "true",
    "PYTHONUNBUFFERED": "1",
}
ENV.update({k: v for k, v in os.environ.items() if k in ("PATH", "SYSTEMROOT", "HOMEDRIVE", "HOMEPATH", "USERPROFILE", "APPDATA", "LOCALAPPDATA", "TMP", "TEMP")})


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


# ---------- DB helpers ----------
def db_conn():
    return sqlite3.connect(str(DB), timeout=60)


def cfg_get(key):
    con = db_conn()
    try:
        row = con.execute("select value from config where key=?", (key,)).fetchone()
        if row is None:
            return None
        v = row[0]
        if isinstance(v, str):
            try:
                return json.loads(v)
            except Exception:
                return v
        return v
    finally:
        con.close()


def cfg_set(key, value):
    con = db_conn()
    try:
        if isinstance(value, (dict, list, str, bool)) or value is None:
            enc = json.dumps(value)
        else:
            enc = value
        con.execute("update config set value=? where key=?", (enc, key))
        con.commit()
    finally:
        con.close()


def set_model(prompt_text=None, knowledge=None):
    con = db_conn()
    try:
        row = con.execute("select params, meta from model where id=?", (MODEL_ID,)).fetchone()
        params = json.loads(row[0]) if row[0] else {}
        meta = json.loads(row[1]) if row[1] else {}
        if prompt_text is not None:
            params["system"] = prompt_text
        if knowledge is not None:
            for it in knowledge:
                it.setdefault("type", "collection")
            meta["knowledge"] = knowledge
        con.execute(
            "update model set params=?, meta=? where id=?",
            (json.dumps(params, ensure_ascii=False), json.dumps(meta, ensure_ascii=False), MODEL_ID),
        )
        con.commit()
    finally:
        con.close()



def set_model_before():
    """重置为‘优化前’模型配置：无系统提示词、不挂知识库（保留工具与能力）。"""
    con = db_conn()
    try:
        row = con.execute("select params, meta from model where id=?", (MODEL_ID,)).fetchone()
        params = json.loads(row[0]) if row[0] else {}
        meta = json.loads(row[1]) if row[1] else {}
        params.pop("system", None)
        params.pop("function_calling", None)
        meta.pop("knowledge", None)
        con.execute(
            "update model set params=?, meta=? where id=?",
            (json.dumps(params, ensure_ascii=False), json.dumps(meta, ensure_ascii=False), MODEL_ID),
        )
        con.commit()
        log("模型已重置为 before 配置（无系统提示词、无知识库）")
    finally:
        con.close()


TOOL_MODULE_CACHE = {}


def run_tool(name, args_json):
    """在本地执行 ds_quiz 工具（与 Open WebUI 服务器端工具执行一致）。"""
    global TOOL_MODULE_CACHE
    mod_path = TESTING.parent / "tools" / "ds_quiz_tool.py"
    if "tools" not in TOOL_MODULE_CACHE:
        import importlib.util

        spec = importlib.util.spec_from_file_location("ds_quiz_tool_local", mod_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        TOOL_MODULE_CACHE["tools"] = mod.Tools()
    tools = TOOL_MODULE_CACHE["tools"]
    args = json.loads(args_json) if isinstance(args_json, str) else (args_json or {})
    fn = getattr(tools, name, None)
    if fn is None:
        return json.dumps({"ok": False, "error": {"code": "NO_TOOL", "message": f"未找到工具函数 {name}"}}, ensure_ascii=False)
    try:
        out = fn(**args)
        return out if isinstance(out, str) else json.dumps(out, ensure_ascii=False)
    except TypeError as e:
        return json.dumps({"ok": False, "error": {"code": "BAD_ARGS", "message": str(e)}}, ensure_ascii=False)

def get_sources_for_chat(chat_id):
    con = db_conn()
    try:
        rows = con.execute("select sources from chat_message where chat_id=? and sources is not null", (chat_id,)).fetchall()
        out = []
        for (s,) in rows:
            try:
                out.append(json.loads(s))
            except Exception:
                out.append(s)
        return out
    finally:
        con.close()


# ---------- HTTP ----------
def http(method, path, body=None, token=None, timeout=120):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = "Bearer " + token
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read().decode("utf-8", "replace")
            return r.status, json.loads(raw) if raw else None
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", "replace")
        return e.code, raw


def mint_token():
    import base64

    def b64(b):
        return base64.urlsafe_b64encode(b).rstrip(b"=").decode()

    header = b64(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    payload = b64(json.dumps({"id": USER_ID, "exp": int(time.time()) + 7200}).encode())
    signing = f"{header}.{payload}".encode()
    sig = b64(hmac.new(SECRET.encode(), signing, hashlib.sha256).digest())
    return f"{header}.{payload}.{sig}"


# ---------- backend process ----------
def start_backend():
    log("启动后端 ...")
    out = DATA_DIR / "_eval_backend_out.log"
    err = DATA_DIR / "_eval_backend_err.log"
    p = subprocess.Popen(
        [PYTHON, "-u", "-m", "uvicorn", "open_webui.main:app", "--host", "127.0.0.1", "--port", "8080"],
        cwd=str(BACKEND), env=ENV, stdout=open(out, "w", encoding="utf-8"), stderr=open(err, "w", encoding="utf-8"),
    )
    deadline = time.time() + 240
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(BASE + "/health", timeout=3) as r:
                if r.status == 200:
                    log("后端健康检查通过")
                    return p
        except Exception:
            pass
        if p.poll() is not None:
            raise RuntimeError(f"后端进程退出 code={p.returncode}; 日志尾部见 {err}")
        time.sleep(2)
    raise RuntimeError("后端 240s 内未就绪")


def refresh_models(token, tries=8):
    for i in range(tries):
        code, data = http("GET", "/api/v1/models?refresh=true", token=token, timeout=90)
        if code == 200 and data and isinstance(data.get("data"), list):
            ids = [m.get("id") for m in data["data"]]
            if "deepseek-v4-flash" in ids:
                log(f"模型列表就绪（第 {i+1} 次刷新），共 {len(ids)} 个外部模型")
                return ids
        time.sleep(3)
    raise RuntimeError("刷新模型列表失败（无法获取 deepseek-v4-flash）；请检查后端日志与网络")


def stop_backend(p):
    if p and p.poll() is None:
        p.terminate()
        try:
            p.wait(timeout=15)
        except Exception:
            p.kill()
    log("后端已停止")


def read_prompt_v03():
    text = PROMPT_V03.read_text(encoding="utf-8")
    m = re.search(r"```text\s*(.*?)\s*```", text, re.S)
    if not m:
        raise RuntimeError("无法从 v0.3 提示词文件中提取代码块")
    return m.group(1)


# ---------- batch runner ----------
def chat_completion(token, user_input, chat_id, timeout=600, files=None):
    """带工具执行循环的单轮对话（等价 UI 智能体循环）。"""
    messages = [{"role": "user", "content": user_input}]
    tool_trace = []
    final_content = ""
    t0 = time.time()
    for step in range(6):
        body = {
            "model": MODEL_ID,
            "messages": messages,
            "stream": False,
            "chat_id": chat_id,
            "tool_ids": ["ds_quiz_tool"],
        }
        if files:
            body["files"] = files
        code, data = http("POST", "/api/chat/completions", body=body, token=token, timeout=timeout)
        if code != 200 or not isinstance(data, dict):
            return code, data, time.time() - t0, tool_trace
        try:
            msg = data["choices"][0]["message"]
        except Exception:
            return code, data, time.time() - t0, tool_trace
        content = msg.get("content") or ""
        tool_calls = msg.get("tool_calls")
        if not tool_calls:
            final_content = content
            break
        messages.append({"role": "assistant", "content": content or None, "tool_calls": tool_calls})
        for tc in tool_calls:
            fn_name = tc["function"]["name"]
            fn_args = tc["function"].get("arguments") or "{}"
            result = run_tool(fn_name, fn_args)
            tool_trace.append({"step": step, "name": fn_name, "arguments": fn_args, "result": result[:2000]})
            messages.append({"role": "tool", "tool_call_id": tc["id"], "content": result})
        if step >= 5:
            final_content = content
            break
    return 200, {"choices": [{"message": {"role": "assistant", "content": final_content}}]}, time.time() - t0, tool_trace


def run_batch(phase, token, kb=None):
    out_dir = EVIDENCE / phase
    out_dir.mkdir(parents=True, exist_ok=True)
    files = [{"id": kb["id"], "name": kb["name"], "type": "collection"}] if kb else None
    summary = []
    for case in CASES:
        cid = case["id"]
        chat_id = str(uuid.uuid4())
        log(f"[{phase}] {cid} 开始: {case['input'][:40]}...")
        code, data, elapsed, tool_trace = chat_completion(token, case["input"], chat_id, files=files)
        content = ""
        citations = []
        if code == 200 and isinstance(data, dict):
            try:
                content = data["choices"][0]["message"]["content"] or ""
            except Exception:
                content = ""
            citations = data.get("citations") or []
        sources = get_sources_for_chat(chat_id) if code == 200 else []
        rec = {
            "phase": phase, "case_id": cid, "category": case["category"], "input": case["input"],
            "http_status": code, "elapsed_s": round(elapsed, 1),
            "output": content, "tool_trace": tool_trace, "response_citations": citations,
            "retrieved_sources": sources, "chat_id": chat_id, "attached_kb": kb,
        }
        (out_dir / f"{cid}.json").write_text(json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8")
        summary.append({"case_id": cid, "status": code, "elapsed_s": round(elapsed, 1), "output_len": len(content)})
        log(f"[{phase}] {cid} 完成 code={code} len={len(content)} {elapsed:.0f}s")
        time.sleep(1)
    (out_dir / "_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    log(f"[{phase}] 批次完成，共 {len(summary)} 例")


# ---------- setup knowledge ----------
def corpus_files():
    files = []
    for p in sorted(CORPUS.rglob("*.md")):
        if p.name == "README.md":
            continue
        files.append(p.relative_to(CORPUS).as_posix())
    return files


def create_kb(token):
    code, data = http("POST", "/api/v1/knowledge/create", body={
        "name": "数据结构课程知识库(kb_ds_001)",
        "description": "数据结构第1-8章语料（课件/习题/试卷），供测试评估",
    }, token=token, timeout=60)
    if code != 200:
        raise RuntimeError(f"创建知识库失败 {code}: {data}")
    kid = data.get("id")
    log(f"知识库已创建 id={kid}")
    return kid, data.get("name")


def import_corpus(token, kid, batch=15):
    files = corpus_files()
    log(f"开始导入 {len(files)} 个语料文件到 {kid}")
    total_ok, total_fail = 0, []
    for i in range(0, len(files), batch):
        chunk = files[i:i + batch]
        code, data = http("POST", "/api/v1/course/corpus/import", body={"knowledge_id": kid, "files": chunk}, token=token, timeout=1200)
        if code != 200:
            log(f"批次 {i} 导入请求失败 {code}: {str(data)[:200]}")
            total_fail.extend(chunk)
            continue
        ok = data.get("imported") or []
        fail = data.get("failed") or []
        skip = data.get("skipped") or []
        total_ok += len(ok)
        total_fail += [f["path"] for f in fail]
        log(f"批次 {i//batch+1}: ok={len(ok)} skip={len(skip)} fail={len(fail)} 累计ok={total_ok}")
        for f in fail[:3]:
            log(f"   失败: {f['path']}: {str(f.get('error'))[:120]}")
    log(f"导入结束：成功 {total_ok}，失败 {len(total_fail)}")
    return total_ok, total_fail


def snapshot(token, kid, kb_name, phase):
    cfg_keys = ["rag.chunk_size", "rag.chunk_overlap", "rag.top_k", "rag.enable_hybrid_search", "rag.embedding_model"]
    snap = {
        "phase": phase,
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "knowledge": {"id": kid, "name": kb_name} if kid else None,
        "config": {k: cfg_get(k) for k in cfg_keys},
        "prompt_version": "v0.3" if phase == "after" else "无（默认助手）",
    }
    con = db_conn()
    try:
        row = con.execute("select params, meta from model where id=?", (MODEL_ID,)).fetchone()
        params = json.loads(row[0]) if row[0] else {}
        meta = json.loads(row[1]) if row[1] else {}
        snap["model_meta"] = {
            "has_system_prompt": bool(params.get("system")),
            "system_prompt_source": "ds-assistant-system-prompt-v0.3.md" if params.get("system") else None,
            "knowledge": meta.get("knowledge"),
            "toolIds": meta.get("toolIds"),
            "params_keys": list(params.keys()),
        }
    finally:
        con.close()
    (EVIDENCE / f"snapshot_{phase}.json").write_text(json.dumps(snap, ensure_ascii=False, indent=2), encoding="utf-8")
    log("配置快照已写入 evidence/snapshot_%s.json" % phase)


# ---------- stages ----------
def stage_smoke():
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    p = start_backend()
    try:
        tok = mint_token()
        refresh_models(tok)
        code, data, el = chat_completion(tok, "请只回复两个字：收到", str(uuid.uuid4()), timeout=180)
        content = ""
        if code == 200:
            content = data["choices"][0]["message"].get("content") or ""
        log(f"冒烟对话 code={code} len={len(content)}")
        if code != 200 or not content:
            raise RuntimeError("冒烟对话失败")
    finally:
        stop_backend(p)


def stage_before():
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    set_model_before()
    p = start_backend()
    try:
        tok = mint_token()
        refresh_models(tok)
        snapshot(tok, None, None, "before")
        run_batch("before", tok)
    finally:
        stop_backend(p)


def stage_setup_after():
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    log("写入优化后检索参数（切分 500/50、top_k=5、混合检索开）")
    cfg_set("rag.chunk_size", 500)
    cfg_set("rag.chunk_overlap", 50)
    cfg_set("rag.top_k", 5)
    cfg_set("rag.enable_hybrid_search", True)
    p = start_backend()
    try:
        tok = mint_token()
        refresh_models(tok)
        kid, kb_name = create_kb(tok)
        ok, fail = import_corpus(tok, kid)
        if ok == 0:
            raise RuntimeError("语料导入全部失败，终止 setup_after")
        prompt = read_prompt_v03()
        set_model(prompt_text=prompt, knowledge=[{"id": kid, "name": kb_name}])
        log("已更新模型：挂载知识库 + 系统提示词 v0.3")
        refresh_models(tok)
        snapshot(tok, kid, kb_name, "after")
    finally:
        stop_backend(p)


def stage_after():
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    snap = json.loads((EVIDENCE / "snapshot_after.json").read_text(encoding="utf-8"))
    kb = snap.get("knowledge") or {}
    log("after 阶段请求级挂接知识库: " + json.dumps(kb, ensure_ascii=False))
    p = start_backend()
    try:
        tok = mint_token()
        refresh_models(tok)
        set_model(prompt_text=read_prompt_v03(), knowledge=[kb])
        refresh_models(tok)
        run_batch("after", tok, kb=kb)
    finally:
        stop_backend(p)


if __name__ == "__main__":
    stage = sys.argv[1] if len(sys.argv) > 1 else "smoke"
    fn = {"smoke": stage_smoke, "before": stage_before, "setup_after": stage_setup_after, "after": stage_after}.get(stage)
    if fn is None:
        raise SystemExit("用法: run_eval.py [smoke|before|setup_after|after]")
    fn()



