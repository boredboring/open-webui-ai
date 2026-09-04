"""
title: DS Quiz Tool
author: 组员B（扩展工具负责人）
version: 1.0.0
description: 数据结构课程练习题工具：按章节随机抽题 + 客观题自动判分
requirements:
"""

import json
import random
import re

# ---------------------------------------------------------------------------
# 章节映射
# ---------------------------------------------------------------------------

CHAPTERS = {
    "ch01": "第1章 绪论",
    "ch02": "第2章 线性表",
    "ch03": "第3章 栈、队列和数组",
    "ch04": "第4章 串",
    "ch05": "第5章 树与二叉树",
    "ch06": "第6章 图",
    "ch07": "第7章 查找",
    "ch08": "第8章 排序",
}

# 主题关键词 -> 章节 key（用于自然语言章节匹配，例如“栈”“二叉树”）
KEYWORDS = {
    "绪论": "ch01", "复杂度": "ch01", "时间复杂度": "ch01", "空间复杂度": "ch01",
    "线性表": "ch02", "顺序表": "ch02", "链表": "ch02",
    "栈": "ch03", "队列": "ch03", "数组": "ch03", "矩阵": "ch03",
    "串": "ch04", "KMP": "ch04", "kmp": "ch04", "模式匹配": "ch04",
    "树": "ch05", "二叉树": "ch05", "哈夫曼": "ch05", "线索": "ch05",
    "图": "ch06", "最短路径": "ch06", "拓扑": "ch06", "最小生成树": "ch06",
    "查找": "ch07", "散列": "ch07", "哈希": "ch07", "折半": "ch07", "二分": "ch07",
    "排序": "ch08", "堆排": "ch08", "快排": "ch08", "归并": "ch08", "基数": "ch08",
}


def resolve_chapter(text):
    """把用户输入的章节描述解析为 (chapter_key, chapter_name)，失败返回 (None, None)。"""
    t = str(text).strip()
    if not t:
        return None, None

    # 1) 精确匹配 chapter key
    if t in CHAPTERS:
        return t, CHAPTERS[t]

    # 2) 提取第一个数字（支持“第3章”“3”“chapter 3”等）
    m = re.search(r"(\d+)", t)
    if m:
        n = int(m.group(1))
        if 1 <= n <= 8:
            key = f"ch{n:02d}"
            return key, CHAPTERS[key]

    # 3) 主题关键词匹配（长的关键词优先，避免“二叉树”被“树”截胡）
    lower = t.lower()
    for kw in sorted(KEYWORDS.keys(), key=len, reverse=True):
        if kw in t or kw.lower() in lower:
            key = KEYWORDS[kw]
            return key, CHAPTERS[key]

    return None, None


# ---------------------------------------------------------------------------
# 题库（32 道客观题，覆盖 8 章；题型 choice/judge/fill）
# ---------------------------------------------------------------------------

QUESTION_BANK = [
    # ===== 第1章 绪论 =====
    {"id": "ch01_001", "chapter": "ch01", "type": "choice", "difficulty": "easy",
     "stem": "数据结构的三个要素是（　）。",
     "options": ["A. 数据元素、数据项、数据类型", "B. 逻辑结构、存储结构、数据的运算",
                 "C. 线性结构、树形结构、图形结构", "D. 顺序存储、链式存储、索引存储"],
     "answer": "B",
     "explanation": "数据结构研究的三要素是逻辑结构、存储（物理）结构，以及定义在结构上的数据运算。"},
    {"id": "ch01_002", "chapter": "ch01", "type": "choice", "difficulty": "medium",
     "stem": "某算法的时间复杂度为 O(n·logn)，下列说法正确的是（　）。",
     "options": ["A. 该算法实际执行 n·logn 次基本操作", "B. 当 n 足够大时，其增长阶介于 O(n) 与 O(n²) 之间",
                 "C. 该算法一定比 O(n) 的算法快", "D. 该算法的空间复杂度也一定是 O(n·logn)"],
     "answer": "B",
     "explanation": "大 O 记号描述的是增长阶（渐近上界），O(n·logn) 介于 O(n) 与 O(n²) 之间；它不是精确执行次数，也不代表空间复杂度。"},
    {"id": "ch01_003", "chapter": "ch01", "type": "judge", "difficulty": "easy",
     "stem": "数据元素是数据的基本单位，在计算机中通常作为一个整体进行考虑和处理。",
     "options": [],
     "answer": "对",
     "explanation": "数据元素是数据的基本单位；数据项是构成数据元素、不可分割的最小单位。"},
    {"id": "ch01_004", "chapter": "ch01", "type": "fill", "difficulty": "medium",
     "stem": "算法的五个重要特性是有穷性、确定性、可行性、输入和____。",
     "options": [],
     "answer": "输出",
     "explanation": "算法的五大特性：有穷性、确定性、可行性、输入、输出；算法可以没有输入，但至少要有一个输出。"},

    # ===== 第2章 线性表 =====
    {"id": "ch02_001", "chapter": "ch02", "type": "choice", "difficulty": "easy",
     "stem": "顺序存储结构的线性表，最主要的优点是（　）。",
     "options": ["A. 插入、删除方便", "B. 可以随机存取任一元素", "C. 存储密度低", "D. 不需要连续的存储空间"],
     "answer": "B",
     "explanation": "顺序表用数组连续存储，可按下标直接访问任意元素，即随机存取；其插入删除需移动大量元素，是主要缺点。"},
    {"id": "ch02_002", "chapter": "ch02", "type": "choice", "difficulty": "medium",
     "stem": "长度为 n 的顺序表，在第 i（1≤i≤n+1）个位置插入一个新元素，需要移动的元素个数是（　）。",
     "options": ["A. n-i", "B. n-i+1", "C. n-i-1", "D. i"],
     "answer": "B",
     "explanation": "在第 i 个位置插入，需要把第 i 到第 n 共 (n-i+1) 个元素依次后移一位，再放入新元素。"},
    {"id": "ch02_003", "chapter": "ch02", "type": "judge", "difficulty": "easy",
     "stem": "顺序存储的线性表支持随机存取，即访问任意元素的时间复杂度为 O(1)。",
     "options": [],
     "answer": "对",
     "explanation": "顺序表按下标直接定位，访问第 i 个元素时间复杂度为 O(1)，即随机存取。"},
    {"id": "ch02_004", "chapter": "ch02", "type": "fill", "difficulty": "medium",
     "stem": "在单链表中删除某个结点时，通常需要先找到该结点的____结点。",
     "options": [],
     "answer": "前驱",
     "explanation": "单链表结点只有指向后继的指针，删除结点需修改其前驱结点的 next 指针，因此要先定位前驱。"},

    # ===== 第3章 栈、队列和数组 =====
    {"id": "ch03_001", "chapter": "ch03", "type": "choice", "difficulty": "easy",
     "stem": "栈的特点是（　）。",
     "options": ["A. 先进先出", "B. 后进先出", "C. 随机存取", "D. 只允许在一端进、另一端出"],
     "answer": "B",
     "explanation": "栈是只允许在一端进行插入和删除的线性表，特点是后进先出（LIFO）。"},
    {"id": "ch03_002", "chapter": "ch03", "type": "choice", "difficulty": "medium",
     "stem": "用一维数组实现循环队列时，通常少用一个存储单元来区分队空与队满。若队头指针 front 指向队头元素、队尾指针 rear 指向队尾元素的下一个位置，则队满的条件是（　）。",
     "options": ["A. front == rear", "B. (rear+1) % maxSize == front", "C. rear == front+1", "D. (rear-1) % maxSize == front"],
     "answer": "B",
     "explanation": "牺牲一个单元区分队空队满：队空为 front==rear，队满为 (rear+1)%maxSize==front。"},
    {"id": "ch03_003", "chapter": "ch03", "type": "judge", "difficulty": "easy",
     "stem": "栈和队列都是操作受限的线性表。",
     "options": [],
     "answer": "对",
     "explanation": "栈和队列本质都是线性表，只是插入、删除操作的位置受到限制。"},
    {"id": "ch03_004", "chapter": "ch03", "type": "fill", "difficulty": "medium",
     "stem": "括号匹配、表达式求值和递归调用等场景，通常使用____这种数据结构来实现。",
     "options": [],
     "answer": "栈",
     "explanation": "栈的后进先出特性天然适合括号匹配、表达式求值以及函数递归调用时的现场保存与恢复。"},

    # ===== 第4章 串 =====
    {"id": "ch04_001", "chapter": "ch04", "type": "choice", "difficulty": "easy",
     "stem": "下列关于空串和空格串的说法，正确的是（　）。",
     "options": ["A. 空串的长度为 1", "B. 空格串的长度为 0", "C. 空串是不含任何字符的串，长度为 0", "D. 空串与空格串完全相同"],
     "answer": "C",
     "explanation": "空串不含任何字符、长度为 0；空格串由一个或多个空格组成、长度不为 0，二者不同。"},
    {"id": "ch04_002", "chapter": "ch04", "type": "choice", "difficulty": "medium",
     "stem": "KMP 算法相对于朴素模式匹配算法，最主要的改进是（　）。",
     "options": ["A. 主串指针 i 不回溯", "B. 模式串长度减半", "C. 不需要比较字符", "D. 使用链表存储主串"],
     "answer": "A",
     "explanation": "KMP 借助 next 数组，在失配时保持主串指针 i 不回退，只移动模式串指针 j，避免重复比较。"},
    {"id": "ch04_003", "chapter": "ch04", "type": "judge", "difficulty": "easy",
     "stem": "KMP 算法中，主串的匹配指针不会回溯。",
     "options": [],
     "answer": "对",
     "explanation": "KMP 的核心思想就是利用 next 数组使主串指针 i 只前进不后退。"},
    {"id": "ch04_004", "chapter": "ch04", "type": "fill", "difficulty": "medium",
     "stem": "KMP 算法中，next 数组记录的是：当模式串第 j 个字符与主串失配时，模式串应回退到的位置，其实质是模式串的最长相等____。",
     "options": [],
     "answer": "前后缀",
     "explanation": "next[j] 表示模式串子串 [0..j-1] 的最长相等前后缀长度，失配时据此跳过已匹配部分。"},

    # ===== 第5章 树与二叉树 =====
    {"id": "ch05_001", "chapter": "ch05", "type": "choice", "difficulty": "easy",
     "stem": "一棵二叉树的第 i（i≥1）层上最多有（　）个结点。",
     "options": ["A. 2^i", "B. 2^(i-1)", "C. 2^(i-1)-1", "D. 2^i-1"],
     "answer": "B",
     "explanation": "二叉树第 i 层结点数最多为 2^(i-1) 个（根为第 1 层）。"},
    {"id": "ch05_002", "chapter": "ch05", "type": "choice", "difficulty": "medium",
     "stem": "已知一棵完全二叉树共有 626 个结点，则叶子结点的个数为（　）。",
     "options": ["A. 311", "B. 312", "C. 313", "D. 314"],
     "answer": "C",
     "explanation": "完全二叉树中，n0=n2+1 且 n=n0+n1+n2，其中 n1 为 0 或 1；对偶数个结点 n1=1，解得 n0=313。"},
    {"id": "ch05_003", "chapter": "ch05", "type": "judge", "difficulty": "medium",
     "stem": "已知一棵二叉树的先序遍历序列和中序遍历序列，可以唯一确定这棵二叉树。",
     "options": [],
     "answer": "对",
     "explanation": "先序（或后序）+ 中序可唯一确定二叉树；但仅先序+后序不能唯一确定。"},
    {"id": "ch05_004", "chapter": "ch05", "type": "fill", "difficulty": "medium",
     "stem": "哈夫曼树的带权路径长度 WPL 定义为：所有叶子结点的____与其到根路径长度的乘积之和。",
     "options": [],
     "answer": "权值",
     "explanation": "WPL = Σ(叶子权值 × 该叶子到根的路径长度)，哈夫曼树是 WPL 最小的二叉树。"},

    # ===== 第6章 图 =====
    {"id": "ch06_001", "chapter": "ch06", "type": "choice", "difficulty": "easy",
     "stem": "具有 n 个顶点、e 条边的无向图，所有顶点的度数之和为（　）。",
     "options": ["A. n", "B. e", "C. 2e", "D. 2n"],
     "answer": "C",
     "explanation": "无向图中每条边连接两个顶点、贡献 2 个度，因此度数之和 = 2e。"},
    {"id": "ch06_002", "chapter": "ch06", "type": "choice", "difficulty": "medium",
     "stem": "Dijkstra 算法用于求解（　）。",
     "options": ["A. 单源最短路径（边权非负）", "B. 任意两点间的最短路径（含负权）", "C. 最小生成树", "D. 拓扑排序"],
     "answer": "A",
     "explanation": "Dijkstra 算法求单源最短路径，要求边权非负；含负权边时需用 Bellman-Ford，任意两点间可用 Floyd。"},
    {"id": "ch06_003", "chapter": "ch06", "type": "judge", "difficulty": "easy",
     "stem": "对连通图进行深度优先遍历（DFS）或广度优先遍历（BFS），可以访问到图中所有顶点。",
     "options": [],
     "answer": "对",
     "explanation": "连通图中任意两点连通，从任一顶点出发进行 DFS 或 BFS 均可遍历全部顶点。"},
    {"id": "ch06_004", "chapter": "ch06", "type": "fill", "difficulty": "medium",
     "stem": "一个连通无向图的生成树是包含图中全部顶点的极小连通子图，其中边权之和最小的生成树称为____。",
     "options": [],
     "answer": "最小生成树",
     "explanation": "边权之和最小的生成树即最小生成树（MST），可用 Prim 或 Kruskal 算法构造。"},

    # ===== 第7章 查找 =====
    {"id": "ch07_001", "chapter": "ch07", "type": "choice", "difficulty": "easy",
     "stem": "折半查找（二分查找）要求查找表必须是（　）。",
     "options": ["A. 顺序存储且有序", "B. 链式存储且有序", "C. 顺序存储但无序", "D. 任意存储结构"],
     "answer": "A",
     "explanation": "折半查找依赖随机存取并按中间元素比较来缩小区间，要求顺序存储且元素有序。"},
    {"id": "ch07_002", "chapter": "ch07", "type": "choice", "difficulty": "medium",
     "stem": "下列不属于散列表冲突处理方法的是（　）。",
     "options": ["A. 拉链法", "B. 开放定址法", "C. 再散列法", "D. 折半查找法"],
     "answer": "D",
     "explanation": "处理冲突常用拉链法、开放定址法、再散列法（建立公共溢出区）等；折半查找是查找方法，不是冲突处理方法。"},
    {"id": "ch07_003", "chapter": "ch07", "type": "judge", "difficulty": "easy",
     "stem": "对二叉排序树进行中序遍历，可以得到一个递增有序序列。",
     "options": [],
     "answer": "对",
     "explanation": "二叉排序树左<根<右，中序遍历（左-根-右）恰好输出递增序列。"},
    {"id": "ch07_004", "chapter": "ch07", "type": "fill", "difficulty": "medium",
     "stem": "衡量查找算法效率的主要指标是____查找长度（ASL）。",
     "options": [],
     "answer": "平均",
     "explanation": "平均查找长度 ASL = Σ(查找第 i 个记录的概率 × 查找该记录所需比较次数)，是评价查找效率的主要指标。"},

    # ===== 第8章 排序 =====
    {"id": "ch08_001", "chapter": "ch08", "type": "choice", "difficulty": "easy",
     "stem": "快速排序在最坏情况下的时间复杂度为（　）。",
     "options": ["A. O(n)", "B. O(n·logn)", "C. O(n²)", "D. O(logn)"],
     "answer": "C",
     "explanation": "当每次划分极不平衡（如序列基本有序）时，快速排序退化为 O(n²)；平均时间复杂度为 O(n·logn)。"},
    {"id": "ch08_002", "chapter": "ch08", "type": "choice", "difficulty": "medium",
     "stem": "下列排序算法中，属于稳定排序的是（　）。",
     "options": ["A. 快速排序", "B. 堆排序", "C. 归并排序", "D. 简单选择排序"],
     "answer": "C",
     "explanation": "归并排序、冒泡排序、直接插入排序是稳定的；快速排序、堆排序、简单选择排序、希尔排序不稳定。"},
    {"id": "ch08_003", "chapter": "ch08", "type": "judge", "difficulty": "easy",
     "stem": "归并排序是一种稳定的排序算法，其时间复杂度为 O(n·logn)。",
     "options": [],
     "answer": "对",
     "explanation": "归并排序在合并时保持相等元素的相对次序，是稳定排序，时间复杂度稳定为 O(n·logn)。"},
    {"id": "ch08_004", "chapter": "ch08", "type": "fill", "difficulty": "medium",
     "stem": "堆排序中，将无序序列构造成一个大根堆的过程称为____。",
     "options": [],
     "answer": "建堆",
     "explanation": "把无序数组调整为堆的过程叫建堆（初始化堆），堆排序先建堆再反复交换堆顶与末尾并向下调整。"},
]


# ---------------------------------------------------------------------------
# 辅助函数
# ---------------------------------------------------------------------------

def _to_bool(value):
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in ("true", "1", "yes", "是", "对", "y", "t")


def _normalize_fill(text):
    t = str(text).strip().lower()
    t = re.sub(r"[，。；、,.!！?？\s]", "", t)
    return t


def _normalize_judge(text):
    t = str(text).strip().lower()
    if t in ("对", "正确", "是", "t", "true", "√", "yes"):
        return "对"
    if t in ("错", "错误", "否", "f", "false", "×", "no"):
        return "错"
    return t


def _answers_match(user, correct, qtype):
    if qtype == "choice":
        return str(user).strip().upper() == str(correct).strip().upper()
    if qtype == "judge":
        return _normalize_judge(user) == _normalize_judge(correct)
    # fill：归一化后做包含匹配（双向，取较宽松的一侧）
    u = _normalize_fill(user)
    c = _normalize_fill(correct)
    if not u or not c:
        return False
    return u in c or c in u


class Tools:
    def __init__(self):
        self.bank = QUESTION_BANK

    def ds_random_quiz(
        self,
        chapter: str,
        question_count: int = 5,
        question_type: str = "choice",
        difficulty: str = "all",
        include_answer: bool = False,
    ) -> str:
        """
        按章节随机抽取数据结构客观题，用于自测或复习。默认只返回题目（不含答案），学生作答后可调用 ds_grade_quiz 判分。

        :param chapter: 章节，可用“第3章”“3”“ch03”或主题词（如“栈”“二叉树”“排序”）
        :param question_count: 抽题数量，默认 5
        :param question_type: 题型，可选 choice(选择)/judge(判断)/fill(填空)/all(全部)，默认 choice
        :param difficulty: 难度，可选 easy/medium/hard/all，默认 all
        :param include_answer: 是否在出题时直接附带答案与解析，默认 False（自测模式不泄露答案）
        """
        key, name = resolve_chapter(chapter)
        if key is None:
            return json.dumps(
                {
                    "ok": False,
                    "error": {
                        "code": "INVALID_CHAPTER",
                        "message": "未找到该章节。请使用“第1章~第8章”、数字 1~8、或章节主题词（如“栈”“二叉树”“排序”）。",
                    },
                },
                ensure_ascii=False,
            )

        include_answer = _to_bool(include_answer)

        pool = [q for q in self.bank if q["chapter"] == key]
        if question_type != "all":
            pool = [q for q in pool if q["type"] == question_type]
        if difficulty != "all":
            pool = [q for q in pool if q["difficulty"] == difficulty]

        if not pool:
            return json.dumps(
                {
                    "ok": False,
                    "error": {
                        "code": "NO_QUESTION",
                        "message": f"章节“{name}”中没有符合条件（题型={question_type}，难度={difficulty}）的题目。",
                    },
                },
                ensure_ascii=False,
            )

        count = int(question_count)
        if count <= 0:
            count = 1
        count = min(count, len(pool))
        selected = random.sample(pool, count)

        questions = []
        for q in selected:
            item = {
                "id": q["id"],
                "type": q["type"],
                "difficulty": q["difficulty"],
                "stem": q["stem"],
            }
            if q["type"] == "choice":
                item["options"] = q["options"]
            if include_answer:
                item["answer"] = q["answer"]
                item["explanation"] = q["explanation"]
            questions.append(item)

        return json.dumps(
            {
                "ok": True,
                "data": {
                    "chapter": name,
                    "question_count": count,
                    "questions": questions,
                    "note": "请逐题作答。判分时调用 ds_grade_quiz，把上面的 questions 原样传回，并按顺序给出答案数组。" if not include_answer else None,
                },
            },
            ensure_ascii=False,
        )

    def ds_grade_quiz(self, questions: str, answers: str) -> str:
        """
        对学生提交的客观题答案进行自动判分，并给出每题解析与总分。

        :param questions: 题目列表的 JSON 字符串（即 ds_random_quiz 返回的 data.questions 数组，每道题需含 id 或 stem）
        :param answers: 学生答案的 JSON 数组字符串，按题目顺序，例如 '["B","对","栈"]'
        """
        try:
            qs = json.loads(questions) if isinstance(questions, str) else questions
        except Exception:
            return json.dumps(
                {"ok": False, "error": {"code": "INVALID_QUESTIONS", "message": "questions 不是合法的 JSON 数组。"}},
                ensure_ascii=False,
            )
        if not isinstance(qs, list):
            return json.dumps(
                {"ok": False, "error": {"code": "INVALID_QUESTIONS", "message": "questions 必须是数组。"}},
                ensure_ascii=False,
            )

        try:
            ans = json.loads(answers) if isinstance(answers, str) else answers
        except Exception:
            # 容错：允许直接传单个答案字符串
            ans = [answers]
        if not isinstance(ans, list):
            ans = [ans]

        if len(qs) != len(ans):
            return json.dumps(
                {
                    "ok": False,
                    "error": {
                        "code": "LENGTH_MISMATCH",
                        "message": f"题目数量({len(qs)})与答案数量({len(ans)})不一致，请按题目顺序逐题给出答案。",
                    },
                },
                ensure_ascii=False,
            )

        results = []
        correct_count = 0
        for idx, (q, a) in enumerate(zip(qs, ans), start=1):
            qid = q.get("id") if isinstance(q, dict) else None
            qtype = q.get("type") if isinstance(q, dict) else "choice"
            stem = q.get("stem", "") if isinstance(q, dict) else str(q)

            target = None
            # 先按 id 从题库查找
            for item in self.bank:
                if item["id"] == qid:
                    target = item
                    break
            # 找不到 id 时按 stem 匹配
            if target is None and stem:
                for item in self.bank:
                    if item["stem"] == stem or item["stem"] in stem or stem in item["stem"]:
                        target = item
                        break

            if target is None:
                results.append({
                    "index": idx,
                    "question_id": qid,
                    "stem": stem,
                    "user_answer": a,
                    "correct": False,
                    "graded": False,
                    "message": "题库中未找到该题，无法判分。请确认题目来自本工具 ds_random_quiz 的返回结果。",
                })
                continue

            qtype = target["type"]
            is_correct = _answers_match(a, target["answer"], qtype)
            if is_correct:
                correct_count += 1
            results.append({
                "index": idx,
                "question_id": target["id"],
                "type": qtype,
                "stem": target["stem"],
                "user_answer": a,
                "correct_answer": target["answer"],
                "correct": is_correct,
                "graded": True,
                "explanation": target["explanation"],
            })

        total = len(qs)
        score = round(correct_count / total * 100, 1) if total else 0.0

        return json.dumps(
            {
                "ok": True,
                "data": {
                    "total": total,
                    "correct_count": correct_count,
                    "wrong_count": total - correct_count,
                    "score": score,
                    "results": results,
                },
            },
            ensure_ascii=False,
        )
