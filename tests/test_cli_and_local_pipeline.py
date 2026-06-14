import subprocess
import sys
import os

from scripts.local_test import run_local_pipeline


def test_cli_list_registered_sources():
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    result = subprocess.run(
        [sys.executable, "scripts/run_crawler.py", "--list"],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
    )

    assert "已注册的信息源 (14 个)" in result.stdout
    for source in [
        "huggingface", "jiqizhixin", "anthropic", "openai", "deepmind", "arxiv", "qbitai",
        "hf_daily_papers", "semantic_scholar", "openalex", "the_gradient", "baai_hub", "google_ai", "meta_ai",
    ]:
        assert source in result.stdout


def test_local_pipeline_uses_temp_knowledge_base(tmp_path):
    result = run_local_pipeline(tmp_path)

    assert result["parsed"] == 1
    assert result["stored"] == 1
    assert result["paths"]
    assert str(tmp_path) in result["paths"][0]


def test_daily_runner_dry_run():
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    result = subprocess.run(
        [sys.executable, "scripts/run_daily.py", "--group", "domestic", "--dry-run"],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
    )

    assert "daily crawl summary" in result.stdout
    assert "dry-run" in result.stdout
