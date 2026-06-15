# Tauri Desktop Shell

[中文](#中文) | [English](#english)

---

## 中文

本目录存放 Tauri 桌面壳工程。

当前已提供最小 Tauri v2 配置，窗口默认加载 `http://127.0.0.1:8000`，也就是 Python desktop sidecar 提供的本地页面。

开发前需要先启动 sidecar：

```powershell
python desktop_app/python_sidecar/desktop_server.py
```

然后在本目录安装依赖并运行：

```powershell
cd desktop_app/tauri
npm install
npm run dev
```

注意：构建 Tauri 需要 Rust/Cargo 工具链。

---

## English

This directory stores the Tauri desktop shell project.

A minimal Tauri v2 configuration is now present. The window loads `http://127.0.0.1:8000`, which is served by the Python desktop sidecar.

Start the sidecar first:

```powershell
python desktop_app/python_sidecar/desktop_server.py
```

Then install dependencies and run from this directory:

```powershell
cd desktop_app/tauri
npm install
npm run dev
```

Note: Tauri builds require the Rust/Cargo toolchain.
