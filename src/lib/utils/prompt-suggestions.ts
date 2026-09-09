type PromptSuggestion = {
	id?: string;
	title?: string[];
	content: string;
};

type ModelLike = {
	id?: string;
	name?: string;
	info?: {
		meta?: {
			suggestion_prompts?: PromptSuggestion[] | null;
			description?: string | null;
		};
	};
};

// 课程 AI 助教专属建议（界面中文 / 英文）
const DS_ASSISTANT_SUGGESTIONS_ZH: PromptSuggestion[] = [
	{
		title: ['二叉树遍历怎么区分？', '先序 · 中序 · 后序'],
		content:
			'请用通俗易懂的方式讲解二叉树先序、中序、后序遍历的区别，并给一个简单例子帮助我理解。'
	},
	{
		title: ['时间复杂度是什么？', '面向初学者'],
		content:
			'我是初学者，请用直观的生活例子解释算法的时间复杂度，尽量少用术语。'
	},
	{
		title: ['帮我抽 3 道选择题', '第 3 章 栈与队列'],
		content:
			'请调用抽题工具，从第 3 章随机抽 3 道选择题，先不要附答案，我想自测。'
	},
	{
		title: ['KMP 的 next 数组怎么求？', '结合课程资料'],
		content:
			'请结合课程资料讲解 KMP 算法中 next 数组的含义与求法，并给出一个示例。'
	},
	{
		title: ['这道作业给我点提示', '先给思路，不直接写答案'],
		content:
			'这是一道数据结构作业题，请先帮我拆解题意并给出思路和关键提示，不要直接写出完整答案。'
	}
];

const DS_ASSISTANT_SUGGESTIONS_EN: PromptSuggestion[] = [
	{
		title: ['Binary tree traversal', 'preorder · inorder · postorder'],
		content:
			'Explain the difference between preorder, inorder and postorder traversal with a simple example.'
	},
	{
		title: ['What is time complexity?', 'beginner friendly'],
		content:
			'Explain algorithm time complexity with everyday examples and keep it simple for a beginner.'
	},
	{
		title: ['Give me 3 quiz questions', 'Chapter 3 stacks and queues'],
		content:
			'Use the quiz tool to draw 3 multiple-choice questions from Chapter 3 without answers for self-testing.'
	},
	{
		title: ['How is the KMP next array built?', 'use course materials'],
		content:
			'Explain the meaning and construction of the KMP next array with an example based on the course materials.'
	},
	{
		title: ['Help me start this assignment', 'hints only, no full answer'],
		content:
			'This is a data structures assignment. Break it down and give me the approach and key hints without writing the full answer.'
	}
];

const isZh = (language = '') => language.toLowerCase().startsWith('zh');

const isDSAssistantModel = (model?: ModelLike | null) => {
	if (!model) {
		return false;
	}
	const name = model.name ?? '';
	const description = model.info?.meta?.description ?? '';
	return model.id === 'ds-assistant' || name.includes('数据结构 AI 助教') || name.includes('数据结构');
};

// 后端 DEFAULT_PROMPT_SUGGESTIONS 的中文映射，仅用于识别默认建议
const DEFAULT_SUGGESTION_ZH: Record<string, PromptSuggestion> = {
	'Help me study': {
		title: ['帮我背单词', '为大学入学考试准备词汇'],
		content:
			'帮我学习词汇：写一个句子让我填空，我会试着选出正确的选项。'
	},
	'Give me ideas': {
		title: ['给我一些创意', '孩子的画作如何收纳'],
		content:
			'孩子的画作我不想扔掉又不好收纳，请给我 5 个有创意的处理方法。'
	},
	'Tell me a fun fact': {
		title: ['讲一个冷知识', '关于罗马帝国'],
		content: '给我讲一个关于罗马帝国的冷知识。'
	},
	'Show me a code snippet': {
		title: ['给我一段示例代码', '网页吸顶导航'],
		content: '用 CSS 和 JavaScript 写一个网页吸顶导航栏的示例代码。'
	},
	'Explain options trading': {
		title: ['解释期权交易', '我会买卖股票'],
		content:
			'用简单的话解释期权交易，假设我熟悉股票买卖但没接触过期权。'
	},
	'Overcome procrastination': {
		title: ['克服拖延', '给我一些建议'],
		content:
			'先问我最容易拖延的场景，再针对性地给我一些克服拖延的建议。'
	}
};

export const getEffectivePromptSuggestions = ({
	model,
	configured,
	fallback,
	language
}: {
	model?: ModelLike | null;
	configured?: PromptSuggestion[] | null;
	fallback?: PromptSuggestion[] | null;
	language?: string;
}): PromptSuggestion[] => {
	if (configured && configured.length > 0) {
		return configured;
	}

	if (isDSAssistantModel(model)) {
		return isZh(language) ? DS_ASSISTANT_SUGGESTIONS_ZH : DS_ASSISTANT_SUGGESTIONS_EN;
	}

	if (!isZh(language) || !fallback) {
		return fallback ?? [];
	}

	return fallback.map((item) => {
		const key = item.title?.[0] ?? '';
		const zhSuggestion = DEFAULT_SUGGESTION_ZH[key];
		if (zhSuggestion) {
			return { ...item, title: zhSuggestion.title, content: zhSuggestion.content };
		}
		return item;
	});
};
