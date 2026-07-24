# Template Observation Protocol

## 目标

把用户提供的PRD样本转换为可确认的格式观察，而不是直接把某篇历史文档当成标准。Observation只描述证据、推断和冲突；用户确认后，结论才能进入Format Profile。

## 输入

支持：

- DOCX；
- Markdown；
- 可读取结构的在线文档；
- PDF或图片仅作为辅助视觉证据。

每个输入必须关联`source_id`。无法读取完整结构时要明确能力缺口，不得把截图观察包装成原生结构事实。

## 观察维度

### Content

- 章节名称与顺序；
- 必填和可选章节；
- 功能需求组织方式；
- 原型图与正文关系。

### Writing

- 语言；
- 语气；
- Logic标签；
- 规则句式；
- 未知项标记方式。

### Presentation

- 标题层级；
- 表格列；
- 列宽倾向；
- 原生列表层级；
- 图片位置与尺寸；
- 表头重复和分页行为。

### Capability

- 哪些结构是Required；
- 哪些结构是Preferred；
- 哪些结构只是某平台偶然表现。

## Observation分类

```text
fact
inference
conflict
unknown
```

- `fact`：可直接从结构或样式读取；
- `inference`：基于多个样本推断；
- `conflict`：样本之间不一致；
- `unknown`：当前工具无法确认。

## 输出结构

```yaml
observation_id: OBS-001
profile_candidate: feature-prd
sources:
  - SRC-TEMPLATE-001
observations:
  - path: presentation.requirements_table.columns
    classification: fact
    value:
      - sequence
      - module
      - prototype
      - logic
    confidence: 1.0
    source_refs:
      - SRC-TEMPLATE-001
    evidence: Four visible table headers.
  - path: writing.tone
    classification: inference
    value: concise
    confidence: 0.7
    source_refs:
      - SRC-TEMPLATE-001
    evidence: Requirement statements are consistently short.
conflicts: []
unknowns: []
```

`confidence`范围为0到1。置信度不是确认状态；即使是1.0，也必须经过用户确认才能写入Profile。

## 工作流

```text
读取样本
→ 提取结构与视觉证据
→ 分离业务内容和格式
→ 生成Observation报告
→ 标记fact/inference/conflict/unknown
→ 用户确认
→ 写入或更新Format Profile
→ 用中性Fixture回归验证
```

## 业务内容隔离

禁止从格式样本复制：

- 系统名；
- 字段名；
- 默认值；
- 权限；
- 指标；
- 页面逻辑；
- 真实图片内容。

只有Format Profile明确建模的格式属性可以进入观察报告。

## 用户确认

确认摘要至少展示：

- 将新增或修改的Profile字段；
- 每项来源与confidence；
- 冲突和采用理由；
- Required/Preferred变化；
- 可能影响的Renderer；
- 是否仍有unknown。

用户未确认时，Observation报告可以保存为草稿，但不得覆盖已生效Profile。

## 回归验证

确认后使用中性Fixture渲染，而不是原业务内容。验证：

- 章节完整；
- 表格列正确；
- Logic层级正确；
- 图片策略正确；
- Required能力未丢失；
- 平台降级被记录。

回归失败时保持旧Profile生效，新Observation标记为`rejected`或`needs_revision`。
