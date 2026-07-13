# 第 2 天：QML 基础语法

> 目标：能看懂 auto-pm 的 QML 画面，能改按钮位置/文字/颜色
> 时间：2-3 小时
> 前置：第 1 天的 Python class 基础

---

## 一、QML 是什么？

QML 是 Qt 的声明式界面语言。

**命令式**（Python 写界面）：告诉电脑"怎么做"——创建按钮、设置位置、添加事件
**声明式**（QML 写界面）：告诉电脑"是什么"——这里有个按钮，它是蓝色的，点击后做什么

像 HMI 画面编辑器：你拖控件、设属性，编辑器生成描述文件。QML 就是那个描述文件。

---

## 二、QML 基本结构

```qml
// 导入模块（像 Python 的 import）
import QtQuick
import QtQuick.Controls

// 定义一个矩形（最基础的元素）
Rectangle {
    id: root                    // 给这个元素起个名字
    width: 400                   // 宽度
    height: 300                  // 高度
    color: "#f0f0f0"             // 背景色
    
    // 在矩形里放一个文字
    Text {
        id: title
        text: "项目列表"
        font.pixelSize: 24
        color: "#333333"
        anchors.top: parent.top          // 顶部对齐到父元素
        anchors.horizontalCenter: parent.horizontalCenter  // 水平居中
        anchors.topMargin: 20             // 顶部留 20 像素边距
    }
    
    // 在矩形里放一个按钮
    Button {
        text: "新建项目"
        anchors.bottom: parent.bottom
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottomMargin: 20
        
        // 点击事件
        onClicked: {
            console.log("按钮被点击了")
        }
    }
}
```

### QML 和 Python 对照

| Python | QML | 说明 |
|--------|-----|------|
| `import` | `import QtQuick` | 导入模块 |
| `class` | `Rectangle { }` | 定义一个元素 |
| 属性赋值 | `width: 400` | 设置属性 |
| 函数调用 | `anchors.centerIn: parent` | 调用布局 |
| 事件回调 | `onClicked: { }` | 事件处理 |

---

## 三、布局：怎么排列控件

### 1. Column（垂直排列）

```qml
Rectangle {
    width: 300
    height: 200
    
    Column {
        anchors.centerIn: parent
        spacing: 10        // 每个元素间距 10 像素
        
        Text { text: "第一行" }
        Text { text: "第二行" }
        Text { text: "第三行" }
    }
}
```

### 2. Row（水平排列）

```qml
Row {
    spacing: 10
    Button { text: "确定" }
    Button { text: "取消" }
}
```

### 3. anchors（锚点定位）

最常用的布局方式，像 HMI 画面的对齐工具：

```qml
Rectangle {
    width: 400
    height: 300
    
    Text {
        text: "标题"
        anchors.top: parent.top              // 顶部贴着父元素的顶部
        anchors.left: parent.left            // 左边贴着父元素的左边
        anchors.topMargin: 10                // 顶部留 10px 边距
        anchors.leftMargin: 10               // 左边留 10px 边距
    }
    
    Button {
        text: "右下角按钮"
        anchors.right: parent.right          // 右边贴着父元素右边
        anchors.bottom: parent.bottom        // 底部贴着父元素底部
        anchors.rightMargin: 10
        anchors.bottomMargin: 10
    }
    
    Text {
        text: "居中"
        anchors.centerIn: parent             // 在父元素正中间
    }
}
```

### anchors 速查

| 属性 | 效果 |
|------|------|
| `anchors.centerIn: parent` | 在父元素正中间 |
| `anchors.fill: parent` | 填满父元素 |
| `anchors.top: parent.top` | 顶部对齐 |
| `anchors.left: parent.left` | 左边对齐 |
| `anchors.right: parent.right` | 右边对齐 |
| `anchors.bottom: parent.bottom` | 底部对齐 |
| `anchors.topMargin: 20` | 顶部留 20px |
| `anchors.margins: 20` | 四周都留 20px |

---

## 四、常用控件

### 1. Text（文字）

```qml
Text {
    text: "你好世界"
    font.pixelSize: 18           // 字号
    font.bold: true              // 加粗
    color: "#ff0000"             // 红色
}
```

### 2. Button（按钮）

```qml
Button {
    text: "确定"
    enabled: true                 // 是否可用
    onClicked: {
        console.log("点击了确定")
    }
}
```

### 3. TextField（输入框）

```qml
TextField {
    placeholderText: "请输入项目名称"    // 提示文字
    text: ""                             // 当前内容
    onTextChanged: {
        console.log("输入了：" + text)
    }
}
```

### 4. ListView（列表）

```qml
ListView {
    width: 300
    height: 400
    
    // 数据源（后面会讲怎么从 Python 传数据过来）
    model: [
        { name: "项目A", id: "DJ-2026-001" },
        { name: "项目B", id: "DJ-2026-002" }
    ]
    
    // 每一行长什么样
    delegate: Rectangle {
        width: ListView.view.width
        height: 50
        color: "white"
        
        Text {
            text: modelData.name
            anchors.left: parent.left
            anchors.leftMargin: 10
            anchors.verticalCenter: parent.verticalCenter
        }
    }
}
```

---

## 五、属性绑定（重要！）

QML 最强大的功能：属性可以自动绑定，数据变了界面自动更新。

```qml
Rectangle {
    width: 400
    height: 300
    
    property int clickCount: 0        // 自定义属性
    
    Text {
        id: counter
        text: "点击次数：" + clickCount   // 绑定：clickCount 变了，text 自动变
        font.pixelSize: 20
        anchors.centerIn: parent
    }
    
    Button {
        text: "点我"
        anchors.bottom: parent.bottom
        anchors.horizontalCenter: parent.horizontalCenter
        
        onClicked: {
            clickCount++               // 改属性值
            // counter.text 会自动更新，不需要手动设置
        }
    }
}
```

---

## 六、看懂 auto-pm 的 QML

打开 `auto_pm/ui/qml/views/ProjectListView.qml`，你会看到类似这样的结构：

```qml
Page {
    title: "项目列表"
    
    // 从 Bridge 获取数据（明天学这个）
    property var projects: []
    
    ListView {
        anchors.fill: parent
        model: projects
        delegate: Card {
            // 每个项目的卡片
            Text { text: modelData.name }
            Text { text: modelData.id }
            Button {
                text: "查看"
                onClicked: {
                    bridge.selectProject(modelData.id)
                }
            }
        }
    }
    
    Button {
        text: "新建项目"
        anchors.bottom: parent.bottom
        anchors.right: parent.right
        onClicked: {
            bridge.openCreateDialog()
        }
    }
}
```

### 读懂这段代码

1. `Page { }` — 一个画面（像 HMI 的一个画面）
2. `property var projects: []` — 自定义属性，存项目列表
3. `ListView` — 列表控件
4. `model: projects` — 绑定数据源
5. `delegate: Card { }` — 每一行的样式
6. `bridge.selectProject()` — 调用 Python 后台方法（明天详讲）
7. `anchors.fill: parent` — 填满父元素

---

## 七、练习题

### 练习 1：改文字和颜色

打开 `auto_pm/ui/qml/views/ProjectListView.qml`：

1. 找到一个 `Text` 元素，把 `text` 改成中文
2. 找到一个 `Button`，把 `text` 改成"点我"
3. 找到一个颜色属性，改成 `"#ff0000"`（红色）

改完运行：
```powershell
& "c:\Users\fubai\Desktop\My_Workspace\.venv\Scripts\Activate.ps1"
python -m auto_pm gui
```

### 练习 2：加一个按钮

在 `ProjectListView.qml` 的合适位置加一个按钮：

```qml
Button {
    text: "刷新"
    anchors.bottom: parent.bottom
    anchors.left: parent.left
    anchors.margins: 10
    onClicked: {
        console.log("刷新按钮被点击")
    }
}
```

运行 GUI，看按钮是否出现，点击后看终端是否输出日志。

### 练习 3：改布局

找一个 `Column` 或 `Row`，修改 `spacing` 的值，看间距变化。

---

## 八、今天学到的

- [ ] QML 是声明式语言（描述"是什么"）
- [ ] `Rectangle`、`Text`、`Button` 是基础控件
- [ ] `Column` 垂直排列，`Row` 水平排列
- [ ] `anchors` 控制对齐和位置
- [ ] `property` 定义自定义属性
- [ ] 属性绑定：数据变了界面自动更新
- [ ] 能改 QML 画面的文字、颜色、位置

---

## 九、明天预习

明天学 Signal/Slot 通信——QML 画面怎么调用 Python 后台方法。

打开这个文件看看：
`auto_pm/ui/qml/bridges/workbench_bridge.py`

找找 `@Slot` 和 `Signal`，不用看懂，先感受。
