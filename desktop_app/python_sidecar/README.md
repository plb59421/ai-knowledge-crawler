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

当前 `desktop_server.py` 和 `pyinstaller.spec` 仅为占位文件，尚未实现真实打包逻辑。

---

## English

This directory stores the future desktop Python sidecar entry point and PyInstaller configuration.

### Design Boundaries

- The sidecar should reuse FastAPI, crawler, storage, and ranking logic from root-level `src/`.
- Do not duplicate business code here.
- Do not store real user config or knowledge base data here.
- Build artifacts should go to `desktop_app/build/` or ignored directories under this workspace.

Current `desktop_server.py` and `pyinstaller.spec` are placeholders only. Real packaging logic is not implemented yet.
