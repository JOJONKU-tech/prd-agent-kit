# Cross-Agent Skill Installation Protocol

## 原则

业务专属Skill的Canonical源文件只保存在用户知识库。Agent目录安装的是薄Wrapper；只有运行时无法读取Canonical路径时，才允许使用`managed_copy`。

默认安装范围为用户级，用户可选择项目级。禁止同时向多个Agent目录乱写。

## 运行时路径

### Claude Code

- 用户级：`~/.claude/skills/<skill-name>/SKILL.md`
- 项目级：`<project>/.claude/skills/<skill-name>/SKILL.md`

### Codex

- 用户级：`~/.agents/skills/<skill-name>/SKILL.md`
- 项目级：`<project>/.agents/skills/<skill-name>/SKILL.md`
- `$CODEX_HOME/skills`仅作legacy兼容，不作为新安装默认路径。

### Hermes

- 用户级：`<active-profile>/skills/<skill-name>/SKILL.md`
- 项目工作流由根`AGENTS.md`加载，不假设统一的项目Skill目录。

## 安装步骤

```text
识别当前运行时
→ 选择user/project scope
→ 计算Canonical Skill sha256
→ 检查目标同名目录
→ 生成Wrapper
→ 写installation manifest
→ 新会话或reload验证
```

## Wrapper

Wrapper只负责：

1. 指向Canonical Skill；
2. 验证文件存在；
3. 完整读取Canonical Skill；
4. 遵守其Router与Format Profile；
5. 禁止未经确认修改知识库。

Wrapper不复制完整业务规则。

## 同名冲突

目录包含以下Manifest时，才视为本项目管理：

```yaml
managed_by: prd-agent-kit
```

- 管理型Wrapper：展示差异，用户确认后可更新；
- 非管理同名Skill：立即停止，让用户选择改名或替换；
- 禁止覆盖非管理Skill；
- 禁止仅凭目录名判断归属。

## managed_copy

Canonical路径不可访问时：

1. 请求用户确认降级；
2. 复制完整Skill；
3. 记录源`sha256`与副本`sha256`；
4. 每次使用前比较；
5. 不一致时提示同步；
6. 禁止静默使用过期副本；
7. 禁止覆盖用户手工修改。

## 验证

- Wrapper Frontmatter有效；
- Canonical路径存在；
- Canonical哈希与Manifest一致；
- 新会话能触发Skill；
- 非管理冲突未被覆盖；
- Manifest无凭据；
- 当前运行时路径正确。
