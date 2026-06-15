# Desktop App Workspace

[中文](#中文) | [English](#english)

---

## 中文

`desktop_app/` 是 EXE 桌面应用的独立工作区。它用于存放桌面壳、安装包配置、Python sidecar 打包配置、桌面专用资源和发布文档。

### 边界

- 当前主项目目录不迁移：`src/`、`scripts/`、`web/report/` 保持原结构。
- 桌面应用通过 sidecar 调用现有 FastAPI 和爬虫能力，不复制业务逻辑。
- 不在本目录提交真实 API Key、运行时知识库、日志或安装产物。
- 所有桌面专用启动、安装、图标、打包和发布文件都应放在本目录内。

### 目录结构

```text
desktop_app/
├── docs/              打包、发布、升级和故障排查文档
├── frontend/          桌面专用前端适配层
├── python_sidecar/    Python sidecar 和 PyInstaller 相关文件
├── resources/         图标、默认配置模板和首启资源
├── tauri/             Tauri 桌面壳相关文件
└── build/             本地构建输出目录，不提交产物
```

### 当前状态

本目录已经包含可运行的 Python desktop sidecar：

```powershell
python desktop_app/python_sidecar/desktop_server.py
```

它会启动本地 API、托管已构建的前端页面，并自动打开浏览器。如果前端尚未构建，请先执行：

```powershell
cd web/report
npm.cmd run build
```

Tauri 桌面壳已提供最小工程配置，但本机需要安装 Rust/Cargo 后才能继续构建原生窗口应用。

---

## English

`desktop_app/` is the isolated workspace for the EXE desktop application. It stores the desktop shell, installer configuration, Python sidecar packaging files, desktop-specific resources, and release documentation.

### Boundaries

- Existing project directories stay where they are: `src/`, `scripts/`, and `web/report/` are not moved.
- The desktop app calls existing FastAPI and crawler capabilities through a sidecar; it does not duplicate business logic.
- Do not commit real API keys, runtime knowledge base data, logs, or installer artifacts here.
- Desktop-specific startup, installer, icon, packaging, and release files should live inside this directory.

### Directory Structure

```text
desktop_app/
├── docs/              Packaging, release, upgrade, and troubleshooting docs
├── frontend/          Desktop-specific frontend adapter layer
├── python_sidecar/    Python sidecar and PyInstaller-related files
├── resources/         Icons, default config templates, and first-run resources
├── tauri/             Tauri desktop shell files
└── build/             Local build output directory; artifacts are ignored
```

### Current Status

This directory now includes a runnable Python desktop sidecar:

```powershell
python desktop_app/python_sidecar/desktop_server.py
```

It starts the local API, serves the built frontend, and opens the browser automatically. If the frontend has not been built yet, run:

```powershell
cd web/report
npm.cmd run build
```

A minimal Tauri shell is present, but Rust/Cargo must be installed before building the native desktop window.
