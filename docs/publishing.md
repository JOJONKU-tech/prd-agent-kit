# 安全发布PRD

## 发布前你会看到什么

Gate 2必须展示：

- PRD标题与内容版本；
- 发布平台、空间和目录；
- 新建、更新或新建版本；
- 最终文档标题；
- Renderer和Format Profile；
- Required/Preferred能力；
- 降级项；
- 上传Asset数量；
- 明确副作用；
- 本地预览；
- 发布后验收方式。

用户确认绑定`plan_sha256`。任何实质变化都会让确认失效。

## 第一次使用文档MCP

Agent会先生成Adapter提案，不会直接往正式目录写文档。用户授权后，在sandbox目录创建一份中性测试文档，验证写入和回读结构。通过后才能标`write_verified`。

## 新建与更新

```text
明确提供目标文档ID → 尝试读取并生成更新计划
未提供目标ID → 新建
目标无法读取 → 新建V2/V3，并重新确认
发现同名 → 不自动覆盖
```

## 发布失败怎么办

- API超时：先查状态，不能直接重试Create；
- 文档已创建但后续失败：保留链接，标`partial`；
- 不自动删除；
- 安全续跑时复用原`publish_id`和文档ID。

## 发布完成标准

接口返回成功不算完成。至少通过：

- MCP结构读取；或
- 浏览器只读检查。

都不可用时，需要用户打开文档确认。确认前状态是`published_unverified`。

## 本地验证

```bash
.venv/bin/python validators/validate_adapter.py adapter examples/document-adapters/feishu.yaml
.venv/bin/python validators/validate_adapter.py plan fixtures/publishing/publish-plan.yaml
.venv/bin/python validators/validate_adapter.py receipt fixtures/publishing/publication-receipt.yaml
```
