# 数据结构课程 AI 助教 · 项目总结报告

> 版本：v1.0
> 日期：2026-09-08
> 主笔：项目统筹（吴泽烨）
> 仓库：https://github.com/boredboring/open-webui-ai

## 1. 项目概述

本项目基于 [Open WebUI](https://github.com/open-webui/open-webui) v0.11.0 定制开发，搭建了「实训 AI 平台」，并在此平台上完成了课程专属 AI 应用——「数据结构 AI 助教」。系统以 DeepSeek 作为大语言模型，通过模型配置、系统提示词、课程知识库（RAG）与扩展工具，实现课程知识问答、通俗解释、难度自适应、例题/代码讲解、练习题生成、客观题判分、来源引用与超出范围提示等功能，帮助学生理解知识点、复习课程内容并完成自测。

## 2. 课程与目标

- 选定课程：数据结构
- 课程代号：DS
- 章节范围：第 1 章绪论、第 2 章线性表、第 3 章栈队列与数组、第 4 章串、第 5 章树与二叉树、第 6 章图、第 7 章查找、第 8 章排序。
- 服务对象：本科学生，兼顾初学者、进阶学习者与备考学生。
- 核心约束：优先依据知识库作答并给出引用；无资料时明确说明“资料中未找到”，不编造；不代写整份作业。

课程范围基线见 `docs/prompts/ds-course-scope.md`。

## 3. 总体方案与技术栈

系统在 Open WebUI 单仓库基础上扩展，沿用其前后端分离架构：

- 前端：Svelte 5 + SvelteKit 2 + Vite 5，负责聊天、工作区（知识库/模型/工具）与课程语料导入界面。
- 后端：FastAPI + Uvicorn，负责鉴权、模型代理、RAG 检索、工具执行与课程语料导入接口。
- 数据层：SQLite（业务数据）+ ChromaDB（向量检索）。
- 模型：DeepSeek（OpenAI 兼容 API）。
- 扩展方式：Workspace Tool（真实函数级工具调用）+ RAG 知识库。

模块协作关系见 `docs/architecture.md` 与 `docs/project-overview.md`，各模块接口约定见 `docs/interface-agreement.md`。

## 4. 系统部署

完成本地开发环境部署与验证，相关说明位于 `README.md` 的「多人协作开发 · 环境统一配置」一节。

- 环境：Python 3.11（conda 环境 `openwebui`）、Node.js 22 LTS、npm、DeepSeek API Key。
- 启动：根目录 `start-dev.bat` 一键拉起后端（8080）与前端（5173）；也可分别执行 `backend/start-backend.bat` 与 `start-frontend.bat`。
- 模型接入：管理面板 → 设置 → 连接 → OpenAI API，URL `https://api.deepseek.com`。
- 定制改造：平台名改为「实训 AI 平台」，新增快捷提示按钮、`GET /api/v1/help` 帮助接口与一键启动脚本。

部署与运行方式已在前端联调中跑通，供组员按统一环境协作开发。

## 5. 课程知识库

由知识库负责人（silkeobey）完成，形成约 105 份 Markdown 课程语料，按章节与资料类型分类。

- 资料来源：课程课件 PDF（按章节）、习题 PDF、试卷 PDF 三类，共处理 106 份 PDF，生成 105 份 Markdown，约 101 万字符。
- 目录分类：`01_绪论` 至 `08_排序` 按八章归档，另设 `90_习题代码`、`91_试卷`，满足“按章节分类”与“不少于 3 类资料”要求。
- 资料清单：`data/corpus/manifest.csv` 记录每份资料的来源、类型、章节、页数与转换状态；`data/corpus/README.md` 说明格式与入库建议。
- 转换工具：`scripts/build_corpus.py` 负责 PDF → Markdown 的自动化转换与页级切分。
- 导入接口：`backend/open_webui/routers/course.py` 提供课程语料读取接口，并做路径安全校验；前端 `CorpusImportModal.svelte` 提供「从课程语料导入」入口。
- RAG 建议：开启 Markdown 标题切分（Header Splitter），本语料按页/模块组织，切分结果可预期。
- 已知限制：扫描版《王道数据结构》教材（420 页）无文字层，未纳入语料，可后续 OCR；图片型公式与图示不转文字。

知识库已导入 Open WebUI，作为「数据结构 AI 助教」的 RAG 依据来源。

## 6. 课程 AI 助教

由项目统筹（吴泽烨）完成，在 Open WebUI 中创建课程专属模型，并编写、迭代系统提示词。

- 模型创建：Workspace → Models → 新建「数据结构 AI 助教」，Model ID 手动填写 `ds-assistant`，基础模型选择 DeepSeek。字段说明见 `docs/prompts/ds-assistant-model-notes.md`。
- 系统提示词覆盖七项要求：身份、课程范围、回答格式、引用要求、学术诚信、无法确认处理、作业不代写；另含难度自适应与抽题反馈策略。
- 提示词版本管理：按版本独立成文件，`docs/prompts/ds-assistant-system-prompt.md` 为索引，当前最新 v0.3。
  - v0.1：初版，使用【直接结论】等结构标签。
  - v0.2：用自然承接句或分隔线替代死板标签，优化可读性。
  - v0.3：新增练习题与抽题反馈策略，按失败次数、用户熟练程度、题目难度决定“给提示”还是“直接给答案”。
- 结构设计：`docs/prompts/ds-assistant-system-prompt-design.md`。

助教能力对齐任务要求：课程知识问答、通俗解释、难度调整、例题/代码/思路、练习生成、答案分析与改进建议、来源引用、超范围提示。

## 7. 自定义扩展工具

由扩展工具负责人（组员B）完成「数据结构练习题」Workspace Tool（工具 ID `ds_quiz`），属于真实结构化输入输出，非提示词模拟。

- 能力一：`ds_random_quiz` 章节随机抽题，支持按章节、题型（选择/判断/填空）、难度抽题，默认不附答案用于自测。
- 能力二：`ds_grade_quiz` 客观题自动判分，逐题判定并返回正确答案、解析与总分。
- 题库：内嵌 32 道客观题，覆盖第 1~8 章，每章 4 题（2 选择 + 1 判断 + 1 填空）。
- 交付物：`docs/tools/ds_quiz_tool.py`（源码）、`docs/tools/test_ds_quiz_tool.py`（18 个单元测试，全部通过）、`docs/tools/tool-catalog.md`（元数据与 schema）、`docs/tools/tool-usage.md`（使用说明与测试样例）。
- 返回结构统一为 `{"ok": true, "data": ...}` / `{"ok": false, "error": {...}}`，与接口约定一致。

工具通过 Workspace Tool 接入助教模型，可在对话中由模型自动调用。

## 8. 系统测试与评价

### 8.1 已完成的自动化验证

- 扩展工具单元测试：`python docs/tools/test_ds_quiz_tool.py`，18 个用例全部通过，覆盖章节解析、抽题过滤、判分、数量钳制与异常输入。
- 语料导入接口测试：`backend/tests/test_course.py`，覆盖语料目录定位、frontmatter 解析、文件列表分组与路径穿越防护。
- 语料转换验证：`manifest.csv` 记录 105 份 Markdown 状态为 `ok`。

### 8.2 提示词层验收用例

`docs/testing/assistant-prompt-cases.md` 设计 14 条用例，覆盖身份识别、知识问答、通俗解释、难度调整、例题/代码、练习生成、批改建议、超范围提示、不确定处理、学术诚信、引用、作业不代写与异常输入。

### 8.3 优化前后对比

- 提示词 v0.1 → v0.2：修复了回答中机械输出【直接结论】等方括号标题的问题，改为自然承接句或分隔线分段，回答更自然。
- 提示词 v0.2 → v0.3：在抽题工具完成后新增答题反馈策略，明确“失败次数 + 熟练程度 + 题目难度”的分级反馈规则，避免直接抛答案。
- 系统级 16 问优化前后对比（测试负责人朱宝龙）：优化前通过 4 / 部分 2 / 失败 10，优化后通过 7 / 部分 9 / 失败 0；引用正确率 0 → 4，回答正确率 14/16 → 15/16。主要收益在于“知识库无答案”类问题由“编造”转为“资料中未找到 + 明确免责 + 引导”。

### 8.4 系统级测试方案

按任务要求应设计不少于 15 个测试问题，分类为：5 个课程知识问答、3 个综合分析、2 个知识库中无答案的问题、2 个练习生成/批改、2 个自定义工具调用、1 个错误/异常输入。每条记录输入、AI 实际输出、引用是否正确、回答是否正确、存在问题与改进方式。

测试负责人朱宝龙已完成 16 个用例 × 优化前后两轮的端到端评测，交付物位于 `docs/testing/`：`eval_cases.json`（16 个测试问题）、`test_cases_ds.csv`（16 例 × before/after = 32 行记录表）、`test-report-ds.md`（执行报告与逐例对比）、`run_eval.py`（可复现评测脚本）、`evidence/`（真实调用证据）。其中部分交付物需在 `codex/testing` 分支评审后入库。

## 9. 团队分工与协作

| 成员 / 职责 | 主要工作 | 关键交付物 |
| --- | --- | --- |
| 吴泽烨（组长 / 项目统筹 / 助教 / 集成 / 交付） | 任务规划与进度统筹、部署验证、系统提示词设计与迭代、模型创建与集成、README 与总结报告主笔、汇总 Codex 交互记录 | `docs/prompts/*`、`docs/testing/assistant-prompt-cases.md`、`docs/interface-agreement.md`、`docs/delivery/codex/吴泽烨.md` |
| 组员A（silkeobey，知识库负责人） | 课程语料采集与转换、语料库构建、导入接口与前端导入界面、语料导入测试 | `data/corpus/*`、`scripts/build_corpus.py`、`backend/open_webui/routers/course.py`、`backend/tests/test_course.py` |
| 黄华栋（组员B · 扩展工具负责人） | 抽题与判分 Workspace Tool 设计实现、单元测试、工具文档 | `docs/tools/ds_quiz_tool.py`、`docs/tools/test_ds_quiz_tool.py`、`docs/tools/tool-catalog.md`、`docs/tools/tool-usage.md` |
| 朱宝龙（组员C · 测试与评价） | 16 用例设计、优化前后两轮评测、测试报告与可复现脚本 | `docs/testing/eval_cases.json`、`docs/testing/test_cases_ds.csv`、`docs/testing/test-report-ds.md`、`docs/testing/run_eval.py`、`docs/testing/evidence/` |

跨模块协作通过 `docs/interface-agreement.md` 对齐知识库、助教、工具、测试四方的字段、命名与返回格式，降低了联调成本。

## 10. 交付物清单

- 源码与仓库：https://github.com/boredboring/open-webui-ai
- Git 提交记录：`docs/delivery/commit.log`
- Codex 交互记录汇总：`docs/delivery/codex/README.md`（含吴泽烨、黄华栋、朱宝龙三份记录）
- 项目总结报告：本文件（`docs/report/project-summary-report.md`）
- 接口约定：`docs/interface-agreement.md`
- 课程范围：`docs/prompts/ds-course-scope.md`
- 系统提示词：`docs/prompts/ds-assistant-system-prompt-v0.1.md` 至 `v0.3.md` 及索引
- 课程语料库：`data/corpus/`（含 `manifest.csv`、`README.md`）
- 扩展工具：`docs/tools/ds_quiz_tool.py` 及相关文档
- 测试用例与评测：`docs/testing/assistant-prompt-cases.md`、`docs/testing/test_cases_ds.csv`、`docs/testing/test-report-ds.md`、`docs/testing/evidence/`

## 11. 遇到的问题与解决方案

- 中文模型名导致 Model ID 自动生成异常：前端会把中文名过滤成无意义的 `-ai-`，解决方式为手动填写英文 ID `ds-assistant`。
- 系统提示词生硬：v0.1 使用【直接结论】等方括号标签，经协作者反馈后改为自然承接句与分隔线，显著改善可读性。
- 扫描版教材无文字层：420 页王道教材 PDF 无法直接提取文本，暂时未纳入语料，后续可用 OCR 处理。
- 工具必须真实结构化：选择 Workspace Tool 而非纯提示词模拟，确保抽题与判分具有确定性的输入输出，满足“不计为提示词模拟”的要求。
- PDF 公式/代码提取损失：图片型公式与图示不转文字，代码缩进可能丢失，需与原始 PDF 对照并在文档中标注限制。

## 12. 总结

本项目完整走通了“部署 → 知识库 → 模型/提示词 → 工具扩展 → 集成联调 → 测试评价 → 交付”的全流程，交付了可运行的数据结构课程 AI 助教。系统以 DeepSeek 为底座、课程语料库为知识来源、抽题判分工具为扩展能力，实现了课程问答、复习自测与按水平反馈的闭环。通过接口约定统一各成员交付边界，团队协作顺畅；提示词按版本迭代并沉淀文档，为后续扩展其他课程与更多工具提供了可复用的模板。
