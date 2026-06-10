#!/usr/bin/env python3
import subprocess
from pathlib import Path


LABEL = "local.status-bot"


def main() -> None:
    plist_path = Path.home() / "Library" / "LaunchAgents" / f"{LABEL}.plist"
    subprocess.run(["launchctl", "bootout", f"gui/{_uid()}", str(plist_path)], check=False)
    if plist_path.exists():
        plist_path.unlink()
    print(f"Stopped and removed {LABEL}")


def _uid() -> int:
    return int(subprocess.check_output(["id", "-u"], text=True).strip())


if __name__ == "__main__":
    main()
