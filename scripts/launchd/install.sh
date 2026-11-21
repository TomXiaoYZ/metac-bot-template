#!/bin/bash
set -euo pipefail

readonly LABEL="com.tom.metac-tournament-trigger"
readonly DOMAIN="gui/$(id -u)"
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly INSTALL_DIR="$HOME/.local/libexec/metac-bot-trigger"
readonly PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
readonly LAUNCHD_LOG="$HOME/Library/Logs/metac-bot-trigger.launchd.log"

mkdir -p "$INSTALL_DIR" "$HOME/Library/LaunchAgents" "$HOME/Library/Logs"
cp "$SCRIPT_DIR/trigger_tournament.sh" "$INSTALL_DIR/trigger_tournament.sh"
chmod 755 "$INSTALL_DIR/trigger_tournament.sh"

cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key><string>$LABEL</string>
    <key>ProgramArguments</key>
    <array><string>/bin/bash</string><string>$INSTALL_DIR/trigger_tournament.sh</string></array>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key><string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string>
        <key>HOME</key><string>$HOME</string>
    </dict>
    <key>StartInterval</key><integer>1200</integer>
    <key>RunAtLoad</key><true/>
    <key>StandardOutPath</key><string>$LAUNCHD_LOG</string>
    <key>StandardErrorPath</key><string>$LAUNCHD_LOG</string>
</dict>
</plist>
EOF

if launchctl print "$DOMAIN/$LABEL" > /dev/null 2>&1; then
    launchctl bootout "$DOMAIN/$LABEL"
fi
launchctl bootstrap "$DOMAIN" "$PLIST"
