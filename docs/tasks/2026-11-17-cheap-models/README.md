# 任务卡：主入口固定使用便宜模型

- 派出：2026-11-17，Claude Code
- 仓库：/Users/tomxiao/Code/metac-bot-template
- 工作树：/Users/tomxiao/Code/metac-bot-template/.worktrees/cheap-models
- 分支：task/cheap-models（基于 main，起点提交 8a6d24e）
- 集成目标：fork 的 main，经 PR，由 Tom 批准
- Codex 线程：派出后由任务会话回填

整张卡不超过 12 KB，不贴源码和日志：引用文件路径和符号名，Codex 自己读工作树。
最多两轮；第二轮仍不通过就拆卡或交 Tom。

## 目标

Tom 只配了 `OPENROUTER_API_KEY`。2026-11-17 的 Test Bot（run 44084367177）里，forecasting-tools 0.3.7 自动选的主模型是
`openrouter/anthropic/claude-opus-5.5`（OpenRouter 价每百万 token 输入 $4 / 输出 $20），检索是 `openrouter/perplexity/sonar-pro`（$3 / $15）。
10 题估算花了约 $1.33，还有 1 题因余额不足失败。Tom 决定换便宜模型。希望主入口 `main.py` 显式固定四个角色的模型：

| 角色 | 模型 | OpenRouter 价（输入/输出，每百万 token） |
| --- | --- | --- |
| default | `openrouter/anthropic/claude-haiku-5.5` | $0.10 / $0.50 |
| summarizer | `openrouter/anthropic/claude-haiku-5.5` | 同上 |
| researcher | `openrouter/perplexity/sonar` | $1 / $1 |
| parser | `openrouter/anthropic/claude-haiku-5.5` | 同上 |

（价格由 CC 于 2026-11-17 从 OpenRouter 公开模型列表核对；summarizer、parser 在上次运行里本来就是 haiku-5.5。）

## 授权

- 网络：否
- 额外可写目录：无
- MCP：关
- 模型：默认
- 强度：默认

## 输入清单

| 文件或数据 | 绝对路径 | 在工作树里？ | 用途 |
| --- | --- | --- | --- |
| 主入口 | /Users/tomxiao/Code/metac-bot-template/.worktrees/cheap-models/main.py | 是 | 唯一要改的文件；`__main__` 段里构造 `FallTemplateBot2026(...)` 处被注释掉的 `llms=` 示例块 |
| 交接文档 | /Users/tomxiao/Code/metac-bot-template/.worktrees/cheap-models/docs/handoff/2026-11-17-codex-handoff.md | 是 | 背景，第 6 节 |

## 人工前置条件

无。

## 用户路径

合入 fork 的 main 后，CC 手动触发 Test Bot；运行日志开头打印的 `*LLMs*` 配置里 default、summarizer、parser 为
`openrouter/anthropic/claude-haiku-5.5`，researcher 为 `openrouter/perplexity/sonar`；测试题照常提交预测，日志末尾的估算总花费明显低于 $1.33。

## 验收标准

1. `main.py` 中传给 `FallTemplateBot2026` 的 `llms` 为上表四个角色、四个模型字符串，逐字一致。
2. `default` 用 `GeneralLlm(...)` 写法，沿用原注释示例里的 `temperature=0.3`、`allowed_tries=2`；`timeout` 用 120（haiku 在 5 次并发预测下 40 秒偏紧，CC 定）。其余三个角色用字符串写法。
3. `python3 -m py_compile main.py` 通过。
4. 只改 `main.py`；把构造处上方那段“默认模型由 forecasting-tools 按环境变量选”的注释改成一句说明当前固定了便宜模型、原因是成本。不改其他参数（`predictions_per_research_report` 等不动）。
5. 主检出工作区干净；改动只在 `task/cheap-models` 分支。

## 改动预算

- 源码新增上限：30 行
- 源码文件上限：1 个
- `main.py`

## 必须通过的新测试

无。理由：仓库没有单元测试入口（交接文档第 3 节），这是纯配置改动；可验证行为是编译通过和合入后 Test Bot 日志里的 `*LLMs*` 配置与花费，后者需要 secret 和真实提交，由 CC 在沙箱外做。

## 编码要求

一条规则：仓库内部的调用互相信任，失败就让它抛出来；不加环境变量开关、不加回退模型、不加校验。

- 校验边界：无
- 失败处理：无
- 拿不准的：不做，写进回执 `omitted_guards`。

## 边界

- 只在工作树内读写；不碰主检出。
- 不 push、不 fetch、不改 `.github/`、`pyproject.toml`、`uv.lock`、`bot_helpers.py`、`main_with_no_framework.py`；不读写密钥，不建 `.env`。
- 不跑 `main.py`、`uv sync` 或任何会联网、调用模型、提交预测的命令。
- 保留策略：无。
- 规格有矛盾或缺事实时停下：把一个具体问题写进 `human_action`，附建议默认值。

## 测试入口

- `python3 -m py_compile main.py`

## 完成定义

到“`main.py` 改好、编译通过、回执写出”为止。不要执行 `git add`/`git commit`：提交由 Claude Code 验收后完成。
如实报告：没做完的标 blocked；没跑的不写 pass。

## 回执格式

```
status: done | blocked | failed
branch: task/cheap-models
changed_files:
  - main.py
tests_run:
  - python3 -m py_compile main.py: pass | fail
budget: 源码 +<行> / <文件数> 个文件（预算 30 / 1）
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
