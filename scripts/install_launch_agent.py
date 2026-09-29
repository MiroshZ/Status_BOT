#!/usr/bin/env python3
import os
import plistlib
import shutil
import subprocess
import tempfile
from pathlib import Path


LABEL = "local.status-bot"


def main() -> None:
    project_dir = Path(__file__).resolve().parents[1]
    home = Path.home()
    runtime_dir = home / ".status-bot-runtime"
    launch_agents_dir = home / "Library" / "LaunchAgents"
    launch_agents_dir.mkdir(parents=True, exist_ok=True)
    logs_dir = home / "Library" / "Logs" / "StatusBot"
    logs_dir.mkdir(parents=True, exist_ok=True)

    plist_path = launch_agents_dir / f"{LABEL}.plist"
    log_path = logs_dir / "bot.log"
    staging_root, staged_runtime = _prepare_runtime(project_dir, home)
    backup_dir = home / f".status-bot-runtime.backup-{os.getpid()}"
    runner = runtime_dir / "scripts" / "run_bot_launchd.sh"

    plist = {
        "Label": LABEL,
        "Program": "/bin/sh",
        "ProgramArguments": ["/bin/sh", str(runner)],
        "RunAtLoad": True,
        "KeepAlive": True,
        "StandardOutPath": "/dev/null",
        "StandardErrorPath": "/dev/null",
        "EnvironmentVariables": {
            "PYTHONUNBUFFERED": "1",
            "STATUS_BOT_LOG_FILE": str(log_path),
        },
    }

    try:
        with plist_path.open("wb") as file:
            plistlib.dump(plist, file)

        _bootout_if_loaded()
        if runtime_dir.exists():
            os.replace(runtime_dir, backup_dir)
        try:
            os.replace(staged_runtime, runtime_dir)
            subprocess.run(["launchctl", "bootstrap", f"gui/{_uid()}", str(plist_path)], check=True)
            subprocess.run(["launchctl", "kickstart", "-k", f"gui/{_uid()}/{LABEL}"], check=True)
        except Exception:
            _bootout_if_loaded()
            if runtime_dir.exists():
                shutil.rmtree(runtime_dir)
            if backup_dir.exists():
                os.replace(backup_dir, runtime_dir)
                subprocess.run(
                    ["launchctl", "bootstrap", f"gui/{_uid()}", str(plist_path)],
                    check=False,
                )
                subprocess.run(
                    ["launchctl", "kickstart", "-k", f"gui/{_uid()}/{LABEL}"],
                    check=False,
                )
            raise
        if backup_dir.exists():
            shutil.rmtree(backup_dir)
    finally:
        shutil.rmtree(staging_root, ignore_errors=True)

    print(f"Installed and started {LABEL}")
    print(f"Plist: {plist_path}")
    print(f"Logs: {log_path}")
    print(f"Runtime: {runtime_dir}")


def _prepare_runtime(project_dir: Path, home: Path) -> tuple[Path, Path]:
    staging_root = Path(tempfile.mkdtemp(prefix=".status-bot-staging-", dir=home))
    staged_runtime = staging_root / "runtime"
    ignore = shutil.ignore_patterns(
        ".git",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "__pycache__",
        "*.pyc",
        "bot.log",
        "bot.err.log",
        "bot.pid",
    )
    try:
        shutil.copytree(project_dir, staged_runtime, ignore=ignore)
        env_file = staged_runtime / ".env"
        if env_file.exists():
            env_file.chmod(0o600)
    except Exception:
        shutil.rmtree(staging_root, ignore_errors=True)
        raise
    return staging_root, staged_runtime


def _uid() -> int:
    return int(subprocess.check_output(["id", "-u"], text=True).strip())


def _bootout_if_loaded() -> None:
    service = f"gui/{_uid()}/{LABEL}"
    result = subprocess.run(
        ["launchctl", "print", service],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if result.returncode == 0:
        subprocess.run(["launchctl", "bootout", service], check=True)


if __name__ == "__main__":
    main()
