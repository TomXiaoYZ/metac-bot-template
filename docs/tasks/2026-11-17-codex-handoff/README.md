# 任务卡：项目交接文档

- 派出：2026-11-17，Claude Code
- 仓库：/Users/tomxiao/Code/metac-bot-template
- 工作树：/Users/tomxiao/Code/metac-bot-template/.worktrees/codex-handoff-20261117
- 分支：task/codex-handoff-20261117（基于 main，bcbd016）
- Codex 线程：派出后由任务会话回填

## 目标

这个仓库是 Tom 从 Metaculus 官方 `metac-bot-template` fork 的预测机器人模板（GitHub：TomXiaoYZ/metac-bot-template），
用于 Metaculus FutureEval 机器人预测赛试跑，此前没有本地开发。从现在起由 Claude Code 负责规划、拆任务和验收，
Codex 负责既定规格内的实现。Claude Code 需要一份能让它独立做规划决定的交接文档：
现状是什么、和上游有什么差异、哪些坑不能踩、怎么跑起来验证。

## 授权

- 网络：关
- 额外可写目录：无
- MCP：关
- 模型：默认
- 强度：默认

## 产出

`docs/handoff/2026-11-17-codex-handoff.md`，中文，结论先行，每条事实给出处（文件路径、分支、
提交、命令输出）。内容按以下结构，没有的小节写“无”，不要凑：

1. **一句话定位**：产品是什么、给谁用、现在处于什么阶段。
2. **代码地图**：顶层文件与目录（`main.py`、`main_with_no_framework.py`、`bot_helpers.py`、`integrations/`、`.github/workflows/`、`pyproject.toml`、`uv.lock`）各自负责什么；依赖 `forecasting-tools` 的哪些入口。
3. **怎么跑、怎么验**：README 和各 workflow 里的实际命令；哪些需要密钥或网络（只写变量名）。
4. **进行中的工作**：未合并分支、工作树、与 upstream 的差异（`git log upstream/main..main` 等，本地已有的 ref 即可，不 fetch）。
5. **最近 30 天做了什么**：按主题归纳上游提交，不逐条列。
6. **已知问题与坑**：至少核对一条：`uv.lock` 锁定的 `forecasting-tools` 版本，以及它的 `ForecastBot` 在只设 `OPENROUTER_API_KEY` 时选用的默认模型（读本地已安装或 uv 缓存里的源码，读不到就标“未核实”）。
7. **待决定事项**：需要 Tom 拍板的取舍，各给一个建议默认值。
8. **外部依赖与环境**：服务、密钥的名字和用途（只写名字和去哪里找，不写值）。
9. **建议 Claude Code 先看的 5 个文件**。

## 验收标准

1. 文档存在于上述路径，各小节齐全，事实都有出处。
2. 第 3 节的命令由 Claude Code 核对与 README/workflow 一致（需要密钥的只核命令存在）。
3. 第 4 节列出的分支和工作树与 `git branch -a`、`git worktree list` 一致。
4. 主检出工作区未被改动；改动只在工作树内，只新增这一份文档。

## 边界

- 只在工作树内读写；可以读主检出的文件与 git 历史，不改它们。
- 不 push、不 fetch、不改代码、不改配置、不装依赖、不跑 `main.py`；不读取或写入密钥值。
- 可以运行只读命令（git log、ls、cat、rg），不运行会改状态的脚本。
- 事实不确定就标“未核实”，不猜。

## 完成定义

文档写入工作树并自检完各小节为止。不要执行 `git add`/`git commit`：提交由 Claude Code
验收后完成（链接工作树的 git 元数据对你是只读的）。

## 回执格式

```
status: done | blocked | failed
branch: task/codex-handoff-20261117
changed_files:
  - docs/handoff/2026-11-17-codex-handoff.md
tests_run:
  - none
blockers:
  - <没有写 none>
human_action: none
next: <none 或建议>
```

## 轮次

### 第 1 轮

- Codex 线程：01a1e971-daba-75a2-a553-faf82e1b1670（gpt-6-astra/xhigh，网络关，MCP 关，stopAudit=true）
- 回执：status done；human_action none；blockers none

判决（2026-11-17，Claude Code 任务会话）：

```
verdict: accept
final: false
thread: 01a1e971-daba-75a2-a553-faf82e1b1670
receipt_status: done
self_audit: 回执未提供该字段
budget: 源码 +0 / 0 文件（只新增 docs/handoff/2026-11-17-codex-handoff.md）
audit: 0 处防御性代码
checklist: 10/10
acceptance:
  - 文档存在、九节齐全、事实带出处: pass（抽查 uv.lock:583-586、bot_helpers 密钥检查、main.py:704/718 均一致）
  - 第 3 节命令与 README/workflow 一致: pass（README 83–136 行与 4 个 workflow 的 uv sync --locked / uv run / cron 逐条核对）
  - 第 4 节分支/工作树与 git branch -a、git worktree list 一致: pass（7 个 origin 分支、2 个工作树、upstream...main = 0 0）
  - 主检出未改、只新增这一份文档: pass
main_checkout_clean: yes
human_action: none
备注: 第 6 节 forecasting-tools 0.3.5 版本已核实；只设 OPENROUTER_API_KEY 时的默认模型标“未核实”（本机 uv 缓存/.local/anaconda 均无 forecasting_tools 源码，已复查），修复卡需先联网取 0.3.5 源码核对。知识库检查：交接文档合规；任务卡本身缺 frontmatter，属项目会话写卡时的遗留，不影响本卡判决。
```
