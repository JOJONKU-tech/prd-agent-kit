# 学习团队PRD模板

## 先说结论

Agent不能看一篇历史PRD就宣布“已经学会团队规范”。正确流程是：提取Observation、给出证据和confidence、处理冲突、让用户确认，再更新Format Profile。

## 用户需要提供什么

优先级：

1. 明确指定的标准模板；
2. 能代表当前规范的历史PRD；
3. 没有模板时使用中性Profile，并标记`provisional`。

多篇样本比一篇更可靠，但样本越多不代表可以跳过冲突确认。

## Agent会观察什么

- 章节顺序；
- 功能需求表格列；
- Logic标签与层级；
- 图片位置；
- 标题、正文和表格样式；
- 写作语气；
- Required与Preferred能力。

Agent不会把样本中的业务字段、系统、默认值或权限复制到新PRD。

## Observation报告怎么看

每项观察都包含：

- Profile字段路径；
- `fact/inference/conflict/unknown`分类；
- 候选值；
- confidence；
- 来源；
- 证据。

`confidence: 1.0`只说明证据清晰，不代表已经获得用户确认。

## 用户确认后发生什么

1. 更新Format Profile；
2. 解析继承关系；
3. 检查自定义Logic Kind；
4. 用中性Fixture做回归；
5. Required能力不满足则拒绝生效；
6. Preferred能力降级则写入报告。

## Profile继承

共享Profile保存团队通用规范，业务域Profile通过`extends`只写差异。规则：

- Map深度合并；
- List由子Profile整体替换；
- 标量由子Profile覆盖；
- 循环继承直接失败；
- 父Profile不存在直接失败。

## 失败处理

以下情况保持旧Profile：

- 用户没有确认；
- 样本冲突未解决；
- 回归Fixture失败；
- Required能力丢失；
- 观察混入业务内容；
- Profile继承存在循环。

完整机器协议见`../protocols/template-observation.md`。
