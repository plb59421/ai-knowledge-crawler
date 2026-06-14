from scripts.export_automation import export_cron, export_json, export_markdown, export_windows, load_manifest


def test_automation_manifest_loads_tasks():
    manifest = load_manifest()

    task_ids = {task["id"] for task in manifest["tasks"]}
    assert "daily-domestic-ingest" in task_ids
    assert "daily-proxy-ingest" in task_ids
    assert "local-report-api" in task_ids


def test_automation_exports_supported_formats():
    manifest = load_manifest()

    assert "daily-domestic-ingest" in export_json(manifest)
    assert "| Task | Schedule |" in export_markdown(manifest)
    assert "scripts/run_daily.py" in export_cron(manifest)
    assert "Register-ScheduledTask" in export_windows(manifest)
    assert "07:30" in export_windows(manifest)
