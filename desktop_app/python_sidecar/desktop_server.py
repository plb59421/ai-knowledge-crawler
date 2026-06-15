"""Desktop sidecar server for the isolated desktop_app workspace.

This entry point serves the existing FastAPI report API and, when available,
the built Vite frontend from knowledge_base/exports/app. It is intentionally
kept under desktop_app/ so desktop packaging work stays isolated from the
current web/API application layout.
"""

from __future__ import annotations

import argparse
import sys
import threading
import webbrowser
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from src.utils.config_loader import get_runtime_config  # noqa: E402
from src.web_api.app import app as report_api_app  # noqa: E402

DEFAULT_FRONTEND_DIR = PROJECT_ROOT / "knowledge_base" / "exports" / "app"


def create_desktop_app(frontend_dir: str | Path = DEFAULT_FRONTEND_DIR) -> FastAPI:
    """Create the desktop FastAPI app with report API routes and a UI route."""
    frontend_path = Path(frontend_dir)
    app = FastAPI(title="AI Knowledge Crawler Desktop", version="0.1.0")
    app.include_router(report_api_app.router)

    assets_path = frontend_path / "assets"
    if assets_path.exists():
        app.mount("/assets", StaticFiles(directory=assets_path), name="assets")

    @app.get("/", include_in_schema=False)
    def index():
        index_path = frontend_path / "index.html"
        if index_path.exists():
            return FileResponse(index_path)
        return HTMLResponse(_fallback_page())

    return app


def _fallback_page() -> str:
    return """<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>AI Knowledge Crawler Desktop</title>
    <style>
      body { font-family: system-ui, sans-serif; margin: 0; line-height: 1.6; color: #172033; background: #f7f8fb; }
      header { padding: 28px 36px; background: #111827; color: white; }
      main { padding: 24px 36px; }
      button { border: 1px solid #c8d1df; background: white; padding: 8px 12px; cursor: pointer; }
      button.active { background: #175cd3; color: white; border-color: #175cd3; }
      .tabs { display: flex; gap: 8px; margin-bottom: 16px; }
      .card { background: white; border: 1px solid #d9e0ea; border-radius: 8px; padding: 16px; margin: 12px 0; }
      .meta { color: #5b6575; font-size: 14px; }
      .score { font-weight: 700; color: #175cd3; }
      .hidden { display: none; }
      a { color: #175cd3; }
    </style>
  </head>
  <body>
    <header>
      <h1>AI Knowledge Crawler Desktop</h1>
      <p>Desktop sidecar is running. Built frontend was not found, so this lightweight built-in view is active.</p>
    </header>
    <main>
      <nav class="tabs">
        <button id="general-tab" class="active">技术资讯</button>
        <button id="academic-tab">学术论文</button>
      </nav>
      <section id="status">正在加载报告数据...</section>
      <section id="general"></section>
      <section id="academic" class="hidden"></section>
    </main>
    <script>
      const generalTab = document.querySelector("#general-tab");
      const academicTab = document.querySelector("#academic-tab");
      const general = document.querySelector("#general");
      const academic = document.querySelector("#academic");
      function activate(name) {
        general.classList.toggle("hidden", name !== "general");
        academic.classList.toggle("hidden", name !== "academic");
        generalTab.classList.toggle("active", name === "general");
        academicTab.classList.toggle("active", name === "academic");
      }
      generalTab.addEventListener("click", () => activate("general"));
      academicTab.addEventListener("click", () => activate("academic"));
      function renderArticle(article, index) {
        const title = article.url ? `<a href="${article.url}" target="_blank" rel="noreferrer">${article.title}</a>` : article.title;
        return `<article class="card">
          <div class="meta">#${index + 1} · ${article.source} · ${article.publish_date || "未知日期"} · <span class="score">${Number(article.rank_score || 0).toFixed(1)}</span></div>
          <h2>${title}</h2>
          <p>${article.summary?.one_sentence || article.abstract || "暂无摘要"}</p>
          <p class="meta">${article.rank_reason || ""}</p>
        </article>`;
      }
      fetch("/api/report", { cache: "no-store" })
        .then((response) => response.json())
        .then((payload) => {
          document.querySelector("#status").textContent = `生成日期：${payload.date || ""}，技术资讯 ${payload.general.length} 篇，学术论文 ${payload.academic.length} 篇`;
          general.innerHTML = payload.general.map(renderArticle).join("") || "<p>暂无技术资讯</p>";
          academic.innerHTML = payload.academic.map(renderArticle).join("") || "<p>暂无学术论文</p>";
        })
        .catch((error) => {
          document.querySelector("#status").textContent = `报告加载失败：${String(error)}`;
        });
    </script>
  </body>
</html>"""


def _open_browser(url: str, disabled: bool):
    if disabled:
        return
    threading.Timer(0.8, lambda: webbrowser.open(url)).start()


def main() -> int:
    runtime_config = get_runtime_config()
    parser = argparse.ArgumentParser(description="Run AI Knowledge Crawler desktop sidecar")
    parser.add_argument("--host", default=runtime_config.get("api_host", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(runtime_config.get("api_port", 8000)))
    parser.add_argument("--frontend-dir", default=str(DEFAULT_FRONTEND_DIR))
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()

    url = f"http://{args.host}:{args.port}/"
    _open_browser(url, args.no_browser)
    uvicorn.run(create_desktop_app(args.frontend_dir), host=args.host, port=args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
