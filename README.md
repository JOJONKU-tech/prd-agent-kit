# prd-agent-kit

> 面向Claude Code、Codex与Hermes的Agent-native PRD知识工程工具包。

`prd-agent-kit`不是提示词合集。它让Agent先读取业务资料和历史PRD，帮助用户建立可追溯的业务知识库、学习团队PRD格式、生成业务专属Skill，再将结构化PRD渲染并发布到在线文档。

## 当前状态

- 版本阶段：`0.1.0`协议实现阶段
- 仓库状态：Private development
- License：MIT
- Claude Code / Codex / Hermes：Designed，尚未完成真实E2E验证

## 快速开始

```bash
git clone https://github.com/JOJONKU-tech/prd-agent-kit.git
cd prd-agent-kit
```

然后对Agent说：

```text
请阅读AGENTS.md，并初始化我的PRD工作流。
```

Agent的第一步应该是读取你提供的业务资料，而不是发一张二十题问卷。

## 核心链路

```text
业务资料与历史PRD
→ 知识库与知识路由
→ PRD格式Profile
→ 业务专属Skill
→ prd-ir.yaml
→ Markdown / DOCX / Feishu Block Plan
→ Gate 2发布确认
→ MCP发布与真实验收
```

## 设计原则

1. 先建知识，再生成文档；
2. 先结构化，再渲染；
3. 先确认，再发布；
4. 先验收，再声称完成；
5. 不编造系统、字段、指标、权限和默认值；
6. 不在仓库或知识库保存凭据。

## 文档

- [完整架构与实施计划](docs/architecture.md)
- [模板学习](docs/template-learning.md)
- [Renderer协议](docs/renderer-protocols.md)
- [安全发布](docs/publishing.md)
- [英文简介](README.en.md)
- [Agent入口](AGENTS.md)
- [兼容状态](compatibility.yaml)

## 开发验证

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python validators/validate_router.py \
  templates/knowledge-base/_meta/router.yaml \
  --kb-root templates/knowledge-base
.venv/bin/python validators/validate_prd_ir.py \
  fixtures/simple-prd/prd-ir.yaml \
  --profile fixtures/simple-prd/format-profile.yaml \
  --assets-root fixtures/simple-prd
```

## LLM Wiki来源

本项目借鉴Andrej Karpathy的LLM Wiki模式，只链接原始来源，不复制正文：

https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f

## V1边界

V1提供协议、Schema、Golden Fixtures和验证器，不提供固定Renderer实现。Agent根据当前工具按协议完成渲染，并必须生成Manifest和验收结果。

## License

MIT
