# 扩展工具使用说明与测试样例

> 工具 ID：`ds_quiz`
> 源码：`docs/tools/ds_quiz_tool.py`
> 测试脚本：`docs/tools/test_ds_quiz_tool.py`
> 维护人：组员B

## 1. 工具能做什么

「数据结构练习题」工具提供两个能力，均为**真实结构化输入输出**（非提示词模拟）：

1. **章节随机抽题**（`ds_random_quiz`）：从内嵌题库按章节、题型、难度随机抽题，默认不返回答案，方便学生自测。
2. **客观题自动判分**（`ds_grade_quiz`）：接收题目与学生的答案列表，逐题判定对错、给出标准答案与解析，并汇总得分。

题库覆盖第 1~8 章共 32 道题（选择 / 判断 / 填空），知识点与课程章节清单一致。

## 2. 接入助教（Workspace Tool）

### 方式 A：界面创建（推荐）

1. 打开前端 http://localhost:5173 ，进入 **Workspace → Tools**。
2. 点击新建工具，将 `docs/tools/ds_quiz_tool.py` 的**全部内容**粘贴到代码编辑器。
3. 工具名建议填「数据结构练习题」，工具 ID 填 `ds_quiz`（前端会根据 frontmatter 的 `title` 自动生成，需手动核对为英文小写）。
4. 保存。前端会自动读取 frontmatter 的 `description` 填入工具简介。
5. 在 **Workspace → Models → 数据结构 AI 助教** 的 Tools 字段中挂接 `ds_quiz`。

### 方式 B：API 创建

```bash
curl -X POST http://localhost:8080/api/v1/tools/create \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "ds_quiz",
    "name": "数据结构练习题（抽题 + 判分）",
    "content": "<ds_quiz_tool.py 的全部源码>",
    "meta": {"description": "按章节随机抽取数据结构客观题并自动判分"},
    "access_grants": []
  }'
```

> 创建接口会校验 `id` 只能为字母数字下划线并转为小写；源码中的 frontmatter 会被自动解析为 `meta.manifest`。

## 3. 测试样例

### 样例 1：章节随机抽题

**自然语言触发**：从第 3 章随机抽 3 道选择题，先不要给答案。

模型调用工具：`ds_random_quiz(chapter="第3章", question_count=3, question_type="choice")`

工具返回（JSON）：

```json
{
  "ok": true,
  "data": {
    "chapter": "第3章 栈、队列和数组",
    "question_count": 3,
    "questions": [
      {"id": "ch03_001", "type": "choice", "difficulty": "easy", "stem": "栈的特点是（　）。", "options": ["A. 先进先出", "B. 后进先出", "C. 随机存取", "D. 只允许在一端进、另一端出"]},
      {"id": "ch03_002", "type": "choice", "difficulty": "medium", "stem": "循环队列队满条件……", "options": ["A. front==rear", "B. (rear+1)%maxSize==front", "C. rear==front+1", "D. (rear-1)%maxSize==front"]},
      {"id": "ch03_003", "type": "choice", "difficulty": "easy", "stem": "……", "options": ["……"]}
    ]
  }
}
```

### 样例 2：客观题自动判分

**自然语言触发**：帮我判分，我的答案是 B、B、对。

模型调用工具：`ds_grade_quiz(questions='<样例1返回的 questions JSON>', answers='["B","B","对"]')`

工具返回（JSON）：

```json
{
  "ok": true,
  "data": {
    "total": 3,
    "correct_count": 3,
    "wrong_count": 0,
    "score": 100.0,
    "results": [
      {"index": 1, "question_id": "ch03_001", "user_answer": "B", "correct_answer": "B", "correct": true, "graded": true, "explanation": "栈是只允许在一端插入删除的线性表，后进先出（LIFO）。"},
      {"index": 2, "question_id": "ch03_002", "user_answer": "B", "correct_answer": "B", "correct": true, "graded": true, "explanation": "……"},
      {"index": 3, "question_id": "ch03_003", "user_answer": "对", "correct_answer": "对", "correct": true, "graded": true, "explanation": "……"}
    ]
  }
}
```

### 样例 3：错误输入（异常处理）

**自然语言触发**：从「操作系统」章节抽 3 道题。

工具返回：

```json
{"ok": false, "error": {"code": "INVALID_CHAPTER", "message": "未找到该章节。请使用“第1章~第8章”、数字 1~8、或章节主题词（如“栈”“二叉树”“排序”）。"}}
```

## 4. 本地测试结果

运行 `python docs/tools/test_ds_quiz_tool.py`，共 18 个用例全部通过：

```text
Ran 18 tests in 0.003s
OK
```

覆盖点：章节解析（数字/中文/主题词/非法）、抽题（题型过滤/难度过滤/数量钳制/附答案）、判分（全对/全错/部分对/数量不匹配/非法 JSON/按题干匹配/大小写归一）。

## 5. 与测试负责人的衔接

- 工具调用类测试用例可直接复用第 3 节样例。
- 判分结果含每题 `correct`、`correct_answer`、`explanation`，便于自动判分与人工复核。
- 工具返回统一采用 `{"ok": ..., "data": ...}` / `{"ok": false, "error": {...}}` 结构，与 `docs/interface-agreement.md` 第 7 节一致。
