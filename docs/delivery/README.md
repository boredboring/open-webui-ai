# 项目交付物说明

> 本文件说明本项目全部交付物的存放位置，方便评审与归档。

## 1. 交付物清单

| 交付物 | 位置 | 说明 |
| --- | --- | --- |
| 源码与仓库 | https://github.com/boredboring/open-webui-ai | 项目源码仓库 |
| Git 提交记录 | [commit.log](commit.log) | 项目 Git 提交历史 |
| Codex 交互记录 | [codex/](codex/) | 各成员与 Codex 的交互记录；汇总见 [codex/README.md](codex/README.md)，原始记录为吴泽烨、黄华栋、朱宝龙三份 |
| 项目总结报告 | [project-summary-report.md](project-summary-report.md)、[project-summary-report.tex](project-summary-report.tex)、[project-summary-report.pdf](project-summary-report.pdf) | Markdown 源稿、LaTeX 源码与编译后的 PDF |
| 接口约定 | [../interface-agreement.md](../interface-agreement.md) | 知识库、助教、工具、测试四方的字段、命名与返回格式约定 |
| 课程范围 | [../prompts/ds-course-scope.md](../prompts/ds-course-scope.md) | 数据结构课程章节清单与范围边界 |
| 系统提示词 | [../prompts/ds-assistant-system-prompt.md](../prompts/ds-assistant-system-prompt.md) | 版本索引；具体版本见 `ds-assistant-system-prompt-v0.1.md` 至 `v0.3.md` |
| 课程语料库 | [../../data/corpus/](../../data/corpus/) | 知识库语料，含 `manifest.csv` 资料清单与 `README.md` 说明 |
| 扩展工具 | [../tools/ds_quiz_tool.py](../tools/ds_quiz_tool.py) | 抽题 + 判分 Workspace Tool 源码，配套文档见 [../tools/tool-catalog.md](../tools/tool-catalog.md)、[../tools/tool-usage.md](../tools/tool-usage.md) |
| 测试用例与评测 | [../testing/assistant-prompt-cases.md](../testing/assistant-prompt-cases.md) | 提示词层验收用例；端到端 16 例评测见测试负责人交付（`eval_cases.json`、`test_cases_ds.csv`、`test-report-ds.md`、`run_eval.py`、`evidence/`） |

## 2. 交付物用途

- **源码与仓库**：项目可运行代码与版本历史。
- **Git 提交记录**：证明开发过程与分工的提交历史。
- **Codex 交互记录**：小组各成员与 Codex 协作完成任务的完整过程记录。
- **项目总结报告**：项目背景、方案、实现、测试、分工与交付的总体说明。
- **接口约定 / 课程范围 / 系统提示词**：助教功能的设计与实现依据。
- **课程语料库 / 扩展工具**：知识库与自定义扩展功能的直接产物。
- **测试用例与评测**：功能正确性与优化前后对比的验证依据。

## 3. 待补事项

- 组员A（知识库，Git 作者 `silkeobey`）的 Codex 交互记录尚未单独提交至 [codex/](codex/) 目录。
- 测试负责人朱宝龙声明的测试交付物（`eval_cases.json`、`test_cases_ds.csv`、`test-report-ds.md`、`run_eval.py`、`evidence/`）需提交至 `codex/testing` 分支后评审合并。
