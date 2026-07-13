# 第 3 天：Signal/Slot 通信

> 目标：理解 QML 画面和 Python 后台怎么互相通信
> 时间：2-3 小时
> 前置：第 1 天 Python class + 第 2 天 QML 基础

---

## 一、整体架构（复习）

```
┌─────────────────────────────────┐
│  QML 画面（HMI）                 │
│  ProjectListView.qml            │
│       ↕ 怎么通信？                │
├─────────────────────────────────┤
│  Bridge（HMI 变量表）             │
│  workbench_bridge.py            │
│       ↕ Python 方法调用          │
├─────────────────────────────────┤
│  Facade（FB 功能块）              │
│  workbench_facade.py            │
│       ↕                          │
├─────────────────────────────────┤
│  Service（SFB 库函数）           │
│  project_service.py             │
└─────────────────────────────────┘
```

今天解决的核心问题：**QML 画面和 Bridge 怎么互相通信？**

---

## 二、三个通信工具

| 工具 | 方向 | 用途 | PLC 对应 |
|------|------|------|----------|
| `@Slot` | QML → Python | QML 画面调用 Python 方法 | HMI 按钮触发脚本 |
| `Signal` | Python → QML | Python 通知 QML 数据变了 | PLC 变量变化事件 |
| `@Property` | Python → QML | QML 读取 Python 属性 | HMI 只读变量 |

---

## 三、@Slot：QML 调用 Python

### 最简单的例子

```python
# workbench_bridge.py
from PySide6.QtCore import QObject, Slot

class WorkbenchBridge(QObject):
    """HMI 变量表 - 画面能调用的方法"""
    
    @Slot(str)           # 声明：接收一个字符串参数
    def selectProject(self, project_id):
        """QML 画面调用这个方法选择项目"""
        print(f"选择了项目：{project_id}")
        # 调用 Facade 处理业务逻辑
        result = self._facade.select_project(project_id)
        return result
```

```qml
// ProjectListView.qml
Button {
    text: "选择项目"
    onClicked: {
        // QML 调用 Python 的 @Slot 方法
        bridge.selectProject("DJ-2026-001")
    }
}
```

### @Slot 参数类型

```python
@Slot()                    # 无参数
@Slot(str)                 # 一个字符串
@Slot(str, str)            # 两个字符串
@Slot(str, int)            # 字符串 + 整数
@Slot(bool)                # 布尔值
@Slot(str, result=bool)    # 有返回值（返回布尔）
```

### 常见用法

```python
class WorkbenchBridge(QObject):
    
    @Slot(str)
    def createProject(self, name):
        """创建项目"""
        result = self._facade.create_project(name)
        return result.success
    
    @Slot()
    def refreshList(self):
        """刷新列表（无参数无返回值）"""
        self._facade.refresh()
    
    @Slot(str, result=str)
    def getProjectName(self, project_id):
        """查询项目名称，返回字符串"""
        return self._facade.get_name(project_id)
```

---

## 四、Signal：Python 通知 QML

当 Python 后台数据变了，怎么通知 QML 画面刷新？用 `Signal`。

### 最简单的例子

```python
from PySide6.QtCore import QObject, Signal, Slot

class WorkbenchBridge(QObject):
    """HMI 变量表"""
    
    # 定义信号（像 PLC 的变量变化事件）
    projectsChanged = Signal()           # 无参数信号
    statusMessageChanged = Signal(str)   # 带一个字符串参数
    
    @Slot()
    def refreshProjects(self):
        """刷新项目列表"""
        # 从后台获取数据
        projects = self._facade.list_projects()
        
        # 存数据
        self._projects = projects
        
        # 发射信号 → QML 画面会收到通知
        self.projectsChanged.emit()
        self.statusMessageChanged.emit(f"加载了 {len(projects)} 个项目")
```

```qml
// ProjectListView.qml

Page {
    // 监听信号
    Connections {
        target: bridge                        // 监听 bridge 对象
        
        function onProjectsChanged() {        // 信号名加 on 前缀
            // 信号触发时执行
            console.log("项目列表变了，刷新画面")
            projectList.model = bridge.getProjects()
        }
        
        function onStatusMessageChanged(message) {
            // 带参数的信号
            statusText.text = message
        }
    }
    
    Text {
        id: statusText
        text: "就绪"
    }
}
```

### Signal 命名规则

```
Python 信号名:  projectsChanged
QML 监听方法名:  onProjectsChanged   （加 on 前缀，首字母大写）

Python 信号名:  statusMessageChanged
QML 监听方法名:  onStatusMessageChanged
```

---

## 五、@Property：QML 读取属性

QML 画面可以直接绑定 Python 的属性，数据变了自动刷新。

```python
from PySide6.QtCore import Property

class WorkbenchBridge(QObject):
    
    # 信号（属性变化时通知 QML）
    projectNameChanged = Signal()
    
    def __init__(self):
        self._project_name = ""
    
    # 读属性
    @Property(str, notify=projectNameChanged)
    def projectName(self):
        return self._project_name
    
    # 写属性（可选）
    @projectName.setter
    def projectName(self, value):
        if self._project_name != value:
            self._project_name = value
            self.projectNameChanged.emit()  # 通知 QML
```

```qml
// QML 里直接用
Text {
    text: bridge.projectName    // 绑定属性，自动刷新
}
```

---

## 六、完整流程：一次按钮点击

以"新建项目"为例，走通全链路：

```
第 1 步：用户在 QML 画面点击"新建项目"按钮

// QML（ProjectListView.qml）
Button {
    text: "新建项目"
    onClicked: {
        bridge.createProject("DJ-2026-001", "测试项目", "plc", "standard")
    }
}

第 2 步：Bridge 收到调用，转发给 Facade

# Python（workbench_bridge.py）
@Slot(str, str, str, str, result=bool)
def createProject(self, project_id, name, stack, mode):
    result = self._facade.create_project(project_id, name, stack, mode)
    return result.success

第 3 步：Facade 调用 Service 处理业务逻辑

# Python（workbench_facade.py）
def create_project(self, project_id, name, stack, mode):
    result = self._project_service.create_project(...)
    if result.success:
        # 创建成功后，发射信号通知 QML 刷新列表
        self.projectsChanged.emit()
    return result

第 4 步：QML 收到信号，刷新画面

// QML
Connections {
    target: bridge
    function onProjectsChanged() {
        listView.model = bridge.getProjects()  // 重新加载列表
    }
}
```

---

## 七、看懂 auto-pm 的 Bridge

打开 `auto_pm/ui/qml/bridges/workbench_bridge.py`：

### 找这些内容

1. **Signal 定义**：在类开头找 `xxxChanged = Signal()`
2. **@Slot 方法**：找 `@Slot` 装饰器
3. **@Property**：找 `@Property` 装饰器

### 对照 QML 看调用

打开 `auto_pm/ui/qml/views/ProjectListView.qml`：

1. 搜索 `bridge.` — 这是 QML 调用 Bridge 的 @Slot 方法
2. 搜索 `Connections` — 这是 QML 监听 Bridge 的 Signal
3. 搜索 `bridge.xxx` 在 Text/Button 的绑定中 — 这是读取 @Property

---

## 八、练习题

### 练习 1：追踪一个调用链

打开 `workbench_bridge.py`，找 `createProject` 方法：

1. 它是 `@Slot` 吗？接收什么参数？
2. 它调用了 `self._facade` 的哪个方法？
3. 打开 `workbench_facade.py`，找到那个方法
4. 它调用了 `self._project_service` 的哪个方法？

把这条链路写下来：
```
QML: bridge.createProject(...)
  → Bridge: createProject()
    → Facade: create_project()
      → Service: ???
```

### 练习 2：找信号

打开 `workbench_bridge.py`，找所有 `Signal` 定义：

```python
xxxChanged = Signal()
yyyChanged = Signal(str)
```

然后打开对应的 QML 文件，搜索 `Connections`，看 QML 怎么监听这些信号。

### 练习 3：加一个 Slot

在 `workbench_bridge.py` 加一个测试方法：

```python
@Slot(result=str)
def helloBridge(self):
    """测试方法"""
    return "Hello from Bridge"
```

然后在 QML 里调用：
```qml
Button {
    text: "测试"
    onClicked: {
        console.log(bridge.helloBridge())
    }
}
```

运行 GUI，点按钮，看终端输出。

---

## 九、今天学到的

- [ ] `@Slot` = QML 画面调用 Python 方法
- [ ] `Signal` = Python 通知 QML 数据变了
- [ ] `@Property` = QML 绑定 Python 属性
- [ ] Signal 在 QML 里用 `on + 信号名` 监听
- [ ] 完整链路：QML → Bridge → Facade → Service
- [ ] 能看懂 auto-pm 的 Bridge 代码

---

## 十、明天实战

明天你要从零加一个完整功能：
- 改 QML 加按钮
- 改 Bridge 加 Slot
- 改 Facade 加方法
- 运行验证

今天学的东西明天全用上。
