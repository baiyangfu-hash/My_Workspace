# auto_pm 稳定部署容器 · 双槽骨架（NG-WP-12）

本目录按《SW-2026-008"研发母体 + 稳定部署"重制实施方案》NG-WP-12 改造为受控稳定容器骨架。

## 布局

- `launcher/launch.py`：自包含 fail-closed 启动器骨架。当前仅做"解析 + 校验"（指针 → release-id → releases containment → manifest 登记），不执行 release 内代码；真实执行接线由 NG-WP-13/15 完成。
- `releases/<release-id>/`：不可变 release 槽位。当前为空（尚未部署任何 release）。
- `active_release.json` / `previous_release.json`：双槽指针，`schema_version=release_pointer.v1`，初始为 `release_id: null`（未初始化）。写指针必须经母体 `DeploymentContainer.write_pointer`（同卷临时文件 + 刷盘 + `os.replace` 原子替换）。
- `deployment_manifest.json`：`schema_version=deployment_manifest.v1`，登记每个 release 的逐文件 SHA-256；launcher 只允许启动 manifest 已登记的 release。
- `.lock`：运行期互斥文件，由 `DeploymentContainer.acquire_lock` 按需 `O_CREAT|O_EXCL` 创建、释放时删除；**骨架不预置**（预置会永久破坏互斥语义）。崩溃残留的锁需人工确认后移除。

## 状态

- 未部署任何 release（`releases/` 为空，双指针为 null）。
- 未切换运行入口：工作区根 `main.py`、`双击启动驾驶舱.bat`、`.venv` 均未改动；当前运行代码仍是本目录平铺源码，直到 NG-WP-13/15 完成入口解耦与首个正式发布。
- 母体源码真源：`01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具`（`auto_pm/application/core/deployment_service.py`）。
