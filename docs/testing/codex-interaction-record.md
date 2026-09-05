# Codex 交互记录（测试与评价）

> 日期：2026-09-05　时段：约 09:45–13:40（Asia/Hong_Kong）
> 说明：本文件记录本轮“测试与评价”任务中 Codex 的实际操作、关键决策与遗留改动，供团队复核与复现。所有真实调用输出均以 JSON 落盘于 `docs/testing/evidence/`。

## 1. 目标回顾

按 `docs/interface-agreement.md` §8 完成 ≥15 例（实际 16 例）测试：
课程知识问答 5 / 综合分析 3 / 知识库无答案 2 / 练习生成与批改 2 / 工具调用 2 / 错误输入异常 2；
逐例记录输入/实际输出/引用正确性/回答正确性/问题/改进；组织同批问题的优化前后对比；整理 Codex 交互记录。

## 2. 环境现状核查（只读阶段）

| 动作 | 结果 |
| --- | --- |
| 阅读 `docs/interface-agreement.md`、`docs/prompts/*`、`docs/tools/tool-catalog.md`、`docs/testing/assistant-prompt-cases.md`、`docs/project-overview.md` | 明确课程=数据结构、模型=数据结构 AI 助教(123)、工具=ds_quiz_tool、测试字段与类别要求 |
| 检查 `backend/data/webui.db` | 用户 zjb(admin)、模型 123（deepseek-v4-flash，挂 ds_quiz_tool，无系统提示词、无知识库）、1 段历史对话；knowledge 表为空 |
| 检查语料 `data/corpus/` | 105 个 md（第1–8章+习题+试卷，约 935 KB），与 8 章课程范围一致 |
| 检查运行状态 | 8080/5173 无监听 → 需要自行拉起后端才能做“真实输出”评测 |

## 3. 启动与联调（含环境适配，重要）

| 步骤 | 遇到问题 | 处理 |
| --- | --- | --- |
| 拉起 uvicorn 后端（conda env openwebui） | HuggingFace `xet` 下载卡死/失败，7 个 onnx/openvino 文件缺失导致快照“incomplete” | 无需 onnx/openvino：复制 torch 必需文件到本地目录 `backend/data/embed_models/all-MiniLM-L6-v2`；把 DB `rag.embedding_model` 改为该本地路径（配置表为 JSON 编码，需 `json.dumps` 写入），启动不再访问 HF |
| aiohttp 外联 | 后端报 “Could not contact DNS servers”（aiohttp 3.13 默认 AsyncResolver 走裸 DNS 被环境拦截；urllib/getaddrinfo 正常） | 在 `backend/open_webui/main.py` 与 `backend/open_webui/utils/session_pool.py` 注入 `aiohttp.connector.DefaultResolver = aiohttp.ThreadedResolver`（改走系统解析器；对正常网络无副作用，可保留） |
| 模型列表为空 | `openai.api_base_urls[1]` 首字符是 `\t` 导致 deepseek 连接失败 | 修正配置为 `https://api.deepseek.com`；`?refresh=true` 后取得 deepseek-v4-flash / v4-pro / v4-flash-vision-exp |
| API 调用模型 123 | 不带 UI session 时不会自动注入模型 meta 中的工具 | 请求体显式传 `"tool_ids": ["ds_quiz_tool"]` |
| 工具调用返回后无正文 | Open WebUI 对非流式 API 返回 `finish_reason=tool_calls` 即停 | 评测脚本实现客户端工具循环：执行 `docs/tools/ds_quiz_tool.py` 本地函数→回填 `role:tool` 消息→继续，直至最终文本 |
| 知识库 RAG 不触发 | 知识库项缺 `type`，模型 meta 缓存旧（无 knowledge） | model.meta.knowledge 每项补 `"type":"collection"`（对应 chroma 集合名=KB id）；`setup_after` 与 `after` 阶段在改模型后再次 `refresh_models`；after 阶段请求级挂接 `files:[{id,name,type:collection}]` |

验证探针：RAG 问答输出含 `[1][2]` 引用并命中课程片段；工具用例输出真实题库题目与判分（见 `evidence/after/T01…T16.json` 及 `snapshot_after.json`）。

## 4. 评测执行（真实调用 DeepSeek）

| 阶段 | 命令/方式 | 结果 |
| --- | --- | --- |
| 冒烟 smoke | `python docs/testing/run_eval.py smoke` | 后端就绪、模型列表 5 个、对话返回正常 |
| before | `python docs/testing/run_eval.py before`（先 `set_model_before()`：清空系统提示词与知识库，保留工具） | 16 例全部 HTTP 200，落盘 `evidence/before/` |
| setup_after | `python docs/testing/run_eval.py setup_after` | 建 KB(kb_ds_001,id `628b5a40-…`)；导入 105/105 成功（分 7 批）；模型挂 v0.3 提示词+知识库；检索参数写入 chunk500/overlap50/top_k5/hybrid |
| after | `python docs/testing/run_eval.py after`（重新应用 after 配置后执行同批 16 例） | 16 例全部 HTTP 200，落盘 `evidence/after/` |

评测脚本不依赖前端，每例新建 chat 并记录输出、工具轨迹（`tool_trace`）、耗时；判定由人工对照 `eval_cases.json` 完成。

## 5. 结果整理（本任务交付物）

| 文件 | 内容 |
| --- | --- |
| `docs/testing/eval_cases.json` | 16 例输入/预期/判断标准（含 6 类覆盖） |
| `docs/testing/test_cases_ds.csv` | 接口约定 §8.1 字段，16 例 × before/after = 32 行判定明细 |
| `docs/testing/test-report-ds.md` | 执行报告：结论摘要、环境配置、逐例 before/after 对比表、分类统计、问题与改进清单 |
| `docs/testing/run_eval.py` | 可复现评测脚本（smoke/before/setup_after/after） |
| `docs/testing/evidence/` | before/after 逐例 JSON + 配置快照 + RAG 探针（真实调用证据） |
| `docs/testing/assistant-prompt-cases.md` | 未改动（提示词层用例，本报告为其端到端落地） |

判定汇总：before 通过 4 / 部分 2 / 失败 10；after 通过 7 / 部分 9 / 失败 0。详见报告 §1。

## 6. 对仓库/运行数据的改动说明

**源码（建议评审后决定是否保留）：**
- `backend/open_webui/main.py`：注入 `aiohttp.connector.DefaultResolver = aiohttp.ThreadedResolver`（约 9 行，注释标明用途）。
- `backend/open_webui/utils/session_pool.py`：TCPConnector 显式传 ThreadedResolver（1 行）。
- 两者仅为“受限网络下走系统 DNS”的环境兼容，不影响正常外网。

**运行数据（`backend/data/*`，已 gitignore，不入库）：**
- `webui.db`：用户/模型配置不变；模型 123 现为 after 配置（v0.3 提示词 + 知识库 kb_ds_001，type=collection）；RAG 参数已调优；`rag.embedding_model` 指向本地模型目录；`openai.api_base_urls` 修正 deepseek URL。
- Chroma：`vector_db/` 新增 107 collections（kb_ds_001 + 106 个 file-*）。
- `backend/data/embed_models/all-MiniLM-L6-v2`：本地嵌入模型副本（约 91 MB）。

**建议后续动作：**
1. 若不想保留 aiohttp 补丁，可用 `git checkout -- backend/open_webui/main.py backend/open_webui/utils/session_pool.py` 还原（之后在正常网络环境启动即可）。
2. 知识库/模型 after 配置建议保留（即“优化后”状态），供团队在 UI 复核引用效果。
3. 复现任意一轮：在能联网的终端 `conda activate openwebui` 后执行 `python docs/testing/run_eval.py before|setup_after|after`。

## 7. 变更记录

| 版本 | 日期 | 变更内容 | 维护人 |
| --- | --- | --- | --- |
| v1.0 | 2026-09-05 | 记录本轮测试执行的交互、环境适配与交付物 | Codex（测试负责人确认） |
