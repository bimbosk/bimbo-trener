"""Windows Task Scheduler task that runs sync.cmd once a day (Interactive: only while I am logged in)."""
from __future__ import annotations

import base64
import os
import subprocess

TASK_NAME = "BimboTrener-Sync"


def _ps(script: str) -> subprocess.CompletedProcess:
    encoded = base64.b64encode(script.encode("utf-16le")).decode()
    return subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-EncodedCommand", encoded],
                          capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)


def _q(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def enable(sync_cmd: str, working_directory: str, at: str = "07:30") -> dict:
    if os.name != "nt":
        raise RuntimeError("Plánovaná úloha je dostupná iba na Windows.")
    script = (f"$a = New-ScheduledTaskAction -Execute {_q(sync_cmd)} -Argument '-Quiet' -WorkingDirectory {_q(working_directory)};"
              f"$t = New-ScheduledTaskTrigger -Daily -At {_q(at)};"
              "$s = New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 30) "
              "-StartWhenAvailable -DontStopIfGoingOnBatteries -AllowStartIfOnBatteries;"
              "$p = New-ScheduledTaskPrincipal -UserId ([Security.Principal.WindowsIdentity]::GetCurrent().Name) -LogonType Interactive -RunLevel Limited;"
              f"Register-ScheduledTask -TaskName {_q(TASK_NAME)} -Action $a -Trigger $t -Settings $s -Principal $p "
              "-Description 'Bimbo trener: denne stiahnutie dat z Garmin Connect' -Force | Out-Null; 'ok'")
    result = _ps(script)
    if result.returncode != 0 or "ok" not in result.stdout:
        raise RuntimeError(f"Plánovanú úlohu sa nepodarilo vytvoriť: {result.stderr.strip()[-500:]}")
    return status()


def disable() -> dict:
    if os.name != "nt":
        return {"task": TASK_NAME, "exists": False}
    result = _ps(f"$t = Get-ScheduledTask -TaskName {_q(TASK_NAME)} -ErrorAction SilentlyContinue;"
                 f"if ($t) {{ Unregister-ScheduledTask -TaskName {_q(TASK_NAME)} -Confirm:$false }}; 'ok'")
    if result.returncode != 0 or "ok" not in result.stdout:
        raise RuntimeError(f"Plánovanú úlohu sa nepodarilo odstrániť: {result.stderr.strip()[-500:]}")
    return status()


def status() -> dict:
    if os.name != "nt":
        return {"task": TASK_NAME, "exists": False, "supported": False}
    result = _ps(f"$t = Get-ScheduledTask -TaskName {_q(TASK_NAME)} -ErrorAction SilentlyContinue;"
                 "if ($t) { $i = $t | Get-ScheduledTaskInfo; 'exists|' + $t.State + '|' + $i.LastRunTime + '|' + "
                 "$i.LastTaskResult + '|' + $i.NextRunTime } else { 'missing' }")
    line = (result.stdout.strip().splitlines() or ["missing"])[-1]
    if not line.startswith("exists|"):
        return {"task": TASK_NAME, "exists": False, "supported": True}
    _, state, last, code, nxt = (line.split("|") + [""] * 5)[:5]
    return {"task": TASK_NAME, "exists": True, "supported": True, "state": state, "last_run": last, "last_result": code, "next_run": nxt}
