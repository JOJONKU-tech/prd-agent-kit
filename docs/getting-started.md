# Getting Started

你不需要先理解完整架构。准备资料，让Agent读入口文件即可。

## 1. 准备环境

需要：

- Git；
- Python 3.11或更高版本；
- Claude Code、Codex或Hermes中的任意一个；
- 你愿意提供给Agent读取的业务资料和历史PRD。

```bash
git clone https://github.com/JOJONKU-tech/prd-agent-kit.git
cd prd-agent-kit
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
```

## 2. 启动Agent

在仓库根目录启动Agent，然后发送：

```text
请阅读AGENTS.md，并初始化我的PRD工作流。
```

第一轮Agent只应该索取资料路径，不该直接建知识库，也不该发二十题问卷。

## 3. 提供资料

优先提供：

1. 业务说明或MRD；
2. 系统说明；
3. 会议纪要；
4. 历史PRD；
5. 团队标准PRD模板。

历史PRD和模板可证明格式，不自动证明当前业务事实。

## 4. 确认Gate 1

Agent读取资料后会展示：

- 业务域与角色；
- 系统和流程；
- 已确认规则；
- 来源、冲突与未知项；
- 即将写入的知识库文件。

只有你确认Gate 1后，Agent才能写知识库和Domain Skill。

## 5. 生成PRD

提供当前需求或会议纪要。Agent应先生成并验证`prd-ir.yaml`，再按Format Profile输出Markdown、DOCX或Native Block Plan。

本地验证：

```bash
.venv/bin/python validators/validate_prd_ir.py   path/to/prd-ir.yaml   --profile path/to/format-profile.yaml   --assets-root path/to/assets-root
```

## 6. 确认Gate 2

发布前必须展示：

- 内容摘要和版本；
- 目标平台与目录；
- 新建、更新或新建版本；
- Required/Preferred能力和降级；
- 图片数量；
- 明确副作用；
- 发布后验收方式。

Gate 2确认绑定Publish Plan Hash。Plan变化后必须重新确认。

## 7. 发布与验收

没有配置文档MCP时，停在本地产物即可。首次使用MCP必须先做用户授权的sandbox写入测试。

接口返回成功不算完成。至少通过MCP结构读取或浏览器只读检查；否则状态保持`published_unverified`。

## 8. 查看完整示例

从这里开始：

- [Nova端到端示例](../examples/nova-event-admin/README.md)
- [原型HTML](../examples/nova-event-admin/source-materials/prototype.html)
- [PRD IR](../examples/nova-event-admin/prd-ir/prd-ir.yaml)
- [DOCX产物](../examples/nova-event-admin/outputs/prd.docx)

## 9. 遇到问题

查看[排障文档](troubleshooting.md)。准备公开发布仓库时，运行：

```bash
.venv/bin/python validators/release_check.py --run-tests
```
