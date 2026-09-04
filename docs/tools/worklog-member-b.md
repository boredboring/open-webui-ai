# 组员B · 扩展工具工作记录

> 角色：扩展工具负责人
> 课程：数据结构
> 日期：2026-09-04

## 1. 调研结论：Open WebUI 扩展开发方式

| 扩展类型 | 定位 | 是否适合本任务 |
| --- | --- | --- |
| Workspace Tool | 原生函数级工具调用，定义 `Tools` 类 + Python 方法，自动生成 OpenAI function spec | ✅ 最适合（真实结构化输入输出） |
| Skill | 给模型的说明性提示 + 资源，偏向指导而非确定性计算 | 不满足“仅提示词模拟不计分” |
| Functions（旧） | 早期插件形式，已被 Tools 取代 | 不采用 |
| 外部 API / MCP | 需要额外服务部署 | 本阶段不采用 |

关键机制（`backend/open_webui/utils/plugin.py` + `utils/tools.py`）：

- 工具源码存数据库 `tool.content`，必须含 `class Tools`。
- `Tools` 类的公共方法（非 `_` 开头、callable）即工具函数。
- 方法参数用类型注解 + docstring（`:param name: desc`）生成 schema。
- 方法返回 JSON 字符串给模型。
- 文件头部用 `"""` 包裹 YAML frontmatter（`title/author/version/description/requirements`）。

## 2. 交付物清单

| 文件 | 说明 |
| --- | --- |
| `docs/tools/ds_quiz_tool.py` | 工具源码：`ds_random_quiz`（章节抽题）+ `ds_grade_quiz`（自动判分），内嵌 32 题题库 |
| `docs/tools/test_ds_quiz_tool.py` | 18 个单元测试（章节解析/抽题/判分/边界/异常） |
| `docs/tools/tool-catalog.md` | 工具元数据与输入输出 schema 登记 |
| `docs/tools/tool-usage.md` | 使用说明、接入步骤、测试样例 |

## 3. 验证证据

1. **单元测试**：`python docs/tools/test_ds_quiz_tool.py` → `Ran 18 tests ... OK`。
2. **真实环境加载验证**：用后端运行的同款 conda 环境（`openwebui`，Python 3.11.16）调用 `open_webui.utils.plugin.load_tool_module_by_id` 成功加载工具，`get_tool_specs` 生成 2 个函数 spec 正确，`ds_random_quiz` / `ds_grade_quiz` 实际执行返回正常（判分 score=100）。
3. 返回结构符合 `docs/interface-agreement.md` 第 7 节（`ok/data` 与 `ok/error` 统一格式）。

## 4. 待办（转组长/集成负责人）

- 在 Workspace → Tools 粘贴 `ds_quiz_tool.py` 创建工具（ID `ds_quiz`）。
- 在「数据结构 AI 助教」模型的 Tools 字段挂接 `ds_quiz`。
- 与 DeepSeek 进行端到端对话调用验证（需管理员凭据）。
