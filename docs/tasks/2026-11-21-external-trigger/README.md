# 任务卡：本机 launchd 定时触发主赛/MiniBench 工作流

- 派出：2026-11-21，Claude Code
- 仓库：/Users/tomxiao/Code/metac-bot-template
- 工作树：/Users/tomxiao/Code/metac-bot-template/.worktrees/external-trigger
- 分支：task/external-trigger（基于 main，起点提交 c0a5020）
- 集成目标：fork 的 main，经 PR，由 Tom 批准
- Codex 线程：派出后由任务会话回填

整张卡不超过 12 KB，不贴源码和日志：引用文件路径和符号名，Codex 自己读工作树。
最多两轮；第二轮仍不通过就拆卡或交 Tom。

## 目标

FutureEval 主赛和 MiniBench 的题每题只开 3 小时。工作流 “Forecast on new AI tournament questions”
（`.github/workflows/run_bot_on_tournament.yaml`，GitHub id 421273160，fork `TomXiaoYZ/metac-bot-template`）
设定每 20 分钟跑一次，但 GitHub 实际 5–9 小时才触发一次（CC 2026-11-21 用 `gh run list` 核对：11-17 至 11-21 共 12 次 schedule 运行，间隔 4.8–9 小时），多数题漏答。
Tom 2026-11-21 批准改用外部定时器：本机 launchd 每 20 分钟用 `gh workflow run` 触发这个工作流的 `workflow_dispatch`。
gh 已在本机 Keychain 登录，不新增任何凭据。GitHub 自带的 schedule 保留作备份（工作流有 `concurrency` 串行、主赛模式跳过已预测的题，所以两者叠加不会重复提交）。

这张卡只做仓库里的三个脚本和测试；安装、启用、观察运行由 CC 在验收后做。Market Pulse 工作流不在本卡范围。

## 授权

- 网络：否
- 额外可写目录：无
- MCP：关
- 模型：默认
- 强度：默认

## 输入清单

| 文件或数据 | 绝对路径 | 在工作树里？ | 用途 |
| --- | --- | --- | --- |
| 主赛工作流 | /Users/tomxiao/Code/metac-bot-template/.worktrees/external-trigger/.github/workflows/run_bot_on_tournament.yaml | 是 | 只读：确认有 `workflow_dispatch` 和 `concurrency` |
| 已有 launchd 范例 | /Users/tomxiao/Library/LaunchAgents/com.tom.workspace-hygiene.plist | 否（只读参考） | plist 写法（PATH、HOME 环境变量、日志路径） |
| 交接文档 | /Users/tomxiao/Code/metac-bot-template/.worktrees/external-trigger/docs/handoff/2026-11-17-codex-handoff.md | 是 | 背景 |

## 人工前置条件

无。gh 已登录（Keychain），Codex 不需要也不能调用真实 gh。

## 用户路径

CC 在验收后运行 `scripts/launchd/install.sh`：它把触发脚本复制到 `~/.local/libexec/metac-bot-trigger/trigger_tournament.sh`，
生成 `~/Library/LaunchAgents/com.tom.metac-tournament-trigger.plist`（`StartInterval` 1200 秒、`RunAtLoad` true），并 `launchctl bootstrap gui/$(id -u)` 加载。
之后每 20 分钟：触发脚本先查这个工作流有没有 `queued` 或 `in_progress` 的运行，有就只记一行“跳过”；没有就 `gh workflow run` 触发一次，记一行“已触发”。
日志在 `~/Library/Logs/metac-bot-trigger.log`，每次运行后只保留最后 2000 行（约 4 周）。
卸载：`scripts/launchd/uninstall.sh`，`launchctl bootout`、删 plist、删 `~/.local/libexec/metac-bot-trigger/`；日志文件保留。

## 验收标准

1. 新增 `scripts/launchd/trigger_tournament.sh`（bash，`set -euo pipefail`）：
   - 仓库和工作流 id 写成脚本顶部常量 REPO、WORKFLOW_ID：`TomXiaoYZ/metac-bot-template`、`421273160`；所有 gh 调用都带 `-R REPO`（本机 gh 默认仓库指向上游 Metaculus，不带会 404）。
   - 先用 `gh run list -R REPO --workflow WORKFLOW_ID --status queued` 和 `--status in_progress`（`--json databaseId`，`--jq length` 或等价）判断是否有活动运行；有则写“跳过”行并退出 0。
   - 否则执行 `gh workflow run WORKFLOW_ID -R REPO --ref main`，写“已触发”行。
   - 每行日志以 UTC ISO 时间开头（`date -u +%Y-%m-%dT%H:%M:%SZ`）。日志路径取环境变量 `METAC_TRIGGER_LOG`，默认 `$HOME/Library/Logs/metac-bot-trigger.log`；写完后裁到最后 2000 行。
   - gh 失败时把错误写进日志并以非零退出（不重试）。不打印、不读取任何 token。
2. 新增 `scripts/launchd/install.sh`：复制触发脚本到 `$HOME/.local/libexec/metac-bot-trigger/` 并设可执行；生成 plist 到 `$HOME/Library/LaunchAgents/com.tom.metac-tournament-trigger.plist`
   （Label 同名，ProgramArguments 为 `/bin/bash` 加复制后的脚本路径，EnvironmentVariables 设 PATH=`/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin` 和 HOME，`StartInterval` 1200，`RunAtLoad` true，StandardOutPath/StandardErrorPath 指向 `$HOME/Library/Logs/metac-bot-trigger.launchd.log`）；
   已加载则先 `launchctl bootout` 再 `launchctl bootstrap gui/$(id -u) 生成的 plist 路径`。plist 里不出现任何 token。
3. 新增 `scripts/launchd/uninstall.sh`：`launchctl bootout gui/$(id -u)/com.tom.metac-tournament-trigger`（未加载时不报错），删 plist 和 `$HOME/.local/libexec/metac-bot-trigger/`，不删日志。
4. 三个脚本都能在 `HOME` 被改到临时目录、`PATH` 前置桩 `gh`/`launchctl` 的情况下运行，不碰真实 `~/Library`。
5. `python3 -m unittest tests/test_launchd_trigger.py -v` 全部通过（只用标准库）。
6. 不改其他文件：`.github/`、`main.py`、`pyproject.toml`、`uv.lock` 都不动。主检出工作区保持干净。

## 改动预算

- 源码新增上限：150 行
- 源码文件上限：3 个
- `scripts/launchd/trigger_tournament.sh`、`scripts/launchd/install.sh`、`scripts/launchd/uninstall.sh`
- 测试：`tests/test_launchd_trigger.py`，不超过 200 行

## 必须通过的新测试

测试用 `tempfile` 建假 HOME 和一个桩目录，桩 `gh`、`launchctl` 是写入调用参数到文件的小 bash 脚本，按环境变量决定 `gh run list` 返回的数量和 `gh workflow run` 的退出码；用 `subprocess` 运行被测脚本。

- `tests/test_launchd_trigger.py::test_dispatches_when_no_active_run`：活动运行为 0 时，桩记录里有 `workflow run 421273160 -R TomXiaoYZ/metac-bot-template --ref main`，日志最后一行含“已触发”，退出码 0。
- `tests/test_launchd_trigger.py::test_skips_when_run_active`：queued 或 in_progress 返回 1 时，不调用 `workflow run`，日志含“跳过”，退出码 0。
- `tests/test_launchd_trigger.py::test_all_gh_calls_pin_repo`：每次 gh 调用参数都含 `-R TomXiaoYZ/metac-bot-template`。
- `tests/test_launchd_trigger.py::test_dispatch_failure_exits_nonzero`：`gh workflow run` 桩退出 1 时，脚本非零退出，日志有错误行。
- `tests/test_launchd_trigger.py::test_log_trimmed_to_2000_lines`：预先写 2500 行日志，运行后日志恰好 2000 行且最后一行是本次记录。
- `tests/test_launchd_trigger.py::test_install_writes_plist_and_bootstraps`：plist 在假 HOME 下生成，`plutil -lint` 通过，`StartInterval` 为 1200，`RunAtLoad` 为 true，ProgramArguments 指向假 HOME 下复制的脚本；桩 launchctl 记录里有 `bootstrap gui/`。
- `tests/test_launchd_trigger.py::test_uninstall_removes_plist_and_script_keeps_log`：先 install 再 uninstall，plist 和 libexec 目录不存在，日志文件仍在，launchctl 记录里有 `bootout`。

## 编码要求

一条规则：**仓库内部的调用互相信任，失败就让它抛出来；只有下面列出的外部边界做校验，并照写的方式处理失败。**
缺数据、类型不对、路径不存在，直接报错即可，不兜底、不回退、不重试、不加配置开关。

- 校验边界：gh 命令的退出码；uninstall 时 `launchctl bootout` 在未加载情况下的非零退出（允许）。
- 失败处理：gh 失败 → 错误写日志，脚本非零退出，等下一次定时；不重试、不发通知。
- 拿不准某个防护要不要加：不加，列进回执的 `omitted_guards`，由 Claude Code 决定。
- 回合结束前有自检钩子跑 `diff_audit.py`：超预算、清单外文件、对不上边界的防护会被退回修改，最多两次。

## 边界

- 只在工作树 `/Users/tomxiao/Code/metac-bot-template/.worktrees/external-trigger` 内读写和执行 git；不碰主检出。
- 不 push、不改 `.github/`、不改部署/配置/凭据；不做破坏性 git 操作。
- 不运行真实的 `gh`、`launchctl`、`install.sh`；测试只用桩和临时 HOME。
- 不改 `main.py` 的预测逻辑，不加题目过滤；不动 Market Pulse 工作流和本机其他 launchd 任务。

- 保留策略：日志 `~/Library/Logs/metac-bot-trigger.log` 由触发脚本每次裁到 2000 行；`metac-bot-trigger.launchd.log` 只收 launchd 自身输出，由 uninstall 后手工删除（手册写明）。安装产物由 `uninstall.sh` 清除。
- 规格有矛盾或缺事实时停下：把**一个**具体问题写进回执的 `human_action`，附建议默认值，不自行改目标。

## 测试入口

- 相关测试：`python3 -m unittest tests/test_launchd_trigger.py -v`（只用标准库、桩命令、临时 HOME，不联网）。
- 本地验证：`bash -n scripts/launchd/*.sh`。

## 完成定义

到“工作树内文件改好、必须通过的新测试通过、回执写出”为止。不要执行 `git add`/`git commit`：提交由 Claude Code 验收后完成。
如实报告：没做完的标 blocked 并写明剩余；测试没跑的不写 pass；不为了避免提问而绕过限制。

## 回执格式

最后一条消息按以下结构写，不要省略字段：

```
status: done | blocked | failed
branch: task/external-trigger
changed_files:
  - 路径
tests_run:
  - 命令: pass | fail
budget: 源码 +行数 / 文件数 个文件（预算 150 / 3）
self_audit: 回合末自检通过 | 第 N 次后仍有 K 处，见 omitted_guards
omitted_guards:
  - 考虑过但没加的防护，或 none
human_action: 需要 Tom 决定的一个具体问题 + 建议默认值，或 none
blockers:
  - 阻塞项，没有写 none
next: 下一步或 none
```

## 轮次

### 第 1 轮

按本卡实现三个脚本和 `tests/test_launchd_trigger.py`。

**判决（第 1 轮）**

```
verdict: accept
final: false
thread: 01a1fd0c-0b1a-78f0-9b89-5ab7789d0284
receipt_status: done
self_audit: 回合末自检通过（diff_audit 基线 c0a5020，预算内，清单外文件 0，防御性代码命中 0）
budget: 源码 +85 行 / 3 个文件（预算 150/3）；测试 184/200 行
audit: 0 处防御性代码，其中 0 处无依据
checklist: 10/10
acceptance:
  - trigger 脚本常量/-R/queued+in_progress/跳过/已触发/UTC/裁剪2000: pass
  - install.sh plist 字段、bootout 再 bootstrap: pass
  - uninstall.sh 保留日志: pass
  - 假 HOME + 桩 PATH 运行: pass
  - unittest 8 项全过（含 7 项指定 + 1 项额外 list 失败）: pass
  - bash -n: pass；无 token 读取/打印: pass；仅新增 scripts/ 与 tests/: pass
main_checkout_clean: yes
human_action: none
```
备注：install.sh 用 `launchctl print` 判断是否已加载（卡写法允许）；unittest 在默认 Anaconda python 下同样通过。
