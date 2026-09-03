# 数据结构 AI 助教 · 创建方式与字段确认

> 版本：v0.1
> 用途：确认 Open WebUI 中模型/智能体的创建入口、字段与存储结构，供提示词编写、知识库挂载、工具挂载和测试共同引用。
> 结论来源：`src/lib/components/workspace/Models/ModelEditor.svelte`、`backend/open_webui/models/models.py`、`backend/open_webui/routers/models.py`。

## 1. 创建入口（UI）

1. 打开「实训 AI 平台」前端 http://localhost:5173。
2. 进入 **Workspace（工作区）→ Models（模型）**。
3. 点击新建模型（Create a model）。
4. 在 ModelEditor 表单中填写字段并保存。

对应后端创建接口为 `POST /api/v1/models/create`，提交体为 `ModelForm`。

## 2. 必填校验

| 校验项 | 规则 |
| --- | --- |
| Model Name | 必填，显示名称 |
| Model ID | 必填、唯一、长度不超过 256 字符 |
| Base Model | 预设模型（preset）时必填，从已有基础模型中选择 |
| Knowledge 文件 | 若挂载文件型知识，需有读取权限 |

## 3. UI 字段与存储字段映射

| UI 字段 | 存储字段 | 说明 | 本组取值 |
| --- | --- | --- | --- |
| Model Name | `name` | 人类可读显示名 | `数据结构 AI 助教` |
| Model ID | `id` | 模型唯一标识 | `ds-assistant`（手动填写） |
| Base Model (From) | `base_model_id` | 上游实际模型 | DeepSeek 对应基础模型 |
| System Prompt | `params.system` | 系统提示词 | 第三步写入 |
| Description | `meta.description` | 简介 | `数据结构课程专属 AI 助教` |
| Tags | `meta.tags` | 标签 | `数据结构`、`AI助教` |
| Knowledge | `meta.knowledge` | 知识库挂载 | 阶段 4 填 `kb_ds_001` |
| Tools | `meta.toolIds` | 工具挂载 | 阶段 4 填工具 ID |
| Skills | `meta.skillIds` | 技能挂载 | 按需 |
| Filters / Actions | `meta.filterIds` / `meta.actionIds` | 过滤器/动作 | 暂不启用 |
| Capabilities | `meta.capabilities` | 能力开关 | 默认关闭 `web_search` 等，避免偏离课程 |
| Access Control | `access_grants` | 权限 | 小组内 `read/write` |
| Advanced Params | `params` | 温度等推理参数 | 默认，可稍降 `temperature` |

## 4. 关键字段说明

### 4.1 Model ID 的生成规则与注意点

前端会在输入 Model Name 时自动生成 Model ID，规则为：

```text
空格 → -
删除非字母/数字/中划线字符
转小写
```

注意：由于模型名是中文，自动生成的 ID 会变成无意义的 `-ai-` 一类结果，因此 **必须手动把 Model ID 改为英文**，建议使用 `ds-assistant`。

### 4.2 System Prompt 存储位置

系统提示词保存在 `params.system`，不是独立文件。因此开发时需在 `docs/prompts/ds-assistant-system-prompt.md` 维护可版本化副本，并在创建模型时把内容粘贴到 System Prompt 文本框。

### 4.3 知识库与工具的挂载位置

- 知识库：`meta.knowledge`，是一个数组，每项可为文件或 collection 引用。
- 工具：`meta.toolIds`，字符串 ID 数组。
- 技能：`meta.skillIds`，字符串 ID 数组。

本阶段（第 2 步）暂不填写，阶段 4 集成时再回填。

### 4.4 基础模型（DeepSeek）

- 基础模型来自已连接的模型列表，在「Base Model (From)」选择器中选取。
- DeepSeek 需先在「管理面板 → 设置 → 连接 → OpenAI API」完成配置：
  - URL：`https://api.deepseek.com`
  - Key：个人 `sk-...`
- 具体 `base_model_id` 以模型列表中 DeepSeek 实际显示的 ID 为准，创建后回填到本表。

## 5. 本组最终取值草案

| 字段 | 值 | 状态 |
| --- | --- | --- |
| model_name | 数据结构 AI 助教 | 确定 |
| model_id | ds-assistant | 待创建后确认 |
| base_model | DeepSeek | 待创建时确认实际 ID |
| provider | OpenAI 兼容 | 确定 |
| system_prompt_path | docs/prompts/ds-assistant-system-prompt.md | 第 3 步创建 |
| knowledge_ids | kb_ds_001 | 阶段 4 回填 |
| tool_ids | 待工具负责人提供 | 阶段 4 回填 |
| version | v0.1 | 创建时填写 |
| status | draft | 创建后改 ready |

## 6. 后续动作

- 第 3 步编写系统提示词，写入 `docs/prompts/ds-assistant-system-prompt.md`。
- 第 6 步创建模型时，按本表填写字段，并回填 `model_id` 与 `base_model` 实际值。

## 7. 变更记录

| 版本 | 日期 | 变更内容 | 维护人 |
| --- | --- | --- | --- |
| v0.1 | 2026-09-03 | 初版，确认模型创建入口、字段映射与本组取值 | 项目统筹 |
