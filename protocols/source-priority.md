# Source Priority Protocol

## 目标

将“业务事实来自哪里”和“PRD格式学谁”彻底分开。两套优先级不得混用，否则历史PRD会被误当成当前事实，业务文档又会被错误用于推断版式。

## 业务事实优先级

```text
用户当前明确确认
> 当前会议结论或MRD
> 当前业务知识页
> 当前系统说明
> 历史PRD
> Agent通用知识
```

### 使用规则

- 高优先级来源可以覆盖低优先级来源；
- 同级来源冲突时不得自行裁决，进入冲突清单；
- 历史PRD只能证明“过去这样写过”，不能自动证明当前仍生效；
- Agent通用知识只用于帮助提问，不得直接写成用户业务事实；
- 用户口头确认覆盖旧资料时，记录确认时间和被覆盖来源。

## 格式规范优先级

```text
用户明确指定的标准PRD
> 用户确认可代表当前团队规范的历史PRD
> 内置中性Golden Profile
```

### 使用规则

- 格式样本只学习章节、表格、列表、图片、文风和样式；
- 不复制样本中的业务字段、规则、系统名和页面名；
- 多个样本不一致时生成Observation报告，用户确认后才写入Profile；
- 使用中性Profile时必须标记`provisional`；
- 格式来源变化不自动修改业务事实。

## 两套来源不得混用

禁止以下行为：

- 因标准模板里出现某字段，就把该字段写进当前需求；
- 因当前业务说明没有四列表格，就改变团队格式规范；
- 因历史PRD写了默认值，就把默认值当成当前系统事实；
- 因当前用户偏好简洁，就删除Required格式能力。

业务内容与格式规范分别记录来源、状态和置信度。

## 冲突处理

### 冲突记录

每个冲突至少包含：

```yaml
conflict_id: CONFLICT-001
topic: ""
candidates:
  - value: ""
    source_id: SRC-001
    source_priority: current_system_document
  - value: ""
    source_id: SRC-002
    source_priority: historical_prd
resolution:
  status: open
  selected_value: null
  confirmed_by: null
  confirmed_at: null
```

### 自动处理边界

仅当高低优先级明确、且高优先级来源内容无歧义时，Agent可以提出采用高优先级来源的建议。以下情况必须询问用户：

- 两个当前来源冲突；
- 用户当前说法与当前系统说明冲突；
- 冲突会影响字段来源、权限、指标、默认值、迁移或系统边界；
- 无法确认来源时效性。

## 来源状态

```text
confirmed
provisional
unknown
deprecated
```

- `confirmed`：有当前来源或用户确认；
- `provisional`：暂按某来源处理，等待确认；
- `unknown`：没有足够信息；
- `deprecated`：已被新来源替代，但保留追溯。

## 高风险规则

以下内容除了页级来源，还必须有行级`source_id`：

```text
字段来源
默认值
权限
指标公式
校验
数据迁移
系统边界
```

没有来源时只能保留`unknown/provisional`，不得伪装成确定规则。

## 时效性

来源清单应记录：

- 原始路径或URL；
- 文件哈希；
- 读取时间；
- 文档自身更新时间（可获取时）；
- 适用业务域；
- 是否仍有效。

路径变化但哈希相同不视为业务变化；哈希变化后应重新审计受影响知识。