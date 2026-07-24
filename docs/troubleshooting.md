# Troubleshooting

## Agent没有读取入口

确认Agent从仓库根目录启动，并明确要求读取`AGENTS.md`。Claude Code通过`CLAUDE.md → @AGENTS.md`进入。

## 第一轮就开始写文件

这是错误行为。初始化第一轮只能索取资料；Gate 1确认前禁止写知识库。

## Router提示`always_read`超过3个

`always_read`只放每次都需要的高价值文件。把其余内容放进按关键词、请求类型或来源类型触发的Route。

## Router引用不存在或越界

所有路径必须位于知识库根目录内，且不能指向`raw/`、`templates/`或`skills/`等排除目录。修正路径后重新运行`validate_router.py`。

## 自定义Logic Kind失败

自定义Kind必须以`x-`开头，并在Format Profile的`custom_logic_kinds`中预注册。不要把拼写错误伪装成扩展。

## 高风险规则缺少来源

`field_source`、`validation`、`permission`、`metric_formula`、`default_value`、`data_migration`和`system_boundary`必须有`source_refs`。

## Required能力不支持

Required能力不足必须停止，不能静默降级。只有Preferred能力可降级，而且必须写入Render Manifest。

## Markdown表格失败

检查：

- 是否使用半角`|`；
- 每张连续表格内部列数是否一致；
- 每条需求是否包含Requirement标记；
- Render Manifest中的输入和输出Hash是否匹配。

## DOCX编号不正确

视觉上出现“1、2、3”不代表原生编号正确。运行：

```bash
.venv/bin/python validators/validate_docx_structure.py path/to/prd.docx
```

每个逻辑单元格必须使用独立`numId`并从1重新开始。DOCX也不能包含评论、修订或本机绝对路径。

## Block Plan层级不一致

Block Plan必须覆盖IR中的全部`logic_id`，不能重复，`depth`必须与IR树深度一致。

## Gate 2确认失效

Publish Plan任何实质变化都会改变`plan_sha256`。重新展示Gate 2并重新确认，不要复用旧Hash。

## 更新目标无法读取

不要覆盖同名文档。改为`create_new_version`，标题使用V2/V3并解释原因，然后重新Gate 2。

## 发布后是`published_unverified`

这不是失败伪装，而是尚未验收。使用MCP结构读取或浏览器只读检查；两者都不可用时请用户确认。

## MCP Tool名称不匹配

Adapter示例不是预配置集成。先读取当前MCP Tool Schema，生成映射提案，用户确认后再做只读和sandbox测试。

## Release Check命中私有词

公开仓库不保存私有黑名单。通过环境变量注入：

```bash
PRD_AGENT_KIT_EXTRA_FORBIDDEN_TERMS='term-one,term-two'   .venv/bin/python validators/release_check.py --run-tests
```

命中后同时检查当前文件、文件名和Git可达历史；不要只删工作区内容。
