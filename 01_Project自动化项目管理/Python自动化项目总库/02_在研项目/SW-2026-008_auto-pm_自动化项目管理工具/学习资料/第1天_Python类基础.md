# 第 1 天：Python 类基础

> 目标：能看懂 auto-pm 的 Facade 类，能加一个新方法
> 时间：2-3 小时
> 前置：会基本的 Python（def 函数、if/for、变量）

---

## 一、为什么需要类？

你写 PLC 程序时，一个 FB（功能块）包含：

- 输入引脚（数据进來）
- 输出引脚（数据出去）
- 内部变量（FB 自己用的）
- 逻辑代码（FB 执行的功能）

Python 的 `class` 就是这个概念：

```
PLC 的 FB              Python 的 class
─────────              ─────────────
FB 名称                 class 类名
输入引脚                 __init__ 的参数
输出引脚                 方法的返回值
内部变量                 self.属性
FB 逻辑                  def 方法()
```

---

## 二、最简单的类

```python
# 定义一个类（像定义一个 FB 的模板）
class ProjectMgr:
  
    # __init__ 是初始化方法，像 FB 的"上电第一个扫描周期"
    # 创建对象时自动执行，用来设置初始值
    def __init__(self, workspace_path):
        self.workspace = workspace_path    # 存到内部变量
        self.project_count = 0             # 初始值
  
    # 这是一个方法，像 FB 里的一个功能逻辑
    def count_projects(self):
        # self.workspace 就是上面 __init__ 里存的值
        print(f"在 {self.workspace} 下扫描项目...")
        self.project_count = 10
        return self.project_count


# ===== 使用这个类 =====

# 创建对象（像在 OB1 里调用 FB 实例）
mgr = ProjectMgr("C:\\我的工作空间")

# 调用方法
result = mgr.count_projects()
print(f"找到 {result} 个项目")
```

### 关键点

| 概念     | 语法                          | PLC 对应        |
| -------- | ----------------------------- | --------------- |
| 定义类   | `class 类名:`               | 定义 FB         |
| 初始化   | `def __init__(self, 参数):` | FB 上电初始化   |
| 内部变量 | `self.变量名 = 值`          | FB 的静态变量   |
| 方法定义 | `def 方法名(self, 参数):`   | FB 的功能逻辑   |
| 创建对象 | `mgr = 类名(参数)`          | OB1 里实例化 FB |
| 调用方法 | `mgr.方法名()`              | 调用 FB 实例    |

---

## 三、self 是什么？

`self` 就是"我自己"——当前这个对象自己。

```python
class Student:
    def __init__(self, name, age):
        self.name = name    # 把传进来的 name 存到"我"的 name 属性
        self.age = age      # 把传进来的 age 存到"我"的 age 属性
  
    def say_hello(self):
        # self.name 意思是"我的 name"
        print(f"我叫 {self.name}，今年 {self.age} 岁")

# 创建两个不同的对象
s1 = Student("张三", 18)
s2 = Student("李四", 20)

s1.say_hello()   # 输出：我叫 张三，今年 18 岁
s2.say_hello()   # 输出：我叫 李四，今年 20 岁
```

**理解要点**：

- `self` 不是关键字，是约定俗成的名字
- 调用 `s1.say_hello()` 时，Python 自动把 `s1` 传给 `self`
- 所以方法里 `self.name` 就是 `s1.name`

---

## 四、看懂 auto-pm 的代码

打开 `auto_pm/application/workbench_facade.py`，你会看到类似这样的结构：

```python
class WorkbenchFacade:
    """FB_Workbench 功能块 - 项目管理"""
  
    def __init__(self, project_service, dashboard_service, template_service):
        # 输入引脚：接收三个 Service（底层库函数）
        self._project_service = project_service
        self._dashboard_service = dashboard_service
        self._template_service = template_service
  
    def list_project_cards(self, workspace_root):
        """列出所有项目卡片"""
        # 调用底层 Service 获取数据
        projects = self._project_service.list_projects(workspace_root)
        # 处理数据
        cards = [self._to_card(p) for p in projects]
        # 返回结果（输出引脚）
        return QueryResult(success=True, data=cards)
  
    def create_project(self, project_id, name, stack, mode):
        """创建新项目"""
        result = self._project_service.create_project(...)
        return CommandResult(success=True, message=result.message)
```

### 读懂这段代码

1. `class WorkbenchFacade:` — 定义了一个类（FB）
2. `__init__` — 初始化，接收 3 个 Service 作为输入引脚
3. `self._project_service = project_service` — 把 Service 存到内部变量
4. `list_project_cards` — 一个方法，返回项目列表
5. `self._project_service.list_projects()` — 调用内部 Service 的方法

---

## 五、练习题

### 练习 1：创建一个简单的类

在项目根目录创建 `练习.py`，写一个 `FbCounter` 类：

```python
class FbCounter:
    """计数器功能块"""
  
    def __init__(self, initial_value=0):
        self.count = initial_value
  
    def increment(self):
        """加 1"""
        self.count += 1
        return self.count
  
    def reset(self):
        """清零"""
        self.count = 0
        return self.count
  
    def get_value(self):
        """获取当前值"""
        return self.count


# 测试你的类
counter = FbCounter(10)
print(counter.increment())  # 应该输出 11
print(counter.increment())  # 应该输出 12
print(counter.reset())     # 应该输出 0
print(counter.get_value()) # 应该输出 0
```

运行方式：

```powershell
& "c:\Users\fubai\Desktop\My_Workspace\.venv\Scripts\Activate.ps1"
cd "...\SW-2026-008_auto-pm_自动化项目管理工具"
python 练习.py
```

### 练习 2：看懂 Facade 代码

打开 `auto_pm/application/workbench_facade.py`，回答：

1. `WorkbenchFacade` 的 `__init__` 接收几个参数？
2. `list_project_cards` 方法调用了哪个 `self._xxx`？
3. `create_project` 方法返回什么类型？

### 练习 3：加一个方法

在 `WorkbenchFacade` 类里，复制 `list_project_cards` 的结构，加一个方法：

```python
def hello_world(self):
    """测试方法"""
    return QueryResult(success=True, data="你好，世界")
```

然后在终端测试：

```powershell
python -c "from auto_pm.application.workbench_facade import WorkbenchFacade; print(WorkbenchFacade.__init__.__code__.co_varnames)"
```

---

## 六、今天学到的

- [ ] `class 类名:` 定义类
- [ ] `__init__` 是初始化方法
- [ ] `self` 是当前对象自己
- [ ] `self.属性` 存内部变量
- [ ] `对象.方法()` 调用方法
- [ ] 能看懂 `workbench_facade.py` 的基本结构

---

## 七、明天预习

明天学 QML，打开这个文件看看：
`auto_pm/ui/qml/views/ProjectListView.qml`

不用看懂，先感受一下 QML 长什么样。
