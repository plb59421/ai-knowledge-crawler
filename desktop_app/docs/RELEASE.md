# Desktop Release Notes

[中文](#中文) | [English](#english)

---

## 中文

本文定义桌面应用公开发布前的检查项。当前仅作为发布规范草案。

### 发布前检查

- 安装包不包含真实 API Key、用户知识库或日志。
- 安装后首次启动可以创建用户数据目录。
- 升级安装不覆盖用户配置和知识库。
- 卸载流程不误删用户导出的知识库数据。
- 应用内设置页能提示缺失 API Key。
- 爬虫失败、模型失败和代理失败都有可读错误。

### 验证命令

```powershell
python -m compileall -q src scripts
pytest
cd web/report
npm.cmd run build
```

桌面打包命令将在真实 Tauri/PyInstaller 流程实现后补充。

---

## English

This document defines checks before publicly releasing the desktop app. It is currently a release policy draft.

### Pre-release Checks

- Installer contains no real API keys, user knowledge base data, or logs.
- First launch can create the user data directory.
- Upgrades do not overwrite user configuration or the knowledge base.
- Uninstall flow does not accidentally delete user-exported knowledge data.
- The settings page can clearly prompt for a missing API key.
- Crawler, model, and proxy failures have readable errors.

### Validation Commands

```powershell
python -m compileall -q src scripts
pytest
cd web/report
npm.cmd run build
```

Desktop packaging commands will be added after the real Tauri/PyInstaller pipeline is implemented.
