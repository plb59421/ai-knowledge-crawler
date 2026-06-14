"""Export tool-neutral automation definitions for external schedulers."""

import argparse
import json
import sys
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
AUTOMATION_PATH = PROJECT_ROOT / ".ai" / "automation.yaml"


def load_manifest(path: Path = AUTOMATION_PATH) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _quote_command(args: list[str]) -> str:
    return " ".join(f'"{arg}"' if " " in arg else arg for arg in args)


def _task_command(task: dict) -> str:
    command = task.get("command", {})
    return _quote_command([str(arg) for arg in command.get("args", [])])


def export_json(manifest: dict) -> str:
    return json.dumps(manifest, ensure_ascii=False, indent=2)


def export_markdown(manifest: dict) -> str:
    lines = [
        f"# {manifest.get('project', {}).get('name', 'Project')} Automation",
        "",
        manifest.get("project", {}).get("description", ""),
        "",
        "| Task | Schedule | Working Directory | Command |",
        "| --- | --- | --- | --- |",
    ]
    for task in manifest.get("tasks", []):
        schedule = task.get("schedule", {})
        schedule_text = schedule.get("expression") or schedule.get("type", "manual")
        cwd = task.get("command", {}).get("cwd", ".")
        lines.append(
            f"| `{task.get('id')}` | `{schedule_text}` | `{cwd}` | `{_task_command(task)}` |"
        )
    return "\n".join(lines)


def export_cron(manifest: dict) -> str:
    lines = [
        "# Generated from .ai/automation.yaml",
        f"# Timezone: {manifest.get('defaults', {}).get('timezone', 'local')}",
    ]
    for task in manifest.get("tasks", []):
        schedule = task.get("schedule", {})
        if schedule.get("type") != "cron" or not schedule.get("expression"):
            continue
        cwd = (PROJECT_ROOT / task.get("command", {}).get("cwd", ".")).resolve()
        lines.append(
            f"{schedule['expression']} cd {cwd} && {_task_command(task)} "
            f">> {PROJECT_ROOT / 'logs' / (task.get('id', 'automation') + '.log')} 2>&1"
        )
    return "\n".join(lines)


def export_windows(manifest: dict) -> str:
    lines = [
        "# Generated from .ai/automation.yaml",
        "$ProjectRoot = Split-Path -Parent $PSScriptRoot",
        "$PythonExe = 'python'",
        "",
    ]
    for task in manifest.get("tasks", []):
        schedule = task.get("schedule", {})
        if schedule.get("type") != "cron":
            continue
        trigger_time = _windows_daily_time(schedule.get("expression", "0 7 * * *"))
        task_id = task.get("id")
        task_name = f"AIKnowledgeCrawler-{task_id}"
        cwd = task.get("command", {}).get("cwd", ".")
        args = _task_command(task).replace("python ", "", 1)
        lines.extend(
            [
                f"$action = New-ScheduledTaskAction -Execute $PythonExe -Argument \"{args}\" -WorkingDirectory (Join-Path $ProjectRoot '{cwd}')",
                f"$trigger = New-ScheduledTaskTrigger -Daily -At {trigger_time}",
                f"Register-ScheduledTask -TaskName '{task_name}' -Action $action -Trigger $trigger -Description '{task.get('title', task_id)}' -Force",
                "",
            ]
        )
    return "\n".join(lines).rstrip()


def _windows_daily_time(expression: str) -> str:
    parts = expression.split()
    if len(parts) < 2:
        return "07:00"
    minute, hour = parts[0], parts[1]
    try:
        return f"{int(hour):02d}:{int(minute):02d}"
    except ValueError:
        return "07:00"


def main():
    parser = argparse.ArgumentParser(description="Export project automation definitions")
    parser.add_argument("--format", choices=["json", "markdown", "cron", "windows"], default="json")
    parser.add_argument("--output", help="Optional output file path")
    args = parser.parse_args()

    manifest = load_manifest()
    if args.format == "json":
        text = export_json(manifest)
    elif args.format == "markdown":
        text = export_markdown(manifest)
    elif args.format == "cron":
        text = export_cron(manifest)
    else:
        text = export_windows(manifest)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(text + "\n", encoding="utf-8")
    else:
        sys.stdout.write(text + "\n")


if __name__ == "__main__":
    main()
