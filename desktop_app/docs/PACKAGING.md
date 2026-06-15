# Desktop Packaging Notes

[中文](#中文) | [English](#english)

---

## 中文

本文记录桌面应用打包方向。当前 Python sidecar 已可运行，Tauri 安装包构建仍需要安装 Rust/Cargo 和 Tauri CLI 后继续验证。

### 目标形态

- Windows 第一版交付安装包。
- 预留 macOS/Linux 目录和配置组织方式。
- 桌面壳使用 Tauri。
- Python API 和爬虫通过 PyInstaller sidecar 提供。

### 打包边界

- 主业务代码仍在项目根目录的 `src/`、`scripts/`、`web/report/` 中维护。
- `desktop_app/` 只保存桌面壳、sidecar、资源和安装发布配置。
- 打包产物输出到 `desktop_app/build/` 或子目录下的 `dist/`、`target/`，并由 Git 忽略。

### 后续实现步骤

1. 完善 PyInstaller sidecar 构建并生成可执行文件。
2. 将 sidecar 接入 Tauri 外部二进制或启动流程。
3. 配置用户数据目录中的配置、知识库和日志路径。
4. 实现设置页、任务页和日志页。
5. 构建 Windows 安装包并验证升级不覆盖用户数据。

---

## English

This document records the desktop packaging direction. The Python sidecar is runnable now; Tauri installer builds still require Rust/Cargo and the Tauri CLI.

### Target Shape

- The first official deliverable is a Windows installer.
- macOS/Linux layout and configuration conventions are reserved.
- The desktop shell uses Tauri.
- The Python API and crawler run through a PyInstaller sidecar.

### Packaging Boundaries

- Main business code remains in root-level `src/`, `scripts/`, and `web/report/`.
- `desktop_app/` stores only the desktop shell, sidecar, resources, and installer/release configuration.
- Build artifacts go under `desktop_app/build/` or child `dist/`/`target/` directories and are ignored by Git.

### Future Implementation Steps

1. Complete the PyInstaller sidecar build and generate an executable.
2. Wire the sidecar into Tauri as an external binary or startup flow.
3. Configure user-data paths for config, knowledge base, and logs.
4. Implement settings, tasks, and logs pages.
5. Build the Windows installer and verify upgrades do not overwrite user data.
