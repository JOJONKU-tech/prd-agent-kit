# Release Checklist

V1发布前逐项执行。未完成的项目不能靠文案包装成“已完成”。

## Scope

- [ ] V1边界未扩张为网页编辑器、重型CLI或固定Renderer；
- [ ] 没有内置企业私有适配；
- [ ] Compatibility仍准确反映真实E2E状态；
- [ ] Changelog没有伪造未发布版本日期。

## Documentation

- [ ] 中文README和英文README入口可用；
- [ ] Getting Started可在不阅读完整架构的情况下执行；
- [ ] Troubleshooting覆盖真实错误；
- [ ] Security和Contributing存在；
- [ ] 所有本地Markdown链接有效；
- [ ] LLM Wiki只引用原始来源，不复制正文。

## Mechanical checks

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/python validators/release_check.py --run-tests
```

- [ ] 全量Unit Tests通过；
- [ ] Python编译检查通过；
- [ ] JSON Schema本身有效；
- [ ] YAML/JSON可解析；
- [ ] Source Manifest Hash匹配；
- [ ] Render Output Hash匹配；
- [ ] Golden DOCX Hash匹配；
- [ ] DOCX无评论、修订和本机路径；
- [ ] PNG无文本或EXIF Metadata；
- [ ] 不存在固定Renderer实现。

## Privacy and security

通过环境变量注入私有黑名单，不把词表提交到公开仓库：

```bash
PRD_AGENT_KIT_EXTRA_FORBIDDEN_TERMS='term-one,term-two'   .venv/bin/python validators/release_check.py --run-tests
```

- [ ] 当前文件内容和文件名0命中；
- [ ] 二进制可提取文本0命中；
- [ ] 所有可达Git历史0命中；
- [ ] 无凭据、签名URL或绝对用户目录；
- [ ] GitHub仓库可见性与README声明一致。

## Runtime claims

- [ ] Claude Code E2E未运行时保持`not_run`；
- [ ] Codex E2E未运行时保持`not_run`；
- [ ] Hermes E2E未运行时保持`not_run`；
- [ ] 手测完成后使用独立证据提交更新，不直接改成“完全兼容”。

## GitHub release

- [ ] CI在`main`和Pull Request上通过；
- [ ] 默认分支是`main`；
- [ ] License是MIT；
- [ ] Commit和远程SHA一致；
- [ ] 创建Tag前再次运行Release Check；
- [ ] 只有真实创建Tag/Release后，才把版本从`Unreleased`移入带日期章节。
