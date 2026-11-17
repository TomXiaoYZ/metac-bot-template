---
type: handoff
owner: tom
author: codex/desktop
updated: 2026-11-17
sources: ["docs/tasks/2026-11-17-codex-handoff/README.md", "README.md", "main.py", "main_with_no_framework.py", "bot_helpers.py", "pyproject.toml", "uv.lock", ".github/workflows/", "integrations/README.md", "git:metac-bot-template@bcbd016", "git:metac-bot-template@15d1034"]
confidence: verified
---

# Metaculus 预测机器人项目交接

本地 `main` 与已有 `upstream/main` 完全一致，目前没有 Tom 的业务代码改动；Claude Code 可以据此规划首次试跑，但应先核实锁定 SDK 的默认模型，再决定试跑范围与费用。本文是 2026-11-17 的离线交接快照：代码、命令和 Git 状态已读回，云端运行和模型可用性未核实。依据：[任务卡](../tasks/2026-11-17-codex-handoff/README.md)、第 4 节 Git 输出、第 6 节依赖核查。

## 1. 一句话定位

这是 Tom 从 Metaculus 官方模板 fork 的 FutureEval 预测机器人，供 Tom 试跑机器人预测赛，当前处于模板接手阶段，由 Claude Code 规划、拆卡、验收，Codex 按既定规格实现；“此前没有本地开发”来自任务卡陈述，当前 `main` 无上游差异由 Git 证实。出处：[任务卡第 9–14 行](../tasks/2026-11-17-codex-handoff/README.md#L9)、[README 第 1–10 行](../../README.md#L1)、第 4 节；fork 地址为 [TomXiaoYZ/metac-bot-template](https://github.com/TomXiaoYZ/metac-bot-template)，本次未联网验证远端。

## 2. 代码地图

| 文件或目录 | 职责与关键边界 | 出处 |
|---|---|---|
| `main.py` | 推荐入口；`FallTemplateBot2026(ForecastBot)` 实现研究及二元、多选、数值、日期、条件题预测；命令行分比赛、Cup、测试区三种模式。当前每题 1 份研究、每份研究 5 次预测，默认发布，报告不保存到本地目录。 | [main.py:48](../../main.py#L48)、[研究入口:131](../../main.py#L131)、[启动及配置:686–729](../../main.py#L686) |
| `main_with_no_framework.py` | 单文件参考实现，自己处理 HTTP、提示词、概率解析、CDF 和提交；没有 `--mode`，由顶部常量控制，直接调用 OpenAI；仍使用 `forecasting_tools` 的搜索入口，并非完全去除框架依赖。 | [导入与常量:15–98](../../main_with_no_framework.py#L15)、[LLM:249–269](../../main_with_no_framework.py#L249)、[搜索:323–353](../../main_with_no_framework.py#L323)、[入口:1624](../../main_with_no_framework.py#L1624) |
| `bot_helpers.py` | 检查必要环境变量，压低依赖日志，打印运行模式、预测链接及错误摘要；不承担预测算法。 | [bot_helpers.py:1–7](../../bot_helpers.py#L1)、[检查:58](../../bot_helpers.py#L58)、[摘要:96](../../bot_helpers.py#L96) |
| `integrations/` | 可选 LightningRod 新闻生成题目及评估示例；README 同时介绍 `metaculus-bot-review`，读取已发布报告做复盘。 | [integrations/README.md:5–54](../../integrations/README.md#L5)、[main_lightningrod_eval.py:56–100](../../integrations/main_lightningrod_eval.py#L56) |
| `.github/workflows/` | 三个预测 workflow，加一个可选复盘 workflow；触发条件与命令见第 3 节。定义存在不代表 fork 云端已经启用。 | [test_bot.yaml](../../.github/workflows/test_bot.yaml)、[run_bot_on_tournament.yaml](../../.github/workflows/run_bot_on_tournament.yaml)、[run_bot_on_metaculus_cup.yaml](../../.github/workflows/run_bot_on_metaculus_cup.yaml)、[review_bot.yaml](../../.github/workflows/review_bot.yaml) |
| `pyproject.toml` | Python `>=3.11,<3.14`；声明运行依赖、`integrations` 和 `dev` 依赖组；一般包设 7 天发布冷却期，`forecasting-tools` 豁免。 | [pyproject.toml:1–29](../../pyproject.toml#L1) |
| `uv.lock` | 可复现依赖锁定，含 Python 条件分支和包哈希；实际锁定 `forecasting-tools==0.3.5`，不同于 pyproject 中的允许范围 `>=0.2.90,<0.4.0`。 | [uv.lock:1–14](../../uv.lock#L1)、[uv.lock:583–612](../../uv.lock#L583)、[pyproject.toml:15](../../pyproject.toml#L15) |

`forecasting-tools` 的具体依赖面：

- 调度、拉题、聚合与发布走父类 `ForecastBot`；主入口调用 `forecast_on_tournament()`、`log_report_summary()`，并用 `MetaculusClient.CURRENT_AI_COMPETITION_ID`、`CURRENT_MINIBENCH_ID`、`CURRENT_METACULUS_CUP_ID` 定位比赛。源码也介绍自选题路径 `forecast_questions()`。[main.py:48–70](../../main.py#L48)、[main.py:743–778](../../main.py#L743)
- LLM 与研究走 `get_llm()`、`GeneralLlm`、`AskNewsSearcher.call_preconfigured_version()`、`SmartSearcher.invoke()`；结构化解析走 `structure_output()`、`clean_indents()`。[main.py:19–42](../../main.py#L19)、[main.py:131–189](../../main.py#L131)、[main.py:233–258](../../main.py#L233)
- 数据类型包括 `MetaculusQuestion` 及各题型、`ReasonedPrediction`、`BinaryPrediction`、`PredictedOptionList`、`NumericDistribution`、`Percentile`、`DatePercentile`、`ConditionalPrediction`、`PredictionAffirmed`；条件题还直接引用包内 `data_models.data_organizer.DataOrganizer`，摘要依赖 `ForecastReport`。[main.py:19–42](../../main.py#L19)、[main.py:621–665](../../main.py#L621)、[bot_helpers.py:106–111](../../bot_helpers.py#L106)
- 无框架版本仅在 Exa 研究路径显式使用 `forecasting_tools.ExaSearcher` / `SmartSearcher`，预测客户端是 `AsyncOpenAI()`。[main_with_no_framework.py:249–269](../../main_with_no_framework.py#L249)、[main_with_no_framework.py:323–353](../../main_with_no_framework.py#L323)

## 3. 怎么跑、怎么验

以下是仓库原有命令的摘录与用途说明，本交接未执行安装、预测或复盘。第 3 节仍由 Claude Code 按任务卡验收；任何联网试跑另行安排。当前卡明确禁止网络、安装依赖、运行 `main.py`、push、fetch、add、commit。[任务卡第 16–56 行](../tasks/2026-11-17-codex-handoff/README.md#L16)

### README 的命令

| 原文命令 | 用途、网络与密钥要求 | 出处 |
|---|---|---|
| `git clone https://github.com/Metaculus/metac-bot-template.git`；`cd metac-bot-template` | 克隆上游模板需网络；README 说明已 fork 时替换为 fork URL。当前已有工作树，无需重复克隆。 | [README:71–76](../../README.md#L71)、第 4 节 |
| `uv --version` | 本地确认 uv 可用，无需密钥或网络。 | [README:78–86](../../README.md#L78) |
| `uv sync` | 安装依赖、创建 `.venv`，缺少解释器时也可能下载 Python；缓存不足需网络，无服务密钥要求。 | [README:86–93](../../README.md#L86) |
| `cp .env.template .env` | README 的配置准备原文；只复制本地文件，不需网络。Tom 的凭据约定要求只留 Keychain，因此这里只记录原文，不照搬后续把真实密钥填入 `.env` 的做法。 | [README:95–100](../../README.md#L95)；本会话提供的 AGENTS.md“凭据只留在 Keychain” |
| `uv run python main.py --mode test_questions` | 测试区在线冒烟，会调用模型并发布真实预测；需要 `METACULUS_TOKEN` 和下述至少一种 LLM key。 | [README:102–107](../../README.md#L102)、[main.py:703–714](../../main.py#L703)、[main.py:767–775](../../main.py#L767) |
| `uv run python main.py --mode tournament` | 预测当季 AI 比赛及 MiniBench，默认跳过已有预测；需网络及同上密钥。 | [README:109–112](../../README.md#L109)、[main.py:716](../../main.py#L716)、[main.py:744–755](../../main.py#L744) |
| `uv run python main.py --mode metaculus_cup` | 预测 Cup，代码关闭“跳过已预测题”；需网络及同上密钥。 | [README:114–117](../../README.md#L114)、[main.py:756–765](../../main.py#L756) |
| `uv run python main_with_no_framework.py` | 默认投向 Fall 2026 AI 比赛并发布；需要 `METACULUS_TOKEN`、`OPENAI_API_KEY` 和网络，搜索凭据可选；不是 OpenRouter 两个 key 即可运行的等价替换。 | [README:119–123](../../README.md#L119)、[常量:52–91](../../main_with_no_framework.py#L52)、[检查:1548–1573](../../main_with_no_framework.py#L1548) |
| `uv run --group integrations bot-review review --resolved-since 30` | 复盘近期已结算预测，需网络及 `METACULUS_TOKEN`；集成文档称不产生 LLM 费用，首次使用可能安装可选依赖。 | [README:129–140](../../README.md#L129)、[integrations/README:7、31–40](../../integrations/README.md#L31) |
| `git push origin <your-branch>` | README 的远端分支验证准备步骤，需要网络和 GitHub 写权限；本卡禁止执行。 | [README:45–52](../../README.md#L45)、[任务卡:49](../tasks/2026-11-17-codex-handoff/README.md#L49) |
| `pip install asknews` | AskNews 示例代码说明中的单独安装命令，缺少缓存需网络；本项目已通过 pyproject 声明 AskNews。 | [README:142–155](../../README.md#L142)、[pyproject.toml:11](../../pyproject.toml#L11) |

主入口的启动检查要求 `METACULUS_TOKEN`，以及 `OPENROUTER_API_KEY`、`OPENAI_API_KEY`、`ANTHROPIC_API_KEY` 至少一种；`PERPLEXITY_API_KEY` 或 AskNews 凭据不能单独替代这里的 LLM key。具体模型是否能调用仍取决于 SDK 选择，见第 6 节。[bot_helpers.py:58–88](../../bot_helpers.py#L58)

### Workflow 的实际命令

四个 workflow 都使用 `ubuntu-latest`、Python `3.11`、`astral-sh/setup-uv@v10.3.0` 和 uv `0.13.1`；每个 workflow 以自身名称作为并发组，`cancel-in-progress: false`。下表为文件定义，云端启用状态和实际执行记录均未核实。[test_bot.yaml:6–28](../../.github/workflows/test_bot.yaml#L6)、[tournament:8–30](../../.github/workflows/run_bot_on_tournament.yaml#L8)、[Cup:8–30](../../.github/workflows/run_bot_on_metaculus_cup.yaml#L8)、[review:12–36](../../.github/workflows/review_bot.yaml#L12)

| Workflow | 触发条件 | 安装与运行原文 | 出处 |
|---|---|---|---|
| `test_bot.yaml` / Test Bot | 仅手动 `workflow_dispatch` | `uv sync --locked`；`uv run python main.py --mode test_questions` | [test_bot.yaml:1–42](../../.github/workflows/test_bot.yaml#L1) |
| `run_bot_on_tournament.yaml` | 手动或 cron `7,27,47 * * * *` | `uv sync --locked`；`uv run python main.py`（代码默认 `tournament`） | [tournament:1–44](../../.github/workflows/run_bot_on_tournament.yaml#L1)、[main.py:692–701](../../main.py#L692) |
| `run_bot_on_metaculus_cup.yaml` | 手动或 cron `0 0 */2 * *` | `uv sync --locked`；`uv run python main.py --mode metaculus_cup` | [Cup:1–44](../../.github/workflows/run_bot_on_metaculus_cup.yaml#L1) |
| `review_bot.yaml` | 手动始终允许；cron `0 6 * * 1` 须仓库变量 `REVIEW_BOT_ENABLED` 为 `true` | `uv sync --locked --group integrations`；随后执行下方多行命令 | [review:1–44](../../.github/workflows/review_bot.yaml#L1) |

`review_bot.yaml` 原文的运行和摘要命令如下，随后通过 `actions/upload-artifact@v4` 上传 `review.json`、`review.md`，保留 90 天。[review_bot.yaml:37–54](../../.github/workflows/review_bot.yaml#L37)

```bash
uv run bot-review review \
  --resolved-since ${{ inputs.days || 30 }} \
  --output review.json \
  --summary review.md
cat review.md >> $GITHUB_STEP_SUMMARY
```

三个预测 workflow 都映射 `METACULUS_TOKEN`、`PERPLEXITY_API_KEY`、`EXA_API_KEY`、`OPENAI_API_KEY`、`OPENROUTER_API_KEY`、`ANTHROPIC_API_KEY`、`ASKNEWS_CLIENT_ID`、`ASKNEWS_SECRET`，并非全部必填；复盘只映射 `METACULUS_TOKEN`。运行均涉及外部网络；密钥是否已配置未读取。[test_bot.yaml:34–42](../../.github/workflows/test_bot.yaml#L34)、[tournament:36–44](../../.github/workflows/run_bot_on_tournament.yaml#L36)、[Cup:36–44](../../.github/workflows/run_bot_on_metaculus_cup.yaml#L36)、[review:43–44](../../.github/workflows/review_bot.yaml#L43)

### 可选集成与验收路径

集成 README 的其余命令如下：LightningRod 需网络和 `LIGHTNINGROD_API_KEY`；bot-review 需网络和 `METACULUS_TOKEN`。其 SDK 是否另需客户端模型凭据未核实，不推断已具备。[integrations/README.md:23–49](../../integrations/README.md#L23)、[LightningRod 客户端初始化:128–132](../../integrations/main_lightningrod_eval.py#L128)

```bash
uv run --group integrations python integrations/main_lightningrod_eval.py
uv run --group integrations bot-review review --tournament <slug-or-id> --output review.json --summary review.md
uv run --group integrations bot-review show <POST_ID> --section research
uv run --group integrations bot-review show <POST_ID> --forecaster R1:F3
```

本地单元测试、lint、类型检查入口：无已跟踪的对应文件或配置（`git ls-files` 清单只有应用、文档、依赖和上述 workflows；`pyproject.toml` 没有这些工具的配置）。`Test Bot` 是外部端到端冒烟，不是离线单元测试。授权试跑后，按 README 检查运行摘要，再切换到 Metaculus bot account，检查预测图和 `Private` 评论；无待预测题或 workflow 绿色本身不足以证明成功提交。[README:31、36–43](../../README.md#L31)、[bot_helpers.py:110–147](../../bot_helpers.py#L110)

## 4. 进行中的工作

本节仅描述本地 refs；没有 fetch，也未查询 GitHub PR，因此“未合入”只指提交图不能从 `main` 到达，不等于 PR 仍然开放，也可能是 squash 合并后留下的远端跟踪分支。

在指定 worktree 内执行 `git branch -a -vv`、`git branch -a --no-merged main`、`git worktree list --porcelain` 得到：

| 分支或 ref | HEAD | 本地观察 |
|---|---|---|
| `main` | `bcbd016` | 跟踪 `origin/main`，主检出使用 |
| `task/codex-handoff-20261117` | `15d1034` | 当前工作分支，跟踪 `origin/main`，ahead 1；未合入 `main` |
| `origin/HEAD` | → `origin/main` | 符号 ref |
| `origin/main` | `bcbd016` | 与本地 `main` 一致 |
| `origin/chore/readme-open-source-bots-ft-0.3` | `be71462` | 出现在 `--no-merged main` |
| `origin/claude/ftools-cooldown-exempt-19e5ac` | `b123556` | 同上 |
| `origin/claude/nest-asyncio-worktree-compat-a2e1e2` | `7d8091f` | 同上 |
| `origin/claude/require-openrouter-drop-llm-proxy` | `1fbdff5` | 同上 |
| `origin/claude/uv-lock-upgrade-19e5ac` | `3a29c21` | 同上 |
| `origin/dependabot/pip/transformers-4.48.0` | `b4e6247` | 同上 |
| `origin/feat/numeric-pchip-distribution` | `f14a475` | 同上 |
| `upstream/HEAD` | → `upstream/main` | 符号 ref |
| `upstream/main` | `bcbd016` | 本地保存的上游快照，与 `main` 一致 |

全部工作树如下，没有其他登记项（来源：`git worktree list --porcelain`）：

| 工作树绝对路径 | 分支 | HEAD |
|---|---|---|
| `/Users/tomxiao/Code/metac-bot-template` | `main` | `bcbd016b9c6aee4f62ceeb7f8556b4d96d97b1cc` |
| `/Users/tomxiao/Code/metac-bot-template/.worktrees/codex-handoff-20261117` | `task/codex-handoff-20261117` | `15d1034f1532457adcdc8dbec0c9733dcb325eaa` |

差异命令及输出：

```text
git log upstream/main..main                       -> 无输出
git log main..upstream/main                       -> 无输出
git diff --stat upstream/main main               -> 无输出
git rev-list --left-right --count upstream/main...main -> 0  0
git rev-list --left-right --count main...HEAD      -> 0  1
git diff --name-status main HEAD                  -> A docs/tasks/2026-11-17-codex-handoff/README.md
```

`15d1034` 的主题为“docs: 交接任务卡 2026-11-17”；本次交接文档是该提交之后的未暂存新增文件，不包含在上表的提交差异里。开始工作时当前 worktree 的 `git status --porcelain=v1 --untracked-files=all` 无输出；主检出的只读状态命令 `git --no-optional-locks --git-dir=../../.git --work-tree=../.. status --short --branch` 仅输出 `## main...origin/main`。主检出未由本任务修改。

## 5. 最近 30 天做了什么

按交接日计算，日期范围为 2026-10-19 至 2026-11-17，只统计本地 `upstream/main` 可见的提交，共 5 个；不代表在线上游此后没有更新。依据命令：

```bash
git log upstream/main --since='2026-10-19T00:00:00-04:00' --until='2026-11-17T23:59:59-05:00' --format='%h %cs %s'
```

| 主题 | 结果与规划影响 | 提交证据 |
|---|---|---|
| 依赖工具链与升级策略 | 从 Poetry 转为 uv，README、workflows 和集成命令一起迁移；升级锁文件，并为一般依赖设置 7 天冷却期；随后豁免 `forecasting-tools`，将其锁到 0.3.5。后续按 uv 工作流维护，不使用旧 Poetry 命令。 | `898f09a`（#121）、`f3bfe8b`（#122）、`8c898aa`（#123）；`git show 898f09a -- pyproject.toml`、`git show 8c898aa -- pyproject.toml`、[uv.lock:584–585](../../uv.lock#L584) |
| 启动配置失败前置 | Metaculus LLM proxy 已不可用的说明进入缺失 LLM key 的错误提示；无 OpenRouter/OpenAI/Anthropic key 时由警告改为失败退出。最终补丁只改 `bot_helpers.py`，没有固定模型。 | `ccee1c5`（#124），`git show ccee1c5 -- bot_helpers.py`；[bot_helpers.py:71–88](../../bot_helpers.py#L71) |
| Python 兼容性 | 限制 Python 小于 3.14；提交说明归因于 `nest_asyncio` 在 3.14 下破坏 `asyncio.timeout`，锁文件去掉不适用条件，未改变包版本。实际复现未做。 | `bcbd016`（#126），`git show bcbd016 -- README.md pyproject.toml`；[README:86](../../README.md#L86)、[pyproject.toml:7](../../pyproject.toml#L7) |

## 6. 已知问题与坑

1. **锁定版本已核实，OpenRouter 默认模型未核实。** `uv.lock:584–585` 为 `forecasting-tools==0.3.5`；`main.py:707–728` 的 `llms` 配置被注释，因此 `default`、`researcher`、`summarizer`、`parser` 由父类选择。这里“只设 `OPENROUTER_API_KEY`”指只提供这一种模型/搜索凭据，实际跑主入口仍须 `METACULUS_TOKEN`。本次未找到可读取的对应 SDK 源码，不能把示例中的 `openrouter/openai/gpt-4o` 当作默认值。[uv.lock](../../uv.lock#L584)、[main.py](../../main.py#L707)、[bot_helpers.py](../../bot_helpers.py#L65)

   查找证据：项目 worktree 和主检出的 `.venv` 均未找到；`/Users/tomxiao/.cache/uv` 存在，`UV_CACHE_DIR` 未设置；`rg --files --hidden --no-ignore -L /Users/tomxiao/.cache/uv -g 'forecast_bot.py' -g 'general_llm.py' -g '**/forecasting_tools/**' -g '**/forecasting_tools-*.dist-info/METADATA'` 未返回对应源码。常见 Homebrew、用户 Python 和 uv tools 安装路径也未找到对应包；没有为核查安装或下载依赖。后续应从与 0.3.5 对应的本地包源码核对四个角色的选择分支，模型线上可用性另行验证。

2. **上游提交说明不能代替最终模型配置。** `git show ccee1c5 -- bot_helpers.py` 的提交说明曾称 OpenRouter-only researcher `openai/gpt-4o-search-preview` 已被移除，也描述过固定模型的中间方案；同一说明随后明确恢复 `main.py` 等文件，最终 diff 只有启动检查。故“该模型曾失效”是历史提交报告，当前 0.3.5 的选择及线上状态均未核实；不把该历史报告写成已修复或当前实测结果。出处：提交 `ccee1c5`、[main.py:707–728](../../main.py#L707)。

3. **测试模式仍会提交，dry-run 也不等于离线。** `publish_to_metaculus=True`，`test_questions` 还将跳过已有预测设为 `False`；重复测试可再次产生预测与模型调用。README 说通过构造参数关闭发布，当前实际可改统一变量 `publish_to_metaculus=False`，让参数和 banner 一致；这是后续实现建议，本卡未改代码。无框架版本的开关是 `SUBMIT_PREDICTION=False`。只关闭发布仍会拉题、研究和调用模型。[README:125–127](../../README.md#L125)、[main.py:703–717、767–782](../../main.py#L703)、[无框架入口:1639–1646](../../main_with_no_framework.py#L1639)

4. **绿色 workflow 不足以证明预测成功。** 主入口传入 `return_exceptions=True`，结果摘要对收集到的异常只打印，末尾没有把这类失败显式转成非零退出；应核对成功数、错误及预测页面。[main.py:743–783](../../main.py#L743)、[bot_helpers.py:110–150](../../bot_helpers.py#L110)。此外默认 `folder_to_save_reports_to=None`，不要假定本地有报告归档。[main.py:715](../../main.py#L715)

5. **README 的替换入口建议有环境前提。** README 说将 workflow 脚本名换成无框架入口即可，但后者要求 `OPENAI_API_KEY`，不是主入口的三选一；它也没有 `--mode`，顶部 `CURRENT_METACULUS_CUP_ID=None`。试跑目标应依该文件常量单独核对。[README:63、119–123](../../README.md#L63)、[main_with_no_framework.py:52–91](../../main_with_no_framework.py#L52)、[1548–1573](../../main_with_no_framework.py#L1548)

6. **版本、赛季与费用边界需要另验。** Python 3.14 被明确排除；主入口比赛 ID 来自 SDK 常量，页尾 URL 则硬编码 Fall 2026；SDK 源码不可得时不能核实二者一致。三种模式默认每题五次预测，Cup 与测试区允许重复预测，代码中这些配置不是总金额预算。出处：[pyproject.toml:7](../../pyproject.toml#L7)、[main.py:710–775](../../main.py#L710)。云端比赛当前开放情况、模型价格、实际扣费和参赛表单完成情况：未核实；表单要求见 [README:32](../../README.md#L32)。

## 7. 待决定事项

以下为建议，尚未获得本卡以外的执行授权；无需为了交付本文立即让 Tom 拍板。

| 需要 Tom 决定的取舍 | 建议默认值 | 依据 |
|---|---|---|
| 首次试跑的范围、是否允许发布，是否直接启用定时比赛 | 先安排一次手动、限题的 `bot-testing-area` 验证；不同时启用正式比赛与 Cup 定时运行。具体限题方式另卡实现。 | [README:31–34](../../README.md#L31)、[测试模式会重做预测](../../main.py#L767)、[正式定时定义](../../.github/workflows/run_bot_on_tournament.yaml#L3) |
| 模型供应商与费用上限 | 沿用 README 推荐的 OpenRouter 作为首选，但先核实 0.3.5 四个角色并固定可用模型；研究策略优先复用同一供应商。总费用上限由 Tom 明确后再做付费试跑，不自行假设额度。 | [README:27–29](../../README.md#L27)、[当前未固定模型](../../main.py#L707)、本交接第 6 节 |
| 首轮是否包含额外数据生成、复盘集成 | 首轮只验推荐主入口；LightningRod 暂不纳入，有已结算预测后再评估 bot-review。 | [README:7–10](../../README.md#L7)、[integrations/README:13–35](../../integrations/README.md#L13) |

## 8. 外部依赖与环境

| 服务或环境 | 变量名及用途 | 去哪里找；证据 |
|---|---|---|
| Metaculus / FutureEval | `METACULUS_TOKEN`：读取题目、发布预测与评论、读取已结算报告 | [FutureEval 参与页](https://www.metaculus.com/futureeval/participate/) 和 [机器人设置资源](https://www.metaculus.com/notebooks/38928/ai-benchmark-resources/#creating-your-bot-account-and-metaculus-token)；[README:27–32](../../README.md#L27)、[integrations/README:35](../../integrations/README.md#L35) |
| OpenRouter | `OPENROUTER_API_KEY`：主入口推荐模型供应商凭据 | [OpenRouter](https://openrouter.ai/)，申请额度入口见 [README:29](../../README.md#L29)；默认模型未核实 |
| OpenAI / Anthropic | `OPENAI_API_KEY`、`ANTHROPIC_API_KEY`：主入口可接受的替代模型凭据；无框架入口必须有前者 | 各供应商控制台；仓库导航见 [README:54–55](../../README.md#L54)，检查依据 [bot_helpers.py:71–74](../../bot_helpers.py#L71)、[无框架检查:1556](../../main_with_no_framework.py#L1556) |
| AskNews / Exa / Perplexity | `ASKNEWS_CLIENT_ID` + `ASKNEWS_SECRET`、`EXA_API_KEY`、`PERPLEXITY_API_KEY`：可选在线研究供应商 | [README 的资源入口](../../README.md#L54)；无框架版本按 AskNews → Exa → Perplexity 优先级选择，均无则返回无研究文本：[main_with_no_framework.py:272–281](../../main_with_no_framework.py#L272)。主框架选择交由 SDK，未核实 |
| LightningRod | `LIGHTNINGROD_API_KEY`：可选新闻题目生成与评估服务 | [LightningRod dashboard](https://dashboard.lightningrod.ai)，[integrations/README:23–29](../../integrations/README.md#L23) |
| GitHub Actions | 预测 workflow 使用第 3 节列出的 secrets；`REVIEW_BOT_ENABLED` 是复盘调度开关，不是密钥；`GITHUB_STEP_SUMMARY` 是 runner 提供的摘要文件路径 | 仓库 `Settings → Secrets and variables → Actions`；[test_bot.yaml:32–42](../../.github/workflows/test_bot.yaml#L32)、[review_bot.yaml:19–46](../../.github/workflows/review_bot.yaml#L19)。未查询配置和运行记录 |
| Python / uv / PyPI | Python `3.11–3.13`；CI 固定 Python `3.11`、uv `0.13.1`；安装从锁文件指定 registry 取得依赖 | [pyproject.toml:7](../../pyproject.toml#L7)、[test_bot.yaml:20–28](../../.github/workflows/test_bot.yaml#L20)、[uv.lock:584–586](../../uv.lock#L584)。本机 `command -v uv python3` 分别返回 `/opt/homebrew/bin/uv`、`/opt/homebrew/bin/python3`；实际版本未核实 |

凭据的现有值、账户、额度和 Keychain 条目名均未读取或核实。仓库 README 介绍 `.env` 与 GitHub Secrets 的配置方式，但本会话 AGENTS.md 要求凭据只留 Keychain；后续按既有授权从 Keychain 注入进程环境，不新增凭据文件，远端配置是否已有或需另获授权由后续任务核实。本次没有新建环境、服务、容器、定时任务或运行产物；只新增本文。[README:27、95–100](../../README.md#L95)、[任务卡边界](../tasks/2026-11-17-codex-handoff/README.md#L46)

## 9. 建议 Claude Code 先看的 5 个文件

1. [README.md](../../README.md)：先确认用户路径、两种入口、测试区提交与 bot account 查看方式，重点第 23–140 行。
2. [main.py](../../main.py)：重点第 48–164、686–783 行，确认框架扩展面、默认参数、发布行为和赛季分派。
3. [uv.lock](../../uv.lock)：先看第 1–14、583–612 行，按真实锁定版本调查默认模型；不要用依赖允许范围或示例代替实际版本。
4. [bot_helpers.py](../../bot_helpers.py)：重点第 58–150 行，确认缺密钥的失败条件、摘要与退出状态的区别。
5. [.github/workflows/test_bot.yaml](../../.github/workflows/test_bot.yaml)：确认首次验收的真实环境、锁定安装命令与 secrets 映射，再结合第 3 节其他调度文件决定上线范围。
