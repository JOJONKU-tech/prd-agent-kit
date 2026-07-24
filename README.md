# prd-agent-kit

> 给你的 Agent 一本筑基宝典。让它从"通用对话框"进化成懂你业务、守你规矩、出错就报告的 PRD 搭档。

## 问题

你用 Claude Code / Codex / Hermes 写 PRD，大概率经历过这些：

- Agent 张嘴就问二十个问题，你不想答，它编答案；
- 它瞎编了一个"App 首页推荐流"，算法逻辑、展示规则全是自己脑补的；
- 上个月刚跟它说过"我们不用 A 工具，用 B 工具"，换了个会话它就忘了；
- 生成的文档格式跟团队规范完全不搭，研发看一眼就扔回来；
- 你以为它发布完成了，结果在线文档里列表全部变成手打编号，对齐已经歪到姥姥家。

**根本原因不是 Agent 不够聪明，是它没有你的业务记忆。**

通用大模型出厂时不认识你的公司、你的系统、你的术语、你的模板、你的发布流程。你每换一个会话、换一个 Agent、甚至换一个话题，它都得从头猜。

## 筑基

`prd-agent-kit` 做一件事：**在 Agent 写出第一个字之前，先把它的地基打好。**

```text
没有地基的 Agent                       筑基后的 Agent
─────────────────                    ─────────────────
"帮我写个邀请有礼的需求"               "帮我写个邀请有礼的需求"
    ↓                                    ↓
Agent: 什么是邀请有礼？               Agent: 已读取知识库"用户增长"，
      你们用的什么后台？                    基于现有增长体系，
      有模板吗？                            开始生成prd-ir.yaml。
      奖励规则怎么定？                      Gate 1：以下是计划摘要，
      ...（20个问题）                       请确认后继续。
```

这个过程分三层：

### 第一层：建知识库

Agent 读你的业务资料和历史 PRD，自己梳理出：

- 你们有哪些业务域、哪些系统、哪些页面
- 术语表（"邀请有礼"到底是啥、"用户分群"指什么）
- 每条知识的来源（谁说的、哪份文档、什么时候）
- 知识路由（Agent 在哪个场景该读哪个文件）

**Agent 不会再瞎编，因为知识库里有真东西可以查。**

### 第二层：学规矩

你们团队写 PRD 有固定套路——标题层级、表格格式、功能需求的写法、逻辑说明的结构。Agent 从你的模板和历史 PRD 里提取这些规则，生成 Format Profile，每次生成文档都按这个来。

**生成的 PRD 格式跟你们手写的一致，研发挑不出排版问题。**

### 第三层：守住门

知识写入前要确认（Gate 1），在线发布前要确认（Gate 2）。确认不是"你同意吗？"——确认绑定计划摘要，计划变了确认就失效。发布后必须做结构验收，不是接口返回 200 就算完。

**你不会再收到"已经发布了"结果打开一看是乱码。**

## 什么场景适合用

- **你的产品逻辑复杂**。功能多、规则多、状态多，每次让 Agent 从头理解想死。
- **你经常换 Agent 或开新会话**。今天 Claude Code、明天 Codex、后天 Hermes，知识库是共享的。
- **你有固定的 PRD 模板**。Agent 生成的文档格式总是不对，改格式比写内容还累。
- **你需要在多个平台发布 PRD**。同一份内容要出 Markdown（存档）、DOCX（导入在线文档）、飞书文档（协作），不想手写三遍。
- **你要审计追溯**。每条业务规则都知道来源，每个发布动作都有记录。

不管是 C 端 App、B 端后台还是内部工具，这套流程都适用。

## 怎么用

```bash
git clone https://github.com/JOJONKU-tech/prd-agent-kit.git
cd prd-agent-kit
```

然后对你的 Agent 说：

```text
读一下 AGENTS.md，帮我初始化 PRD 工作流。
```

剩下的 Agent 自己搞定：读你的资料 → 梳理知识库 → 学习模板 → 生成业务专属 Skill → 做好 Gate 确认 → 按规矩生成和发布 PRD。

具体步骤看 [Getting Started](docs/getting-started.md)。

Agent 第一步是读你给的业务资料，不是扔给你一张二十题问卷。

## 核心链路

```text
业务资料 + 历史PRD
  → 知识库 + 知识路由
  → PRD格式Profile
  → 业务专属Skill
  → prd-ir.yaml（结构化的PRD中间表示）
  → Markdown / DOCX / 飞书Block Plan（多格式渲染）
  → Gate 2确认
  → MCP发布 + 真实验收
```

## 内置了什么

- **协议**：初始化流程、来源优先级、确认门机制、模板学习方法
- **Schema**：知识路由、业务全景、PRD IR、Format Profile——全部 JSON Schema 校验
- **验证器**：路由完整性检查、PRD IR 语义校验、发布前安全检查
- **Golden Fixtures**：标准输入输出样例，你可以照着测你的 Agent 对不对
- **中立 DOCX 模板**：不绑任何公司的样式，Agent 可以直接拿来渲染
- **脱敏示例**：一份虚构的"Nova 活动管理平台"从 0 到 1 完整走通

## 设计原则

1. 先建知识，再写文档
2. 先结构化，再渲染
3. 先确认，再发布
4. 先验收，再说完成
5. 不编造任何系统、字段、指标、权限或默认值
6. 不在仓库或知识库里存任何凭据

## 开发验证

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/python validators/release_check.py --run-tests
```

## 文档索引

- [Getting Started](docs/getting-started.md)
- [完整架构](docs/architecture.md)
- [模板学习](docs/template-learning.md)
- [渲染器协议](docs/renderer-protocols.md)
- [发布与验收](docs/publishing.md)
- [排障](docs/troubleshooting.md)
- [发布检查清单](docs/release-checklist.md)
- [Nova 示例](examples/nova-event-admin/README.md)
- [英文简介](README.en.md)
- [Agent 入口](AGENTS.md)
- [兼容状态](compatibility.yaml)
- [Security](SECURITY.md)
- [Contributing](CONTRIBUTING.md)
- [Changelog](CHANGELOG.md)

## 借鉴来源

知识库组织方式借鉴 Andrej Karpathy 的 LLM Wiki 模式，只链接原文，不复制：

https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f

## V1 边界

V1 提供协议、Schema、Golden Fixtures 和验证器，不绑定特定渲染器实现。Agent 根据当前可用的工具按协议完成渲染，必须生成 Manifest 和验收结果。

## License

MIT
