# Python Sidecar

[中文](#中文) | [English](#english)

---

## 中文

本目录用于存放未来桌面版 Python sidecar 的打包入口和 PyInstaller 配置。

### 设计边界

- sidecar 应复用主项目 `src/` 中的 FastAPI、爬虫、存储和评分逻辑。
- 不在本目录复制业务代码。
- 不在本目录保存真实用户配置或知识库。
- 打包产物输出到 `desktop_app/build/` 或本目录下的忽略目录。

### 启动方式

```powershell
python desktop_app/python_sidecar/desktop_server.py
```

可选参数：

```powershell
python desktop_app/python_sidecar/desktop_server.py --host 127.0.0.1 --port 8000 --no-browser
```

`desktop_server.py` 会复用现有 `/api/report`、`/api/health` 等 API，并在根路径 `/` 托管 `knowledge_base/exports/app` 中的前端构建产物。

`pyinstaller.spec` 已提供基础打包配置，后续安装 PyInstaller 后可继续完善生成 sidecar 可执行文件。

---

## English

This directory stores the future desktop Python sidecar entry point and PyInstaller configuration.

### Design Boundaries

- The sidecar should reuse FastAPI, crawler, storage, and ranking logic from root-level `src/`.
- Do not duplicate business code here.
- Do not store real user config or knowledge base data here.
- Build artifacts should go to `desktop_app/build/` or ignored directories under this workspace.

### Run

```powershell
python desktop_app/python_sidecar/desktop_server.py
```

Optional arguments:

```powershell
python desktop_app/python_sidecar/desktop_server.py --host 127.0.0.1 --port 8000 --no-browser
```

`desktop_server.py` reuses existing APIs such as `/api/report` and `/api/health`, and serves the frontend build output from `knowledge_base/exports/app` at `/`.

`pyinstaller.spec` provides a basic packaging configuration that can be refined after PyInstaller is installed.
