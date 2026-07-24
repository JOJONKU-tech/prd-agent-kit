# Renderer Contract

## 边界

Renderer只把已验证PRD IR转换为本地产物或Block Plan。Renderer不得：

- 修改IR；
- 补业务事实；
- 删除未知项；
- 调用在线发布MCP；
- 保存凭据；
- 把Preferred降级伪装成完整支持。

仓库不提供固定`render_markdown.py`、`render_docx.py`或`render_feishu.py`。Agent根据当前工具和目标平台执行协议，验证器负责机械验收。

## 阶段

```text
R0 输入校验
R1 Profile解析
R2 能力预检
R3 兼容性判断
R4 临时渲染
R5 结构验证
R6 视觉/平台验证
R7 生成Render Manifest
```

任一阶段失败都不得发布。

## 输入

- 已通过Schema与语义验证的`prd-ir.yaml`；
- 已解析继承的Format Profile；
- 可读取的Assets；
- 可选用户模板；
- 目标Renderer能力清单。

## Required与Preferred

- Required不支持：`status: failed`；
- Preferred不支持：允许降级，但必须在`degradations`记录feature、reason、action和severity；
- `unknown/unavailable`按不支持处理；
- 计划能力发生变化后，Gate 2确认失效。

## Markdown

默认Portable模式：

- 使用半角`|`；
- 表格列数一致；
- 每个Requirement带机器标记`<!-- requirement:REQ-ID -->`；
- 表格内Logic可用`<br>`展示，但Manifest必须报告原生列表降级；
- 本地图片路径必须存在；
- Rich模式可用HTML，但必须明确兼容范围。

## DOCX

优先级：

```text
用户指定模板
> Profile模板
> 中性Golden Template
> 停止高保真DOCX输出
```

硬规则：

- Logic Item是独立`w:p`；
- 每段有`w:numPr`；
- 深度0/1/2映射decimal/lowerLetter/lowerRoman；
- 每个逻辑单元格使用独立`w:numId`；
- 单元格首段从level 0开始；
- 必须验证ZIP、OOXML、编号引用和视觉预览；
- DOCX未通过视觉验证不能标`ready_for_publish`。

## Block Plan

Block Renderer只生成结构计划：

- 标题、段落、表格、列表和图片均为显式Block；
- 每个Logic Block记录`logic_id`和`depth`；
- Block顺序与IR一致；
- 表格能力不足且table为Preferred时可降级为需求卡片；
- table为Required时禁止降级；
- Asset上传由Publisher在Gate 2后执行。

## Render Manifest

每次渲染必须生成Manifest，记录：

- 输入路径与哈希；
- Renderer；
- Required/Preferred能力；
- 输出路径与哈希；
- 降级；
- Schema、结构和视觉检查；
- 最终状态。

Manifest变化会改变发布计划哈希。

## 临时实现

Agent可在系统临时目录创建一次性脚本。任务完成后不得把临时Renderer写入仓库、知识库、桌面或Skill目录。验证器和Fixtures是仓库的稳定资产。
