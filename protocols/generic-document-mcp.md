# Generic Document MCP Protocol

## 目标

用语义能力映射不同文档MCP，而不是把某个Server的Tool名称写死在PRD工作流里。Adapter只保存Tool Schema映射和验证状态，凭据永远留在Agent或MCP自身配置。

## 安全边界

V1允许：

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

V1明确禁止：

```text
delete_document
move_document
change_permissions
share_document
```

禁止在Adapter、Publish Plan或Receipt保存Authorization、Cookie、password、secret、token、私钥、临时签名URL或Credential Header。

## Adapter发现

```text
列出MCP Tools
→ 读取Tool Schema
→ 匹配通用能力
→ 生成Adapter Proposal
→ 用户确认映射
→ 只读测试
→ 请求sandbox写入授权
→ 写入中性Fixture
→ 回读结构
→ 标记write_verified/structure_verified
```

不能因为Tool名字里含`create`就直接调用，必须核对参数和返回Schema。

## 验证状态

```text
discovered
mapped
read_verified
write_verified
structure_verified
broken
```

正式发布最低要求是`write_verified`。自动结构验收要求`structure_verified`。

## sandbox规则

- 首次正式发布前必须得到用户单独授权；
- 使用中性Fixture，不上传真实业务资料；
- 优先复用同一sandbox文档；
- 不测试删除、权限、分享或外部公开；
- Adapter只有在记录测试文档和验证时间后才能标`write_verified`；
- sandbox失败不得拿真实发布“顺便测试”。

## 发布策略

### block_native

创建文档、上传Asset、应用Block Plan、读取Blocks验收。

### file_import

上传本地文件、获取稳定导入引用、发起导入、轮询任务、读取文档验收。

### hybrid

仅在平台确实需要时使用；V1默认不推荐。

## 新建与更新

- 没有明确`document_id`时只能新建；
- 只有用户明确指定ID/URL时才能更新；
- 同名文档不自动覆盖；
- 更新目标无法读取时，操作改为`create_new_version`；
- 标题使用`V2/V3`递增；
- 操作变化后必须重新Gate 2。

## 幂等

每次发布有稳定`publish_id`和`query_before_retry`策略。超时后：

1. 查询Operation；
2. 查询目标目录；
3. 检查本地Receipt；
4. 仍无法判断则停止。

禁止超时后直接重复Create。

## 部分失败

文档已创建但Asset或Block写入失败时：

- 状态标`partial`；
- 保存文档ID和URL；
- 记录完成与失败步骤；
- 续跑复用同一文档；
- V1不自动删除失败文档。

## 发布后验收

MCP结构读取或浏览器只读验收至少通过一种。两者都不可用时请求用户确认，确认前保持`published_unverified`。
