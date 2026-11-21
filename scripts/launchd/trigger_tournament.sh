#!/bin/bash
set -euo pipefail

readonly REPO="TomXiaoYZ/metac-bot-template"
readonly WORKFLOW_ID="421273160"
readonly LOG_FILE="${METAC_TRIGGER_LOG:-$HOME/Library/Logs/metac-bot-trigger.log}"

write_log() {
    local line
    while IFS= read -r line; do
        printf '%s %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$line" >> "$LOG_FILE"
    done <<< "$1"
    tail -n 2000 "$LOG_FILE" > "$LOG_FILE.tmp"
    mv "$LOG_FILE.tmp" "$LOG_FILE"
}

run_gh() {
    local output status
    if output=$(gh "$@" 2>&1); then
        printf '%s\n' "$output"
    else
        status=$?
        write_log "错误：gh $*: $output"
        return "$status"
    fi
}

for run_status in queued in_progress; do
    active=$(run_gh run list -R "$REPO" --workflow "$WORKFLOW_ID" \
        --status "$run_status" --json databaseId --jq length)
    if (( active > 0 )); then
        write_log "跳过：存在 $run_status 运行"
        exit 0
    fi
done

run_gh workflow run "$WORKFLOW_ID" -R "$REPO" --ref main > /dev/null
write_log "已触发：$REPO 工作流 $WORKFLOW_ID"
