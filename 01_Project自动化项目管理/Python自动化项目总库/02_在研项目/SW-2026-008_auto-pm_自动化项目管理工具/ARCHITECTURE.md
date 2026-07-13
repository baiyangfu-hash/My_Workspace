# auto-pm 架构说明（PLC/HMI 视角）

## 一句话总结

auto-pm 是一个 **Python 写的桌面工具**，用 **QML 做画面（HMI）**，用 **Python 类做功能块（FB）**。如果你会 PLC 编程，这个架构你可以直接理解。

---

## 架构层次图

```
┌─────────────────────────────────────────────────────────┐
│  HMI 画面层  (auto_pm/ui/qml/)                          │
│  ├── views/       10 个画面（像 HMI 的画面列表）         │
│  ├── components/  20+ 个控件（像 HMI 的控件库）          │
│  ├── dialogs/     16 个弹窗（像 HMI 的弹出画面）         │
│  └── theme/       主题样式                               │
│                                                         │
│  QML 通过 Signal/Slot 与变量表通信                       │
│  （像 HMI 通过 Profinet/Modbus 读写 PLC 变量）            │
└───────────────────────┬─────────────────────────────────┘
                        │ Qt Signal/Slot
┌───────────────────────▼─────────────────────────────────┐
│  HMI 变量表  (auto_pm/ui/qml/bridges/)                  │
│  ├── workbench_bridge.py  画面能调用的方法 + 数据信号     │
│  ├── change_bridge.py                                    │
│  ├── spec_bridge.py                                      │
│  ├── delivery_bridge.py                                  │
│  └── system_bridge.py                                    │
│                                                         │
│  @Slot = HMI 按钮触发的脚本                              │
│  Signal = HMI 变量变化事件（数据变了自动刷新画面）         │
│  Property = HMI 只读变量（画面直接绑定显示）              │
└───────────────────────┬─────────────────────────────────┘
                        │ Python 方法调用
┌───────────────────────▼─────────────────────────────────┐
│  FB 功能块层  (auto_pm/application/)                    │
│  ├── workbench_facade.py  FB_Workbench（项目管理）       │
│  ├── change_facade.py     FB_Change（变更管理）          │
│  ├── spec_facade.py       FB_Spec（规范检查）            │
│  ├── delivery_facade.py   FB_Delivery（交付管理）        │
│  └── system_facade.py     FB_System（系统设置）          │
│                                                         │
│  每个 FB 封装一个完整功能，有明确的输入/输出              │
│  - 输入：__init__ 参数（像 FB 的 Input 引脚）            │
│  - 输出：返回 QueryResult/CommandResult（像 Output 引脚） │
│  - 内部：调用 SFB 库函数（core/ 下的 Service）           │
└───────────────────────┬─────────────────────────────────┘
                        │ 聚合调用
┌───────────────────────▼─────────────────────────────────┐
│  SFB 库函数层  (auto_pm/core/ + change/ + spec/ + ...)  │
│  ├── ProjectService      底层项目操作（文件读写）         │
│  ├── ChangeService       变更单 CRUD                     │
│  ├── DashboardService    驾驶舱数据聚合                   │
│  ├── TemplateService     模板引擎                        │
│  └── ...（10+ 个 Service）                               │
│                                                         │
│  像 PLC 的 SFB/SFC 系统函数，被 FB 调用                  │
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────┐
│  DB 数据层  (auto_pm/db/ + models/)                     │
│  ├── models/       UDT 自定义数据类型（Project, Change） │
│  ├── db/           SQLite 数据库（持久化存储）            │
│  └── contracts/    HMI 画面数据结构（DTO）               │
└─────────────────────────────────────────────────────────┘

                    ┌──────────────────┐
                    │  OB1 组织块       │
                    │  ui/registry.py   │
                    │  FacadeRegistry   │
                    │                  │
                    │  上电初始化：      │
                    │  1. 初始化所有 DB │
                    │  2. 装配所有 FB   │
                    │  3. 注入 HMI 上下文│
                    └──────────────────┘
```

---

## 概念对照表

| 你要做的事 | PLC/HMI 怎么做 | auto-pm 怎么做 |
|-----------|---------------|---------------|
| 看代码结构 | 打开 TIA Portal 项目树 | 看上面的架构图 |
| 改画面布局 | 打开 HMI 画面编辑器，拖控件 | 编辑 `hmi/views/Screen_*.qml` |
| 改业务逻辑 | 打开 FB，改 SCL 代码 | 编辑 `application/*_facade.py` |
| 改底层数据操作 | 打开 DB，改数据结构 | 编辑 `core/*_service.py` |
| 查画面能调什么方法 | 看 HMI 变量表 | 看 `ui/qml/bridges/*_bridge.py` 的 @Slot |
| 新增一个功能 | 新建 FB + 新建画面 + 在 OB1 注册 | 新建 Facade + 新建 QML + 在 registry.py 注册 |
| 数据怎么从后台到画面 | DB → FB → HMI 变量表 → 画面刷新 | Service → Facade → Bridge Signal → QML 刷新 |

---

## 数据流详解

### 画面读数据（像 HMI 读取 PLC 变量）

```
QML 画面调用 bridge.listProjects()
  → Bridge 调用 facade.list_project_cards()
    → Facade 调用 project_service.list_projects()
      → Service 读文件/数据库
    ← 返回项目列表
  ← 返回 DTO 数据
← Bridge 发射 projectsChanged 信号
← QML 收到信号，自动刷新画面
```

### 画面写数据（像 HMI 按钮触发 PLC 逻辑）

```
QML 按钮点击 → bridge.createProject(...)
  → Bridge 调用 facade.create_project(...)
    → Facade 调用 template_service + project_service
      → 创建目录、写入文件
    ← 返回结果
  ← 返回成功/失败
← Bridge 发射 projectsChanged 信号（刷新列表）
← QML 收到信号，项目列表自动更新
```

---

## 如何新增一个功能

用 PLC 的思维来新增功能，比如要加一个"备份管理"功能：

### 步骤 1：创建 UDT 数据类型（如果需要）
```
在 models/ 下定义数据结构（像 PLC 的 UDT）
```

### 步骤 2：创建 SFB 库函数
```
在 core/ 下创建 backup_service.py（像 PLC 的 SFB）
封装底层文件操作逻辑
```

### 步骤 3：创建 FB 功能块
```
在 application/ 下创建 backup_facade.py（像 PLC 的 FB）
- __init__ 接收需要的 Service（输入引脚）
- 方法返回 QueryResult/CommandResult（输出引脚）
```

### 步骤 4：创建 HMI 变量表
```
在 ui/qml/bridges/ 下创建 backup_bridge.py（像 HMI 变量表）
- @Slot 方法：QML 画面能调用的脚本
- Signal：数据变化时通知画面刷新
```

### 步骤 5：创建 HMI 画面
```
在 ui/qml/views/ 下创建 BackupView.qml（像 HMI 画面）
- 布局：拖控件 / 写 QML 代码
- 数据绑定：通过 bridge 变量读取数据
- 事件：按钮点击调用 bridge 的 @Slot 方法
```

### 步骤 6：在 OB1 注册
```
在 ui/registry.py 的 FacadeRegistry.initialize() 中：
1. 实例化新的 FB
2. 在 ui/qml_main_window.py 中注入新的 Bridge 到 QML 上下文
```

---

## 常用文件速查

| 想改什么 | 去哪个文件 |
|---------|-----------|
| 项目列表画面 | `ui/qml/views/ProjectListView.qml` |
| 新建项目逻辑 | `application/workbench_facade.py` → `create_project()` |
| 变更中心画面 | `ui/qml/views/ChangeCenterView.qml` |
| 创建变更单逻辑 | `application/change_facade.py` |
| 规范检查画面 | `ui/qml/views/SpecCenterView.qml` |
| 规范检查逻辑 | `application/spec_facade.py` |
| 驾驶舱画面 | `ui/qml/views/PlatformDashboardView.qml` |
| 驾驶舱数据 | `core/dashboard_service.py` |
| 变量表编辑器 | `ui/qml/views/VarTableEditorView.qml` |
| 变量表解析 | `vartable/` |
| 全局初始化 | `ui/registry.py`（OB1） |
| 程序入口 | `ui/qml_main_window.py` |
| CLI 命令 | `cli/` |

---

## 一句话记住每个文件

- **main.qml** = 主画面（导航框架）
- **views/*.qml** = 各个功能画面
- **bridges/*.py** = HMI 变量表（画面能调什么方法、能读什么数据）
- **application/*.py** = FB 功能块（业务逻辑）
- **core/*.py** = SFB 库函数（底层工具）
- **registry.py** = OB1（上电初始化）
- **qml_main_window.py** = 启动程序入口