import os
from pathlib import Path
import plistlib
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
LABEL = "com.tom.metac-tournament-trigger"
REPO = "TomXiaoYZ/metac-bot-template"
GH_STUB = r"""#!/bin/bash
set -eu
printf '%s\n' "$*" >> "$GH_CALLS"
if [[ "$1 $2" == 'run list' ]]; then
    case " $* " in
        *" --status ${FAIL_LIST_STATUS:-none} "*)
            printf '读取失败\n第二行详情\n' >&2; exit 2 ;;
    esac
    case " $* " in
        *' --status queued '*) printf '%s\n' "${QUEUED_COUNT:-0}" ;;
        *' --status in_progress '*) printf '%s\n' "${IN_PROGRESS_COUNT:-0}" ;;
        *) exit 99 ;;
    esac
elif [[ "$1 $2" == 'workflow run' ]]; then
    if [[ "${DISPATCH_EXIT:-0}" != 0 ]]; then
        printf '触发失败\n第二行详情\n' >&2
    fi
    exit "${DISPATCH_EXIT:-0}"
else
    exit 99
fi
"""
LAUNCHCTL_STUB = r"""#!/bin/bash
set -eu
printf '%s\n' "$*" >> "$LAUNCHCTL_CALLS"
case "$1" in
    print) test -f "$LAUNCHCTL_STATE" ;;
    bootstrap) touch "$LAUNCHCTL_STATE" ;;
    bootout)
        test -f "$LAUNCHCTL_STATE" || exit 113
        rm "$LAUNCHCTL_STATE" ;;
    *) exit 99 ;;
esac
"""


class LaunchdTriggerTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(dir=ROOT)
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)
        self.fake_home = self.directory / "fake home"
        self.log = self.fake_home / "Library/Logs/metac-bot-trigger.log"
        self.log.parent.mkdir(parents=True)
        stub_dir = self.directory / "bin"
        stub_dir.mkdir()
        for name, content in (("gh", GH_STUB), ("launchctl", LAUNCHCTL_STUB)):
            stub = stub_dir / name
            stub.write_text(content)
            stub.chmod(0o755)
        self.gh_calls = self.directory / "gh-calls"
        self.launchctl_calls = self.directory / "launchctl-calls"
        self.gh_calls.touch()
        self.launchctl_calls.touch()
        self.env = {
            "HOME": str(self.fake_home),
            "PATH": f"{stub_dir}:/usr/bin:/bin",
            "GH_CALLS": str(self.gh_calls),
            "LAUNCHCTL_CALLS": str(self.launchctl_calls),
            "LAUNCHCTL_STATE": str(self.directory / "loaded"),
        }
        self.plist = self.fake_home / f"Library/LaunchAgents/{LABEL}.plist"
        self.libexec = self.fake_home / ".local/libexec/metac-bot-trigger"

    def run_script(self, name, **environment):
        return subprocess.run(
            ["/bin/bash", str(ROOT / "scripts/launchd" / name)],
            env=self.env | environment, cwd=self.directory,
            capture_output=True, text=True,
        )

    def assert_success(self, result):
        self.assertEqual(result.returncode, 0, result.stderr)

    def assert_timestamped(self, path):
        for line in path.read_text().splitlines():
            self.assertRegex(line, r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z ")

    def test_dispatches_when_no_active_run(self):
        self.assert_success(self.run_script("trigger_tournament.sh"))
        self.assertIn(f"workflow run 421273160 -R {REPO} --ref main",
                      self.gh_calls.read_text().splitlines())
        self.assertIn("已触发", self.log.read_text().splitlines()[-1])
        self.assert_timestamped(self.log)

    def test_skips_when_run_active(self):
        for status in ("QUEUED_COUNT", "IN_PROGRESS_COUNT"):
            with self.subTest(status=status):
                self.gh_calls.write_text("")
                self.assert_success(self.run_script("trigger_tournament.sh", **{status: "1"}))
                self.assertNotIn("workflow run", self.gh_calls.read_text())
                self.assertIn("跳过", self.log.read_text().splitlines()[-1])
        self.assert_timestamped(self.log)

    def test_all_gh_calls_pin_repo(self):
        self.assert_success(self.run_script("trigger_tournament.sh"))
        calls = self.gh_calls.read_text().splitlines()
        self.assertEqual(len(calls), 3)
        for call in calls:
            self.assertIn(f"-R {REPO}", call)
        for status in ("queued", "in_progress"):
            self.assertIn(f"run list -R {REPO} --workflow 421273160 "
                          f"--status {status} --json databaseId --jq length", calls)

    def test_dispatch_failure_exits_nonzero(self):
        result = self.run_script("trigger_tournament.sh", DISPATCH_EXIT="1")
        self.assertEqual(result.returncode, 1)
        self.assertIn("错误", self.log.read_text())
        self.assertIn("触发失败", self.log.read_text())
        self.assertIn("第二行详情", self.log.read_text())
        self.assertEqual(self.gh_calls.read_text().count("workflow run"), 1)
        self.assert_timestamped(self.log)

    def test_list_failure_exits_nonzero_without_dispatch(self):
        for status in ("queued", "in_progress"):
            with self.subTest(status=status):
                self.gh_calls.write_text("")
                result = self.run_script("trigger_tournament.sh", FAIL_LIST_STATUS=status)
                self.assertEqual(result.returncode, 2)
                self.assertIn("错误", self.log.read_text())
                self.assertIn("读取失败", self.log.read_text())
                self.assertNotIn("workflow run", self.gh_calls.read_text())
                self.assertEqual(self.gh_calls.read_text().count(f"--status {status}"), 1)
        self.assert_timestamped(self.log)

    def test_log_trimmed_to_2000_lines(self):
        custom_log = self.fake_home / "custom.log"
        custom_log.write_text("旧记录\n" * 2500)
        self.assert_success(self.run_script("trigger_tournament.sh", METAC_TRIGGER_LOG=str(custom_log)))
        lines = custom_log.read_text().splitlines()
        self.assertEqual(len(lines), 2000)
        self.assertIn("已触发", lines[-1])
        self.assertFalse(self.log.exists())

    def test_install_writes_plist_and_bootstraps(self):
        self.assert_success(self.run_script("install.sh"))
        lint = subprocess.run(["/usr/bin/plutil", "-lint", str(self.plist)],
                              capture_output=True, text=True)
        self.assertEqual(lint.returncode, 0, lint.stdout + lint.stderr)
        config = plistlib.loads(self.plist.read_bytes())
        installed = self.libexec / "trigger_tournament.sh"
        self.assertEqual(config["Label"], LABEL)
        self.assertEqual(config["StartInterval"], 1200)
        self.assertIs(config["RunAtLoad"], True)
        self.assertEqual(config["ProgramArguments"], ["/bin/bash", str(installed)])
        self.assertEqual(config["EnvironmentVariables"], {
            "HOME": str(self.fake_home),
            "PATH": "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin",
        })
        for key in ("StandardOutPath", "StandardErrorPath"):
            self.assertEqual(config[key], str(self.log.with_name("metac-bot-trigger.launchd.log")))
        self.assertEqual(installed.read_bytes(), (ROOT / "scripts/launchd/trigger_tournament.sh").read_bytes())
        self.assertTrue(os.access(installed, os.X_OK))
        self.assertNotIn("token", self.plist.read_text().lower())
        self.assertIn(f"bootstrap gui/{os.getuid()} {self.plist}", self.launchctl_calls.read_text())
        self.launchctl_calls.write_text("")
        self.assert_success(self.run_script("install.sh"))
        calls = self.launchctl_calls.read_text().splitlines()
        self.assertLess(calls.index(f"bootout gui/{os.getuid()}/{LABEL}"),
                        calls.index(f"bootstrap gui/{os.getuid()} {self.plist}"))

    def test_uninstall_removes_plist_and_script_keeps_log(self):
        self.assert_success(self.run_script("install.sh"))
        launchd_log = self.log.with_name("metac-bot-trigger.launchd.log")
        for path in (self.log, launchd_log):
            path.write_text("保留日志\n")
        self.assert_success(self.run_script("uninstall.sh"))
        self.assertFalse(self.plist.exists())
        self.assertFalse(self.libexec.exists())
        for path in (self.log, launchd_log):
            self.assertEqual(path.read_text(), "保留日志\n")
        self.assertIn(f"bootout gui/{os.getuid()}/{LABEL}", self.launchctl_calls.read_text())
        self.assert_success(self.run_script("uninstall.sh"))
