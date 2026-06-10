#!/usr/bin/env python3
import plistlib
import subprocess
from pathlib import Path


LABEL = "local.status-bot"


def main() -> None:
    project_dir = Path(__file__).resolve().parents[1]
    home = Path.home()
    launch_agents_dir = home / "Library" / "LaunchAgents"
    launch_agents_dir.mkdir(parents=True, exist_ok=True)

    plist_path = launch_agents_dir / f"{LABEL}.plist"
    python_executable = (project_dir / ".venv" / "bin" / "python").resolve()
    log_path = project_dir / "bot.log"

    plist = {
        "Label": LABEL,
        "Program": str(python_executable),
        "ProgramArguments": [str(python_executable), "-m", "status_bot.main"],
        "WorkingDirectory": str(project_dir),
        "RunAtLoad": True,
        "KeepAlive": True,
        "StandardOutPath": str(log_path),
        "StandardErrorPath": str(log_path),
        "EnvironmentVariables": {
            "PYTHONUNBUFFERED": "1",
        },
    }

    with plist_path.open("wb") as file:
        plistlib.dump(plist, file)

    subprocess.run(["launchctl", "bootout", f"gui/{_uid()}", str(plist_path)], check=False)
    subprocess.run(["launchctl", "bootstrap", f"gui/{_uid()}", str(plist_path)], check=True)
    subprocess.run(["launchctl", "kickstart", "-k", f"gui/{_uid()}/{LABEL}"], check=True)

    print(f"Installed and started {LABEL}")
    print(f"Plist: {plist_path}")
    print(f"Logs: {log_path}")


def _uid() -> int:
    return int(subprocess.check_output(["id", "-u"], text=True).strip())


if __name__ == "__main__":
    main()
