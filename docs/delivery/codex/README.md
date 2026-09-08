# Codex 交互记录汇总

> 用途：汇总小组各成员与 Codex 协作完成本项目的交互记录，作为“与 Codex 的交互记录”交付物。
> 原始记录以成员姓名命名，均存放于本目录。

## 1. 记录清单

| 成员 | 角色 | 记录文件 | 主要工作 | 关键产出 |
| --- | --- | --- | --- | --- |
| 吴泽烨 | 组长 / 项目统筹 / 部署 / 助教 / 集成 / 交付 | `吴泽烨.md` | 任务规划与进度统筹、接口约定、课程范围、系统提示词设计与迭代、模型创建与集成、部署验证、README 与总结报告主笔 | `docs/interface-agreement.md`、`docs/prompts/*`、`docs/testing/assistant-prompt-cases.md`、`docs/delivery/project-summary-report.*` |
| 黄华栋 | 组员B · 扩展工具 | `黄华栋.md` | 调研 Workspace Tool 扩展机制，实现「章节抽题 + 客观题判分」工具，18 个单元测试，接入文档 | `docs/tools/ds_quiz_tool.py`、`docs/tools/test_ds_quiz_tool.py`、`docs/tools/tool-catalog.md`、`docs/tools/tool-usage.md` |
| 朱宝龙 | 组员C · 测试与评价 | `朱宝龙.md` | 设计 16 个测试用例，完成优化前后两轮真实评测，输出测试报告与证据 | `docs/testing/eval_cases.json`、`docs/testing/test_cases_ds.csv`、`docs/testing/test-report-ds.md`、`docs/testing/run_eval.py`、`docs/testing/evidence/` |

## 2. 各成员工作摘要

### 吴泽烨（组长）

- 牵头制定整体分步计划与里程碑，产出接口约定，统一知识库、助教、工具、测试四方的字段与命名。
- 完成部署验证、课程范围锁定、助教模型创建方式确认，编写并迭代系统提示词 v0.1 → v0.3。
- 主笔 README 与项目总结报告，汇总 Git 提交记录与 Codex 交互记录。

### 黄华栋（组员B · 扩展工具）

- 调研确定使用 Workspace Tool（真实结构化输入输出，非提示词模拟）。
- 实现 `ds_quiz` 工具：`ds_random_quiz` 章节随机抽题 + `ds_grade_quiz` 客观题自动判分，内嵌 32 题题库。
- 编写 18 个单元测试并通过，提供元数据登记、使用说明与测试样例。

### 朱宝龙（组员C · 测试与评价）

- 按接口约定设计 16 个测试问题，覆盖知识问答、综合分析、知识库无答案、练习生成/批改、工具调用、错误输入六类。
- 在真实后端（Open WebUI + DeepSeek）上完成 16 例 × 优化前后两轮的评测，输出逐例对比表与分类统计。
- 汇总优化结论：优化前通过 4 / 部分 2 / 失败 10，优化后通过 7 / 部分 9 / 失败 0，引用正确率 0 → 4，回答正确率 14/16 → 15/16。

## 3. 备注

- 知识库（组员A，Git 作者 `silkeobey`）的课程语料库、转换脚本、导入接口等工作已入库（`data/corpus/`、`scripts/build_corpus.py`、`backend/open_webui/routers/course.py` 等），但该成员的 Codex 交互记录未在本目录单独提交；如需补全，请补充对应记录文件。
- 朱宝龙声明的测试交付物（`eval_cases.json`、`test_cases_ds.csv`、`test-report-ds.md`、`run_eval.py`、`evidence/`）在当前工作区的 `docs/testing/` 下尚未全部入库，建议由其提交至 `codex/testing` 分支后评审合并。
