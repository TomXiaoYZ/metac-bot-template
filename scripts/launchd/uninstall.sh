#!/bin/bash
set -euo pipefail

readonly LABEL="com.tom.metac-tournament-trigger"
launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
rm -f "$HOME/Library/LaunchAgents/$LABEL.plist"
rm -rf "$HOME/.local/libexec/metac-bot-trigger"
# 两份日志均保留；launchd 日志在卸载后按需手工删除。
