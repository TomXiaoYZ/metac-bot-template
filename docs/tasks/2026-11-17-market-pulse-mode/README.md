# 任务卡：新增 Market Pulse 运行模式和每日工作流

- 派出：2026-11-17，Claude Code
- 仓库：/Users/tomxiao/Code/metac-bot-template
- 工作树：/Users/tomxiao/Code/metac-bot-template/.worktrees/market-pulse-mode
- 分支：task/market-pulse-mode（基于 main，起点提交 fff2026）
- 集成目标：fork 的 main，经 PR，由 Tom 批准
- Codex 线程：派出后由任务会话回填

整张卡不超过 12 KB，不贴源码和日志：引用文件路径和符号名，Codex 自己读工作树。
最多两轮；第二轮仍不通过就拆卡或交 Tom。

## 目标

Tom 决定让现有机器人参加 Metaculus Market Pulse 26Q4（奖池 7,500 美元，12-21 是计奖最后一天；允许机器人账号领奖）。
这个比赛按每道子题关题时的最后一次预测计分，所以要每天重新预测一遍所有开放子题，不能跳过已经预测过的题。

forecasting-tools 0.3.7 的 `MetaculusClient.CURRENT_MARKET_PULSE_ID` 已经等于 `"market-pulse-26q4"`（CC 于 2026-11-17 从 0.3.7 wheel 的 `helpers/metaculus_client.py` 核对）。
模板对数值题和题组子题已经有支持，只需要加一个运行模式和一个工作流。

## 授权

- 网络：否
- 额外可写目录：无
- MCP：关
- 模型：默认
- 强度：默认

## 输入清单

| 文件或数据 | 绝对路径 | 在工作树里？ | 用途 |
| --- | --- | --- | --- |
| 主入口 | /Users/tomxiao/Code/metac-bot-template/.worktrees/market-pulse-mode/main.py | 是 | `__main__` 段：`argparse` 的 `--mode` choices、`run_mode` 的 `Literal`、`TOURNAMENT_URLS`、按 `run_mode` 分支的 `if/elif`（参照 `metaculus_cup` 分支） |
| 杯赛工作流 | /Users/tomxiao/Code/metac-bot-template/.worktrees/market-pulse-mode/.github/workflows/run_bot_on_metaculus_cup.yaml | 是 | 新工作流的复制模板 |
| 交接文档 | /Users/tomxiao/Code/metac-bot-template/.worktrees/market-pulse-mode/docs/handoff/2026-11-17-codex-handoff.md | 是 | 背景 |

## 人工前置条件

无。

## 用户路径

PR 合入 fork 的 main 之后，GitHub Actions 里会出现 “Forecast on Market Pulse” 工作流，每天 UTC 13:17 自动跑一次 `uv run python main.py --mode market_pulse`。
CC 先手动触发一次，确认日志里的赛事是 market-pulse-26q4，并且数值子题都提交了预测。

## 验收标准

1. `main.py` 的 `--mode` choices 和 `run_mode` 的 `Literal` 都新增 `"market_pulse"`，原有三个模式保持不变，默认值仍是 `tournament`。
2. 新增 `elif run_mode == "market_pulse":` 分支，写法和 `metaculus_cup` 分支一致：
   - 先设 `template_bot.skip_previously_forecasted_questions = False`；
   - 再调用 `template_bot.forecast_on_tournament(client.CURRENT_MARKET_PULSE_ID, return_exceptions=True)`；
   - 结果赋给 `forecast_reports`。
   - 分支上方加一行注释，说明 Market Pulse 按关题时的预测计分，所以每天要重新预测。
3. `TOURNAMENT_URLS` 新增 `"market_pulse": "https://www.metaculus.com/tournament/market-pulse-26q4/"`。
4. 新文件 `.github/workflows/run_bot_on_market_pulse.yaml`，和 `run_bot_on_metaculus_cup.yaml` 相比只有三处不同：
   - `name: Forecast on Market Pulse`；
   - cron 改为 `"17 13 * * *"`，行尾注释说明每天一次；
   - 运行命令改为 `uv run python main.py --mode market_pulse`。
5. `python3 -m py_compile main.py` 通过。新工作流用 `diff` 对比杯赛工作流，只有上面三处差异。
6. 不改其他文件：模型配置、`run_bot_on_tournament.yaml` 等都不动。主检出工作区保持干净。

## 改动预算

- 源码新增上限：60 行（含工作流 YAML 约 45 行）
- 源码文件上限：2 个
- `main.py`
- `.github/workflows/run_bot_on_market_pulse.yaml`（新增）

## 必须通过的新测试

无。理由：仓库没有单元测试入口（见交接文档第 3 节），这次只是按现有模式加一个分支；能验证的行为是编译通过、工作流和杯赛工作流的 diff 只有三处、合入后手动触发的运行日志。最后一项需要 secret 和真实提交，由 CC 在沙箱外做。

## 编码要求

一条规则：仓库内部调用互相信任，失败就抛出来；不加环境变量开关、回退赛事 ID 或校验。

- 校验边界：无
- 失败处理：无（沿用现有的 `return_exceptions=True`）
- 拿不准的地方：不做，写进回执的 `omitted_guards`。

## 边界

- 只在工作树内读写，不碰主检出。
- 不 push，不 fetch。不改 `pyproject.toml`、`uv.lock`、`bot_helpers.py`、`main_with_no_framework.py`、其他工作流文件。不读写密钥，不建 `.env`。
- 不跑 `main.py`、`uv sync`，也不跑任何会联网、调用模型或提交预测的命令。
- 保留策略：无。
- 规格有矛盾或缺事实时停下：在 `human_action` 里写一个具体问题，附建议默认值。

## 测试入口

- `python3 -m py_compile main.py`
- `diff .github/workflows/run_bot_on_metaculus_cup.yaml .github/workflows/run_bot_on_market_pulse.yaml`

## 完成定义

做到这里为止：两个文件改好、编译通过、diff 符合、回执写出。不要执行 `git add` 或 `git commit`，提交由 Claude Code 验收后完成。
如实报告：没做完的标 blocked，没跑的不写 pass。

## 回执格式

```
status: done | blocked | failed
branch: task/market-pulse-mode
changed_files:
  - main.py
  - .github/workflows/run_bot_on_market_pulse.yaml
tests_run:
  - python3 -m py_compile main.py: pass | fail
  - diff 杯赛工作流: 三处差异 | 其他
budget: 源码 +<行> / <文件数> 个文件（预算 60 / 2）
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

判决（第 1 轮，2026-11-17）：accept。线程 01a1e9b4-7e3a-77d1-a444-d4bc221549a1；回执 done，自检通过；预算 源码 +57 / 2 个文件；防御性代码 0 处；清单 7/7；py_compile 通过，工作流与杯赛 diff 仅三处；主检出未动。Actions 实跑待合入后由 CC 手动触发。
