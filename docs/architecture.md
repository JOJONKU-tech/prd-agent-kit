# prd-agent-kit 完整设计文档与实施清单

> 状态：V1 Implemented / Private Release Preparation；真实跨Agent E2E仍为`not_run`
> 日期：2026-07-24  
> License：MIT  
> 文档语言：中文主文档，精简英文入口；Schema字段使用英文

## 1. 项目定义

### 1.1 一句话定位

`prd-agent-kit`是一套Agent-native PRD知识工程协议：让Claude Code、Codex、Hermes等Agent读取仓库后，主动帮助用户建立业务知识库、学习团队PRD规范、生成业务专属Skill，并通过MCP发布格式正确、可验证的在线PRD。

### 1.2 核心问题

普通“PRD提示词”存在四个根本问题：

1. 每次都要重新解释业务背景、系统、术语和规则；
2. 模型会把历史PRD、格式模板和当前业务事实混在一起；
3. Markdown、DOCX和在线文档平台的结构能力不同，视觉相似不等于原生结构正确；
4. 在线文档接口返回成功，不代表标题、表格、图片和多级列表真正渲染正确。

本项目通过“知识库 + 业务Skill + 结构化PRD IR + Renderer Protocol + 发布确认门 + 发布后验收”解决上述问题。

### 1.3 目标用户

- 有大量业务资料和历史PRD、但每次都要重新给Agent讲背景的产品经理；
- 希望把团队PRD标准沉淀为Agent能力的产品团队；
- 已接入飞书或其他文档MCP，希望自动发布格式化在线PRD的人；
- 同时使用Claude Code、Codex、Hermes等Agent，希望知识与Skill不被某个平台锁死的人。

### 1.4 V1明确不做

- 不做单纯提示词合集；
- 不做PRD网页编辑器；
- 不做重型CLI；
- 不提供固定Markdown/DOCX/飞书Renderer代码；
- 不内置任何企业内部文档系统或私有业务适配；
- 不保存Token、Cookie、Header、Secret或临时签名URL；
- 不承诺“无资料一句话生成专业PRD”；
- 不提供删除在线文档、修改权限或分享文档能力；
- 不把未运行的兼容性测试宣传成“完全兼容”。

## 2. 已确认的产品决策

| 主题 | 决策 |
|---|---|
| 启动方式 | 克隆仓库后，让Agent阅读`AGENTS.md`并初始化PRD工作流 |
| 业务范围 | 行业通用，支持B端和C端；首发仅提供一个脱敏B端示例 |
| 素材策略 | 先读取用户资料和历史PRD，只追问缺口 |
| 知识库位置 | 初始化时指定，默认`~/prd-knowledge-base` |
| 原始资料 | 初始化时选择“仅引用路径/复制原文件”，默认仅引用 |
| 无资料用户 | 支持分阶段访谈，只建立最小知识库，不补假事实 |
| 标准模板缺失 | 使用内置中性模板并标记`provisional` |
| 知识库结构 | 一个知识库支持多个业务域，`domains/`隔离，`_shared/`复用 |
| 路由格式 | `router.yaml`是机器真源，`index.md`是人类导航 |
| 路由更新 | Agent提出变更建议，用户确认后更新 |
| 来源追踪 | 页级来源必填，高风险规则增加行级`source_id` |
| PRD IR | YAML实例 + JSON Schema；章节Block可扩展，Requirements严格建模 |
| Logic层级 | 使用`children`嵌套树，Renderer根据深度生成列表层级 |
| Logic标签 | 由`kind`映射，正文不手写标签 |
| 自定义Kind | 标准Kind + 预注册的`x-`扩展 |
| 未确认内容 | IR显式记录`status/open_questions/blocking` |
| 发布配置 | `prd-ir.yaml`与`publish-plan.yaml`完全分离 |
| 格式Profile | 支持多个Profile，并指定一个Default |
| 模板学习 | 先生成Observation报告，用户确认后生效 |
| 写作风格 | 可从历史PRD推断，但必须确认后生效 |
| 跨平台格式 | Required不满足则失败；Preferred允许降级并报告 |
| Renderer实现 | 不提供固定Renderer代码；保留协议、Schema、Fixtures和验证脚本 |
| Markdown | Portable模式为默认，富格式降级必须显式报告 |
| DOCX | 用户模板优先，中性Golden Template兜底 |
| 飞书 | 使用原生Blocks；表格为Preferred时可降级为需求卡片 |
| 输出目录 | 默认`~/prd-output/<document-id>/` |
| 发布确认 | Gate 2展示内容摘要、目标、能力、降级、副作用和预览 |
| 新建/更新 | 明确目标ID才更新；未指定则新建；同名不自动覆盖 |
| 更新读取失败 | 改为新建版本，并在Gate 2明确提示 |
| 版本命名 | 原标题、原标题 V2、原标题 V3自动递增 |
| MCP适配 | Agent生成能力映射提案，用户确认后保存并做沙箱测试 |
| MCP凭据 | 只留在Agent/MCP自身配置，不进入知识库 |
| 首次发布 | 必须通过用户授权的沙箱写入测试 |
| 发布后验收 | MCP结构读取或浏览器至少通过一种；否则要求用户确认 |
| 核心Skill | 仅维护一份Agent Skills公共格式源文件 |
| Skill安装 | 默认安装薄Wrapper；无法访问源文件时使用受管理副本 |
| 安装范围 | 默认用户级，可选项目级 |
| 同名Skill | 管理型Wrapper可更新；非管理Skill必须让用户选择 |
| 文档语言 | 中文主README + 精简英文README；Schema字段英文 |
| License | MIT |
| E2E | 首发只提供手测手册，不宣称已完成真实E2E |

## 3. 总体架构

```text
用户资料/历史PRD/标准模板
          ↓
Agent主动初始化与缺口访谈
          ↓
Gate 1：确认知识库写入内容
          ↓
业务知识库 + business-profile + prd-format-spec
          ↓
业务专属PRD Skill
          ↓
MRD/会议纪要/需求描述
          ↓
prd-ir.yaml
          ↓
Renderer Protocol
  ├── Portable Markdown
  ├── DOCX Native Lists
  └── Feishu Block Plan
          ↓
render-manifest.yaml
          ↓
Gate 2：确认发布目标、格式与副作用
          ↓
Generic Document MCP Publisher
          ↓
发布后结构/浏览器验收
          ↓
publication-receipt.yaml
```

### 3.1 分层边界

- Knowledge Layer：保存稳定业务知识、来源、模板和Skill；
- IR Layer：保存本次PRD的结构化内容；
- Renderer Layer：只把IR转换为本地文件或Block Plan，不调用MCP；
- Publisher Layer：只负责MCP写入，不修改PRD内容；
- Verification Layer：只负责结构与视觉验收，不修改文档。

## 4. 仓库规划

```text
prd-agent-kit/
├── AGENTS.md
├── CLAUDE.md
├── README.md
├── README.en.md
├── LICENSE
├── compatibility.yaml
│
├── docs/
│   ├── getting-started.md
│   ├── architecture.md
│   ├── llm-wiki.md
│   ├── knowledge-base-design.md
│   ├── knowledge-routing.md
│   ├── template-learning.md
│   ├── prd-ir.md
│   ├── renderer-protocols.md
│   ├── publishing.md
│   ├── security.md
│   ├── agent-compatibility/
│   │   ├── claude-code.md
│   │   ├── codex.md
│   │   └── hermes.md
│   └── testing/e2e/
│       ├── claude-code.md
│       ├── codex.md
│       └── hermes.md
│
├── protocols/
│   ├── onboarding.md
│   ├── source-priority.md
│   ├── confirmation-gates.md
│   ├── template-observation.md
│   ├── renderer-contract.md
│   └── generic-document-mcp.md
│
├── schemas/
│   ├── source-manifest.schema.json
│   ├── business-profile.schema.json
│   ├── router.schema.json
│   ├── prd-format-spec.schema.json
│   ├── prd-ir.schema.json
│   ├── render-manifest.schema.json
│   ├── document-adapter.schema.json
│   ├── publish-plan.schema.json
│   └── publication-receipt.schema.json
│
├── skills/
│   └── prd-knowledge-engineering/
│       ├── SKILL.md
│       └── references/
│           ├── onboarding.md
│           ├── knowledge-routing.md
│           ├── template-learning.md
│           ├── prd-ir.md
│           ├── rendering.md
│           └── publishing.md
│
├── platforms/
│   ├── claude/
│   │   ├── README.md
│   │   ├── wrapper-template.md
│   │   └── mcp-setup.md
│   ├── codex/
│   │   ├── README.md
│   │   ├── wrapper-template.md
│   │   ├── openai-yaml.example
│   │   └── mcp-setup.md
│   └── hermes/
│       ├── README.md
│       ├── wrapper-template.md
│       └── mcp-setup.md
│
├── templates/
│   ├── knowledge-base/
│   ├── format-profiles/
│   ├── wrappers/
│   └── golden/
│       ├── neutral-prd-template.docx
│       └── neutral-prd-template.manifest.yaml
│
├── fixtures/
│   ├── simple-prd/
│   ├── nested-logic/
│   ├── image-heavy/
│   └── incompatible-capabilities/
│
├── examples/
│   └── nova-event-admin/
│       ├── README.md
│       ├── source-materials/
│       ├── knowledge-base/
│       ├── generated-skill/
│       ├── prd-ir/
│       └── outputs/
│
├── validators/
│   ├── validate_prd_ir.py
│   ├── validate_markdown.py
│   ├── validate_docx_structure.py
│   ├── validate_block_plan.py
│   ├── validate_router.py
│   ├── validate_adapter.py
│   └── check_sensitive_content.py
│
└── tests/
    ├── schemas/
    ├── validators/
    ├── fixtures/
    └── sensitive-content/
```

## 5. Agent主动初始化协议

### 5.1 状态机

```text
S0 环境识别
S1 素材接收
S2 素材审计
S3 缺口访谈
S4 Gate 1确认
S5 建库与生成Skill
S6 初始化验收
```

### 5.2 第一轮固定对话

```text
我会先读取你现有的业务资料和历史PRD，再只追问真正缺失的信息。

请直接提供业务资料所在的文件、目录或在线文档链接；不用提前整理，我会自行分类。
```

第一轮禁止同时询问知识库路径、复制策略、模板、MCP和Agent类型。

### 5.3 素材审计分类

```text
business_overview
system_document
terminology
metric_definition
meeting_record
mrd
prd_sample
prd_template
image_asset
irrelevant
unknown
```

### 5.4 缺口访谈

- 先完整读取，再集中识别缺口；
- 每轮最多3个问题；
- 优先解决业务边界、角色、主链路、系统、字段来源和冲突；
- 问业务决策，不问技术实现；
- 用户不知道时允许回答`unknown`。

### 5.5 Gate 1

展示：

- 业务范围；
- 角色与主链路；
- 系统与页面；
- 术语、指标与规则；
- 已解决冲突；
- 保留未知项；
- 模板来源；
- 计划创建文件；
- Skill能力；
- 知识库路径；
- 原始资料处理方式。

只有用户明确确认后才写入知识库。

## 6. 用户知识库设计

```text
~/prd-knowledge-base/
├── _meta/
│   ├── SCHEMA.md
│   ├── config.yaml
│   ├── router.yaml
│   ├── index.md
│   ├── log.md
│   └── document-adapters/
├── _shared/
│   ├── index.md
│   ├── systems/
│   ├── concepts/
│   ├── processes/
│   ├── sop/
│   ├── standards/
│   ├── templates/
│   └── skills/
└── domains/
    └── <domain-slug>/
        ├── domain.yaml
        ├── index.md
        ├── sources/
        │   ├── manifest.yaml
        │   └── raw/
        ├── business/
        ├── systems/
        ├── concepts/
        ├── processes/
        ├── sop/
        ├── standards/
        ├── templates/
        └── skills/domain-prd/
```

### 6.1 路由

- `_meta/router.yaml`：选择业务域；
- `domains/<domain>/sop/router.yaml`：按需求读取最小必要知识；
- `always_read`最多3个文件；
- 默认禁止读取`sources/raw/`、`templates/`和`skills/`；
- 路由变更由Agent提出，用户确认后生效。

### 6.2 来源

- 每页Frontmatter必须包含页级`sources`；
- 字段来源、默认值、权限、指标公式、迁移和系统边界必须有行级`source_id`；
- 默认仅记录原路径/URL、哈希和读取时间；
- 用户授权后才复制原文件。

### 6.3 共享继承

- `_shared/standards`保存团队通用标准；
- 业务域标准通过`extends`继承并只写差异；
- Required规则只能显式移除，并记录理由与确认人。

## 7. PRD IR

### 7.1 形式

- 实例：YAML；
- 校验：JSON Schema Draft 2020-12；
- 文档章节：可扩展Blocks；
- 功能需求：严格Requirements结构；
- Logic：`children`嵌套树；
- 列表层级由Renderer计算；
- 发布配置不进入IR。

### 7.2 标准Logic Kind

```text
added_content
trigger
field_source
display_rule
interaction_rule
branch
validation
permission
boundary
metric_formula
default_value
data_migration
system_boundary
```

允许预注册`x-<slug>`扩展。

### 7.3 高风险约束

以下Kind必须自带`source_refs`：

```text
field_source
default_value
permission
metric_formula
validation
data_migration
system_boundary
```

### 7.4 未确认内容

- Requirement和Logic支持`confirmed/provisional/unknown/deprecated`；
- `open_questions`区分`blocking/non_blocking`；
- Blocking未解决时不得正式发布；
- 不把`〔待确认〕`混进正文冒充普通内容。

## 8. Format Profile与模板学习

### 8.1 Profile

- 支持多个Profile；
- 指定`default_profile`；
- Profile分为`content/writing/presentation/renderer_overrides`；
- 共享Profile可被业务域覆盖。

### 8.2 模板学习

```text
读取DOCX/Markdown/在线文档
→ 提取章节、表格、列表、图片和样式
→ 分离业务内容与格式
→ 生成template-observation
→ 标记事实、推断、冲突、未知和置信度
→ 用户确认
→ 写入Profile
→ 用中性Fixture回归渲染
```

### 8.3 Logic标签

IR只保存`kind`和正文；Profile将Kind映射为显示标签。Logic按场景`required_when`，不强制每个功能项输出全部标签。

### 8.4 跨平台能力

- Required不满足：停止；
- Preferred不满足：允许降级并写入Manifest；
- 禁止静默降级。

## 9. Renderer Protocol

仓库不提供固定Renderer代码。Agent按协议使用当前工具或临时脚本执行；临时脚本不进入仓库、知识库或用户桌面。

### 9.1 共同流程

```text
R0 输入校验
R1 Profile解析
R2 能力预检
R3 兼容性判断
R4 临时渲染
R5 结构验证
R6 视觉/平台验证
R7 生成render-manifest
```

### 9.2 Markdown

- 默认Portable模式；
- 半角表格分隔符；
- 多级列表降级必须报告；
- Profile要求原生列表时建议改用DOCX或飞书；
- Rich模式允许HTML，但必须标注兼容性范围。

### 9.3 DOCX

- 用户模板优先，中性Golden Template兜底；
- 逻辑项必须是独立Word原生编号段落；
- 每个逻辑单元格独立`numId`；
- 使用已验证的多级编号定义；
- 必须检查OOXML和视觉预览；
- 结构通过但视觉失败只能标`ready_for_review`。

### 9.4 飞书

- Renderer只生成Block Plan和Asset Upload Plan；
- Publisher在Gate 2后调用MCP；
- 表格内无法保留原生列表时：Table为Required则停止，Preferred则可降级为需求卡片；
- 发布后重新读取Blocks验收。

## 10. Gate 2与发布

### 10.1 Gate 2展示

- 内容摘要；
- 目标平台、空间和文档；
- 新建/更新/新建版本；
- Renderer和Profile；
- Required/Preferred能力；
- 降级清单；
- 上传图片数量；
- 副作用；
- 预览文件；
- 验收方式。

确认绑定`plan_sha256`。内容或目标变化后，原确认失效。

### 10.2 新建/更新

- 明确`document_id`才允许更新；
- 未指定则新建；
- 同名不自动覆盖；
- 更新目标读取失败时改为新建版本；
- 标题使用V2/V3递增；
- Gate 2必须明确提示操作变化。

### 10.3 发布状态

```text
planning
awaiting_confirmation
publishing
partial
published_unverified
published_verified
failed
```

### 10.4 验收

- MCP结构读取或浏览器验收至少通过一种；
- 都不可用时要求用户确认；
- 未验收只能标`published_unverified`；
- 所有发布生成`publication-receipt.yaml`。

## 11. Generic Document MCP

### 11.1 通用能力

```text
health_check
list_targets
search_documents
read_document
inspect_structure
create_document
update_document
import_document
upload_asset
get_operation_status
resolve_document_url
export_document
```

V1不含删除、移动、权限和分享能力。

### 11.2 Adapter

- 保存在`_meta/document-adapters/`；
- 只保存Tool名称、参数映射、输出映射和验证状态；
- 凭据保留在Agent/MCP自身配置；
- 陌生MCP由Agent生成映射提案；
- 用户确认后做只读测试；
- 正式发布前必须通过用户授权的沙箱写入测试。

### 11.3 幂等

- 每次发布有稳定`publish_id`；
- 调用超时先查任务状态和目标目录；
- 禁止直接重复Create；
- 部分失败保留文档链接，允许安全续跑；
- V1不自动删除失败文档。

## 12. 跨Agent兼容

### 12.1 根指令

- Codex：原生读取`AGENTS.md`；
- Hermes：原生读取`AGENTS.md`；
- Claude Code：根`CLAUDE.md`使用`@AGENTS.md`导入。

### 12.2 Skill

核心Skill仅使用Agent Skills公共字段。平台专有配置放Wrapper或旁路文件。

用户专属Skill唯一源文件保存在知识库。默认安装薄Wrapper；无法读取源路径时使用受管理副本并检查哈希。

### 12.3 默认用户级路径

- Claude：`~/.claude/skills/<name>/SKILL.md`；
- Codex：`~/.agents/skills/<name>/SKILL.md`；
- Hermes：当前Profile的`skills/<name>/SKILL.md`。

### 12.4 兼容声明

V1只宣称“Designed for”，不宣称E2E-verified：

```yaml
runtimes:
  claude-code:
    instruction_entry: designed
    skill_discovery: designed
    e2e: not_run
  codex:
    instruction_entry: designed
    skill_discovery: designed
    e2e: not_run
  hermes:
    instruction_entry: designed
    skill_discovery: designed
    e2e: not_run
```

## 13. LLM Wiki引用

只链接原始来源，不复制、不翻译全文：

- Andrej Karpathy, “LLM Wiki”  
  https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f

本项目只解释如何把该模式用于PRD知识工程：业务目录、来源、路由、模板、Skill、IR与在线文档发布。

## 14. Nova脱敏示例

示例名称：`Nova活动管理平台`。

必须从零虚构：

- 品牌；
- 系统；
- 字段；
- 页面；
- 截图；
- 业务数据；
- PRD文案。

示例完整覆盖：

```text
业务资料
→ 多域知识库
→ Knowledge Router
→ Format Profile
→ Domain Skill
→ PRD IR
→ Markdown
→ DOCX原生列表
→ Feishu Block Plan
→ Gate 2
→ Publication Receipt示例
```

严禁使用真实企业内部资料改名式脱敏。

## 15. 安全与隐私

### 15.1 禁止进入仓库

- 企业内部系统名；
- 企业内部文档平台名；
- 真实业务字段；
- 真实页面截图；
- 真实文档URL；
- 员工ID；
- Token、Cookie、Header、Secret；
- 临时签名URL；
- 真实客户或用户数据。

### 15.2 自动敏感检查

`check_sensitive_content.py`扫描：

- 预配置敏感词；
- Credential模式；
- 内部域名；
- 用户绝对路径；
- 临时签名参数；
- 图片Metadata；
- DOCX Core Properties、Comments和Revision信息。

## 16. V1验收标准

### 16.1 初始化

- Agent读取入口后第一轮只索取资料；
- 先读资料再问缺口；
- Gate 1前不写知识库；
- 无资料时只建最小知识库；
- 原始资料默认仅引用；
- Skill安装需要用户授权。

### 16.2 知识库

- 多业务域隔离；
- 共享标准可覆盖；
- 页级来源必填；
- 高风险规则有行级来源；
- Router只读最小必要文件；
- Router变更需确认。

### 16.3 IR与格式

- IR通过Schema与语义校验；
- Logic树最多3层；
- 标签不手写；
- 高风险Kind有来源；
- Blocking问题阻止发布；
- Profile支持多模板和继承。

### 16.4 渲染

- Markdown结构合法并报告降级；
- DOCX包含原生编号；
- Feishu使用Blocks或显式降级；
- Renderer不修改IR、不调用MCP；
- 每次输出Render Manifest。

### 16.5 发布

- Gate 2展示目标、格式、降级和副作用；
- 确认与Plan Hash绑定；
- 同名不自动覆盖；
- MCP首次发布前经过沙箱；
- 超时不重复创建；
- 发布后有真实验收；
- 每次发布有Receipt。

### 16.6 兼容与安全

- Claude、Codex、Hermes入口文件符合当前官方约定；
- 核心Skill只有一份；
- Wrapper不覆盖非管理Skill；
- 兼容状态如实标记`e2e:not_run`；
- 敏感扫描通过；
- 仓库中无真实企业内部信息。

## 17. 实施阶段

### Phase 0：设计冻结

**目标：** 将本设计文档转入仓库并锁定V1边界。

- [x] 用户确认本设计文档；
- [x] 确认GitHub仓库归属和可见性；
- [x] 确认默认分支；
- [x] 确认是否立即创建远程仓库；
- [x] 确认首发版本号`0.1.0`。

### Phase 1：仓库骨架

**创建：**

- `README.md`
- `README.en.md`
- `AGENTS.md`
- `CLAUDE.md`
- `LICENSE`
- `compatibility.yaml`
- 本文档落入`docs/architecture.md`
- 所有一级目录和空目录占位文件

**验收：**

- [x] `CLAUDE.md`正确导入`AGENTS.md`；
- [x] `AGENTS.md`小于约20KB；
- [x] README不宣称已完成E2E；
- [x] License为MIT；
- [x] 敏感扫描通过。

### Phase 2：初始化协议与核心Skill

**创建：**

- `protocols/onboarding.md`
- `protocols/source-priority.md`
- `protocols/confirmation-gates.md`
- `skills/prd-knowledge-engineering/SKILL.md`
- `templates/knowledge-base/`

**验收：**

- [x] 第一轮只索取资料；
- [x] Gate 1前禁止写盘；
- [x] 无资料模式不补假事实；
- [x] 核心Skill只用公共字段；
- [x] 引用文件路径全部存在。

### Phase 3：知识库Schema与Router

**创建：**

- `schemas/source-manifest.schema.json`
- `schemas/business-profile.schema.json`
- `schemas/router.schema.json`
- `templates/knowledge-base/_meta/`
- `templates/knowledge-base/_shared/`
- `templates/knowledge-base/domains/`
- `validators/validate_router.py`

**验收：**

- [x] Root Router和Domain Router样例通过Schema；
- [x] `always_read`超过3个时失败；
- [x] 指向不存在文件时失败；
- [x] 引用raw路径时失败；
- [x] 多业务域歧义会要求确认。

### Phase 4：PRD IR与Format Profile

**创建：**

- `schemas/prd-ir.schema.json`
- `schemas/prd-format-spec.schema.json`
- `protocols/template-observation.md`
- `docs/template-learning.md`
- `fixtures/simple-prd/`
- `fixtures/nested-logic/`
- `validators/validate_prd_ir.py`

**验收：**

- [x] 标准Kind通过；
- [x] 未注册`x-` Kind失败；
- [x] Logic超过3层失败；
- [x] 高风险Kind无来源失败；
- [x] Asset引用不存在失败；
- [x] Blocking问题阻止`confirmed`发布状态；
- [x] Profile继承可解析。

### Phase 5：Renderer Protocol与Golden Fixtures

**创建：**

- `protocols/renderer-contract.md`
- `docs/renderer-protocols.md`
- `templates/golden/neutral-prd-template.docx`
- `templates/golden/neutral-prd-template.manifest.yaml`
- `fixtures/image-heavy/`
- `fixtures/incompatible-capabilities/`
- Markdown、DOCX、Block Plan验证脚本

**验收：**

- [x] 不提供固定Renderer代码；
- [x] Markdown降级进入Manifest；
- [x] Golden DOCX具备原生多级编号；
- [x] 每个DOCX逻辑单元格可从1重新编号；
- [x] Block Plan层级与IR一致；
- [x] Required能力不足时验证失败。

### Phase 6：发布协议与MCP Adapter

**创建：**

- `protocols/generic-document-mcp.md`
- `schemas/document-adapter.schema.json`
- `schemas/publish-plan.schema.json`
- `schemas/publication-receipt.schema.json`
- `docs/publishing.md`
- 飞书公开适配示例
- 中性Generic Adapter示例

**验收：**

- [x] Adapter不包含凭据；
- [x] 不提供删除/权限/分享能力；
- [x] 未通过沙箱时不能正式发布；
- [x] Gate 2变化会使确认失效；
- [x] 更新读取失败转为V2/V3新建；
- [x] Receipt不保存临时签名URL。

### Phase 7：跨Agent入口

**创建：**

- `platforms/claude/`
- `platforms/codex/`
- `platforms/hermes/`
- `docs/agent-compatibility/`
- `docs/testing/e2e/`
- Wrapper模板与安装Manifest模板

**验收：**

- [x] Claude使用`CLAUDE.md → @AGENTS.md`；
- [x] Codex说明`AGENTS.md`与`.agents/skills`；
- [x] Hermes说明项目上下文和Profile Skill目录；
- [x] Wrapper可读取Canonical Skill；
- [x] 非管理同名Skill不会被覆盖；
- [x] Compatibility保持`e2e:not_run`。

### Phase 8：Nova示例

**创建：**

- 虚构业务资料；
- 虚构系统说明；
- 虚构标准PRD模板；
- 知识库成品；
- Domain Skill；
- PRD IR；
- Markdown示例；
- DOCX示例；
- Feishu Block Plan示例；
- Gate 1、Gate 2和Receipt示例。

**验收：**

- [x] 所有内容从零虚构；
- [x] 无真实企业或产品痕迹；
- [x] 完整链路可被Agent理解；
- [x] 敏感扫描通过；
- [x] 图片Metadata清理完成。

### Phase 9：文档与发布准备

**创建/完善：**

- 中文README；
- 精简英文README；
- Getting Started；
- LLM Wiki引用；
- Troubleshooting；
- Security；
- Contributing；
- Changelog。

**验收：**

- [x] 用户能仅凭`AGENTS.md`开始；
- [x] README不要求理解全部架构；
- [x] 英文README能解释项目和快速开始；
- [x] 所有链接有效；
- [x] 所有Schema示例通过；
- [x] 所有验证脚本通过；
- [x] Compatibility声明真实；
- [x] MIT License存在。

## 18. 建议提交顺序

```text
1. docs: add architecture and V1 scope
2. chore: initialize repository structure
3. feat: add onboarding protocol and core skill
4. feat: add knowledge-base schemas and routing
5. feat: add PRD IR and format profile schemas
6. feat: add renderer protocols and golden fixtures
7. feat: add publishing and generic MCP contract
8. feat: add agent compatibility adapters
9. docs: add Nova end-to-end example
10. docs: finalize bilingual guides and release checklist
```

## 19. 建仓库决策记录

1. GitHub仓库：`JOJONKU-tech/prd-agent-kit`；
2. 可见性：Private；
3. 发布方式：Private环境完成并通过敏感扫描；如需转Public，必须再次执行Release Checklist；
4. 默认分支：`main`；
5. 首发目标版本：`0.1.0`，尚未创建公开Tag/Release；
6. Issues、Discussions和Wiki以GitHub当前仓库设置为准，不在文档中虚构状态；
7. Phase 9启用CI自动执行Release Check和全量测试。

## 20. 参考来源

- Andrej Karpathy, LLM Wiki  
  https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- Claude Code Memory / CLAUDE.md  
  https://code.claude.com/docs/en/memory
- Claude Code Skills  
  https://code.claude.com/docs/en/skills
- OpenAI Codex AGENTS.md  
  https://developers.openai.com/codex/guides/agents-md
- OpenAI Codex Skills  
  https://developers.openai.com/codex/skills
- OpenAI Codex source  
  https://github.com/openai/codex
- Hermes Agent Context Files  
  https://hermes-agent.nousresearch.com/docs/user-guide/features/context-files
- Hermes Agent Skills  
  https://hermes-agent.nousresearch.com/docs/user-guide/features/skills

---

## 21. 结论

`prd-agent-kit`的核心价值不是“帮用户写一篇PRD”，而是把用户的业务知识、PRD标准和在线文档能力编译成可持续复用的Agent工作流。

V1必须坚持四条底线：

1. 先建知识，再生成文档；
2. 先结构化，再渲染；
3. 先确认，再发布；
4. 先验收，再声称完成。

设计冻结后，再创建仓库。不要一边建文件一边继续改根架构。