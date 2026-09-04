# 扩展工具目录（Tool Catalog）

> 版本：v1.0
> 维护人：组员B（扩展工具负责人）
> 关联文档：`docs/interface-agreement.md` 第 7 节、`docs/tools/tool-usage.md`、`docs/tools/ds_quiz_tool.py`

本文件登记「数据结构 AI 助教」所挂接的扩展工具元数据，供助教集成负责人与测试负责人对齐。

## 1. 工具概览

| 字段 | 值 |
| --- | --- |
| tool_id | ds_quiz |
| tool_name | 数据结构练习题（抽题 + 判分） |
| tool_type | Workspace Tool |
| description | 按章节随机抽取数据结构客观题（选择/判断/填空），并对学生提交的答案自动判分、给出解析与得分 |
| version | v1.0 |
| owner | 组员B |
| status | ready |

## 2. 工具函数

工具源码内定义 `class Tools`，共暴露两个函数（即两个可被模型调用的工具）：

| 函数名 | 用途 |
| --- | --- |
| `ds_random_quiz` | 章节随机抽题（默认不附答案，供自测） |
| `ds_grade_quiz` | 客观题自动判分（逐题判定 + 解析 + 总分） |

## 3. 输入输出结构

### 3.1 ds_random_quiz（抽题）

**输入（OpenAI function calling 参数）**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| chapter | string | 是 | — | 章节，支持“第3章”“3”“ch03”或主题词（如“栈”“二叉树”“排序”） |
| question_count | integer | 否 | 5 | 抽题数量 |
| question_type | string | 否 | choice | choice/judge/fill/all |
| difficulty | string | 否 | all | easy/medium/hard/all |
| include_answer | boolean | 否 | false | 是否在出题时附带答案与解析（自测模式为 false） |

**输出（JSON 字符串）**

```json
{
  "ok": true,
  "data": {
    "chapter": "第3章 栈、队列和数组",
    "question_count": 3,
    "questions": [
      {
        "id": "ch03_001",
        "type": "choice",
        "difficulty": "easy",
        "stem": "栈的特点是（　）。",
        "options": ["A. 先进先出", "B. 后进先出", "C. 随机存取", "D. 只允许在一端进、另一端出"]
      }
    ]
  }
}
```

### 3.2 ds_grade_quiz（判分）

**输入**

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| questions | string | 是 | `ds_random_quiz` 返回的 `data.questions` 数组的 JSON 字符串 |
| answers | string | 是 | 学生答案的 JSON 数组字符串，按题目顺序，如 `'["B","对","栈"]'` |

**输出**

```json
{
  "ok": true,
  "data": {
    "total": 3,
    "correct_count": 2,
    "wrong_count": 1,
    "score": 66.7,
    "results": [
      {
        "index": 1,
        "question_id": "ch03_001",
        "type": "choice",
        "stem": "栈的特点是（　）。",
        "user_answer": "B",
        "correct_answer": "B",
        "correct": true,
        "graded": true,
        "explanation": "栈是只允许在一端进行插入和删除的线性表，特点是后进先出（LIFO）。"
      }
    ]
  }
}
```

### 3.3 错误返回（统一结构）

```json
{"ok": false, "error": {"code": "INVALID_CHAPTER", "message": "未找到该章节……"}}
```

| code | 含义 |
| --- | --- |
| INVALID_CHAPTER | 章节无法识别 |
| NO_QUESTION | 该章节没有符合条件的题目 |
| INVALID_QUESTIONS | questions 不是合法 JSON 数组 |
| LENGTH_MISMATCH | 题目数量与答案数量不一致 |

## 4. 自然语言触发示例

1. “帮我从第 3 章随机抽 5 道选择题，难度中等。”
2. “从第 2 章抽 3 道题，题型不限，先不要给答案。”
3. “把这几道题判一下分，我的答案是 B、对、栈。”
4. “第 5 章二叉树章节，抽 4 道题并附上答案和解析。”

## 5. 题库范围

内嵌题库共 **32 道客观题**，覆盖第 1~8 章，每章 4 题（2 道选择 + 1 道判断 + 1 道填空），知识点与 `docs/prompts/ds-course-scope.md` 的章节清单一致。

## 6. 变更记录

| 版本 | 日期 | 变更内容 | 维护人 |
| --- | --- | --- | --- |
| v1.0 | 2026-09-04 | 初版：章节抽题 + 客观题判分，内嵌 32 题题库 | 组员B |
