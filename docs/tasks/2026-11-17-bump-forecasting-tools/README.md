# 任务卡：把锁定的 forecasting-tools 从 0.3.5 升到 0.3.7

- 派出：2026-11-17，Claude Code
- 仓库：/Users/tomxiao/Code/metac-bot-template
- 工作树：/Users/tomxiao/Code/metac-bot-template/.worktrees/bump-forecasting-tools
- 分支：task/bump-forecasting-tools（基于 main，起点提交 bcbd016）
- 集成目标：fork 的 main，经 PR，由 Tom 批准
- Codex 线程：01a1e97b-0e36-7921-867a-d8c220a5cc7b

整张卡不超过 12 KB，不贴源码和日志：引用文件路径和符号名，Codex 自己读工作树。
最多两轮；第二轮仍不通过就拆卡或交 Tom。

## 目标

Tom 在 GitHub Actions 上手动跑 Test Bot（`.github/workflows/test_bot.yaml`，`uv sync --locked` 后跑 `main.py --mode test_questions`），
2026-11-17 的 run 44078957162 中 10 道测试题全部失败、0 预测提交。原因：`uv.lock` 锁定的 `forecasting-tools` 0.3.5 在只配置
`OPENROUTER_API_KEY` 时默认检索模型是 `openrouter/openai/gpt-4o-search-preview`，OpenRouter 已下线该模型。PyPI 上 0.3.6/0.3.7
（2026-11-08、2026-11-14 发布）的默认检索模型已改为 `openrouter/perplexity/sonar-pro`（CC 已从 PyPI wheel 源码核对过
`ForecastBot._llm_config_defaults`）。希望锁文件把 `forecasting-tools` 锁到 0.3.7，让 `uv sync --locked` 装到新版本。

## 授权

- 网络：是（仅用于 uv 从 PyPI 解析和下载包）
- 额外可写目录：无
- MCP：关
- 模型：默认
- 强度：默认

## 输入清单

| 文件或数据 | 绝对路径 | 在工作树里？ | 用途 |
| --- | --- | --- | --- |
| 锁文件 | /Users/tomxiao/Code/metac-bot-template/.worktrees/bump-forecasting-tools/uv.lock | 是 | 唯一要改的文件 |
| 项目配置 | /Users/tomxiao/Code/metac-bot-template/.worktrees/bump-forecasting-tools/pyproject.toml | 是 | 只读；`[tool.uv]` 的 7 天冷却对 forecasting-tools 已豁免 |
| 交接文档 | 分支 task/codex-handoff-20261117 的 docs/handoff/2026-11-17-codex-handoff.md | 否（用 `git show` 只读） | 背景，第 3、6 节 |

## 人工前置条件

无。（仓库 secret 已由 Tom 配好；Test Bot 重跑由 CC 在合入后做。）

## 用户路径

合入 fork 的 main 后，CC 手动触发 Test Bot；workflow 的 `uv sync --locked` 装到 forecasting-tools 0.3.7，
检索不再报模型下线错误，bot-testing-area 的测试题出现新的预测。

## 验收标准

1. `uv.lock` 中 `forecasting-tools` 的 version 为 `0.3.7`，sdist/wheel 来源为 PyPI。
2. 在工作树里 `uv lock --check` 通过（锁文件与 `pyproject.toml` 一致）。
3. 除 `forecasting-tools` 以及 0.3.7 的依赖约束强制要求变化的包之外，其他包的锁定版本不变；回执里列出所有版本变化的包和原因。
4. 只改 `uv.lock`，不改 `pyproject.toml` 或其他文件。
5. 主检出工作区干净；改动只在 `task/bump-forecasting-tools` 分支。

## 改动预算

只做这一个变化。锁文件是生成文件，不计源码行数。

- 源码新增上限：0 行
- 源码文件上限：0 个
- `uv.lock`（生成文件）

## 必须通过的新测试

无。理由：只是依赖锁升级，仓库没有单元测试入口（交接文档第 3 节）；可验证行为是 `uv lock --check`，
以及合入后的 Test Bot 线上冒烟（需要 secret 和真实提交，由 CC 在沙箱外做）。

## 编码要求

一条规则：只用 uv 自己生成锁文件，不手改 `uv.lock`。建议命令：`uv lock --upgrade-package forecasting-tools==0.3.7`。

- 校验边界：无
- 失败处理：解析失败或需要改 `pyproject.toml` 才能解析 → 停下，写进 blockers。
- 拿不准的：不做，写进回执。

## 边界

- 只在工作树内读写和执行命令；不碰主检出。
- 不 push、不 fetch、不改 `.github/`、`pyproject.toml`、`main.py`、`bot_helpers.py`；不读取或写入密钥值，不建 `.env`。
- 不跑 `main.py` 或任何会调用模型、提交预测的命令。
- 可以 `uv sync --locked` 验证能装上；产生的 `.venv/` 在回执前删掉（它被 .gitignore 忽略但占工作树空间）。
- 保留策略：无（uv 缓存在 ~/.cache/uv，属 uv 自身管理）。
- 规格有矛盾或缺事实时停下：把一个具体问题写进 `human_action`，附建议默认值。

## 测试入口

- `uv lock --check`
- 可选：`uv sync --locked` 后 `uv run python -c "import importlib.metadata as m; print(m.version('forecasting-tools'))"` 输出 0.3.7。

## 完成定义

到“`uv.lock` 改好、`uv lock --check` 通过、`.venv/` 已删、回执写出”为止。不要执行 `git add`/`git commit`：
提交由 Claude Code 验收后完成。如实报告：没做完的标 blocked；没跑的不写 pass。

## 回执格式

```
status: done | blocked | failed
branch: task/bump-forecasting-tools
changed_files:
  - uv.lock
tests_run:
  - uv lock --check: pass | fail
version_changes:
  - <包>: <旧> -> <新>（原因）
budget: 源码 +0 / 0 个文件（预算 0 / 0）
self_audit: <回合末自检通过 | …>
omitted_guards:
  - none
human_action: none
blockers:
  - none
next: none
```

## 轮次

### 第 1 轮

原始任务。

判决（验收）：accept，线程 01a1e97b-0e36-7921-867a-d8c220a5cc7b，回执 done。
- uv.lock 只有 forecasting-tools 0.3.5 -> 0.3.7（PyPI sdist/wheel）；其他包版本无变化；`uv lock --check` 实跑通过。
- 附带变化：uv 把锁格式 `revision` 3 -> 5（uv 自动，无包变化）。
- 预算 源码 +0 / 0 个文件；diff_audit 防御性代码 0 处；主检出 status 为空；无 .venv。
