// main.qml - V0.8.0 QML 主入口（V0.6.0 W2 完整版 + V0.8.0 Phase 1+2 扩展）
//
// V0.6.0 W2 扩展：
// - 完整侧边栏导航（项目列表 / 变更中心 / 规范中心 / 设置）
// - StackView 页面切换
// - 顶部工具栏（工作空间路径 + 应用标题）
// - 状态栏（项目数 / 变更数 / DB 状态）
//
// V0.8.0 Phase 1 扩展（CHG-090）：
// - 侧边栏补全 6 入口（新增报告中心 + 模板管理，激活规范中心 + 设置占位）
// - StackLayout 扩展 4 个新分支（占位 Rectangle，CHG-091 实现真实页面）
// - 版本号 V0.6.0 → V0.8.0
//
// V0.8.0 Phase 2 扩展（CHG-091）：
// - StackLayout 4 个占位 Rectangle 替换为真实页面组件
//   （SpecCenterView / ReportView / TemplateView / SettingsView）
//
// 通过 context property 访问：bridge（QmlBridge） / projectModel（ProjectListModel） / changeModel（ChangeListModel）

import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "theme"
import "views"
import "components"

ApplicationWindow {
    id: mainWindow
    visible: true
    width: 1280
    height: 800
    title: "auto-pm V0.8.0 (QML)"
    color: Theme.background

    // ── 当前页面状态 ────────────────────────────────────
    // "projectList" / "workspace" / "changeCenter" / "specCenter" / "reportCenter" / "templateManage" / "settings"
    property string currentPage: "projectList"
    property string currentProjectId: ""
    property string currentProjectName: ""

    // ── 顶部标题栏 ──────────────────────────────────────
    Rectangle {
        id: header
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        height: 48
        color: Theme.primary

        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: Theme.spacingLg
            anchors.rightMargin: Theme.spacingLg
            spacing: Theme.spacingMd

            Text {
                text: "auto-pm"
                color: "white"
                font.pixelSize: Theme.fontSizeLg
                font.bold: true
            }

            Text {
                text: "V0.8.0"
                color: "#cbd5e1"
                font.pixelSize: Theme.fontSizeSm
            }

            Item { Layout.fillWidth: true }

            Text {
                text: {
                    if (typeof workspace_root !== "undefined") {
                        return "工作空间: " + workspace_root
                    }
                    return ""
                }
                color: "#cbd5e1"
                font.pixelSize: Theme.fontSizeXs
                elide: Text.ElideRight
                Layout.maximumWidth: 600
            }
        }
    }

    // ── 主内容区：侧边栏 + 页面 StackView ──────────────
    RowLayout {
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: header.bottom
        anchors.bottom: statusbar.top
        spacing: 0

        // ── 侧边栏导航 ──────────────────────────────────
        Rectangle {
            Layout.preferredWidth: Theme.sidebarWidth
            Layout.fillHeight: true
            color: Theme.sidebarBg

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: Theme.spacingMd
                spacing: Theme.spacingSm

                Text {
                    text: "📂 导航"
                    color: "white"
                    font.pixelSize: Theme.fontSizeMd
                    font.bold: true
                    Layout.topMargin: Theme.spacingSm
                }

                // 项目列表
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 36
                    color: mainWindow.currentPage === "projectList" ? Theme.primary : "transparent"
                    radius: Theme.radiusSm

                    Text {
                        anchors.centerIn: parent
                        text: "📋 项目列表"
                        color: mainWindow.currentPage === "projectList" ? "white" : "#cbd5e1"
                        font.pixelSize: Theme.fontSizeSm
                    }

                    MouseArea {
                        anchors.fill: parent
                        cursorShape: Qt.PointingHandCursor
                        onClicked: mainWindow.currentPage = "projectList"
                    }
                }

                // 变更中心
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 36
                    color: mainWindow.currentPage === "changeCenter" ? Theme.primary : "transparent"
                    radius: Theme.radiusSm

                    Text {
                        anchors.centerIn: parent
                        text: "🔄 变更中心"
                        color: mainWindow.currentPage === "changeCenter" ? "white" : "#cbd5e1"
                        font.pixelSize: Theme.fontSizeSm
                    }

                    MouseArea {
                        anchors.fill: parent
                        cursorShape: Qt.PointingHandCursor
                        onClicked: mainWindow.currentPage = "changeCenter"
                    }
                }

                // 规范中心（V0.8.0 Phase 1 激活，CHG-090）
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 36
                    color: mainWindow.currentPage === "specCenter" ? Theme.primary : "transparent"
                    radius: Theme.radiusSm

                    Text {
                        anchors.centerIn: parent
                        text: "📐 规范中心"
                        color: mainWindow.currentPage === "specCenter" ? "white" : "#cbd5e1"
                        font.pixelSize: Theme.fontSizeSm
                    }

                    MouseArea {
                        anchors.fill: parent
                        cursorShape: Qt.PointingHandCursor
                        onClicked: mainWindow.currentPage = "specCenter"
                    }
                }

                // 报告中心（V0.8.0 Phase 1 新增，CHG-090）
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 36
                    color: mainWindow.currentPage === "reportCenter" ? Theme.primary : "transparent"
                    radius: Theme.radiusSm

                    Text {
                        anchors.centerIn: parent
                        text: "📊 报告中心"
                        color: mainWindow.currentPage === "reportCenter" ? "white" : "#cbd5e1"
                        font.pixelSize: Theme.fontSizeSm
                    }

                    MouseArea {
                        anchors.fill: parent
                        cursorShape: Qt.PointingHandCursor
                        onClicked: mainWindow.currentPage = "reportCenter"
                    }
                }

                // 模板管理（V0.8.0 Phase 1 新增，CHG-090）
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 36
                    color: mainWindow.currentPage === "templateManage" ? Theme.primary : "transparent"
                    radius: Theme.radiusSm

                    Text {
                        anchors.centerIn: parent
                        text: "📑 模板管理"
                        color: mainWindow.currentPage === "templateManage" ? "white" : "#cbd5e1"
                        font.pixelSize: Theme.fontSizeSm
                    }

                    MouseArea {
                        anchors.fill: parent
                        cursorShape: Qt.PointingHandCursor
                        onClicked: mainWindow.currentPage = "templateManage"
                    }
                }

                // 设置（V0.8.0 Phase 1 激活，CHG-090）
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 36
                    color: mainWindow.currentPage === "settings" ? Theme.primary : "transparent"
                    radius: Theme.radiusSm

                    Text {
                        anchors.centerIn: parent
                        text: "⚙️ 设置"
                        color: mainWindow.currentPage === "settings" ? "white" : "#cbd5e1"
                        font.pixelSize: Theme.fontSizeSm
                    }

                    MouseArea {
                        anchors.fill: parent
                        cursorShape: Qt.PointingHandCursor
                        onClicked: mainWindow.currentPage = "settings"
                    }
                }

                Item { Layout.fillHeight: true }

                // 项目数统计
                Text {
                    text: "项目数: " + (projectModel ? projectModel.rowCount() : 0)
                    color: "#94a3b8"
                    font.pixelSize: Theme.fontSizeXs
                }

                Text {
                    text: "变更数: " + (typeof bridge !== "undefined" && bridge !== null && bridge.hasChangeService ? bridge.listAllChanges().length : 0)
                    color: "#94a3b8"
                    font.pixelSize: Theme.fontSizeXs
                }
            }
        }

        // ── 页面内容区 ──────────────────────────────────
        StackLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            currentIndex: {
                if (mainWindow.currentPage === "projectList") return 0
                if (mainWindow.currentPage === "workspace") return 1
                if (mainWindow.currentPage === "changeCenter") return 2
                if (mainWindow.currentPage === "specCenter") return 3
                if (mainWindow.currentPage === "reportCenter") return 4
                if (mainWindow.currentPage === "templateManage") return 5
                if (mainWindow.currentPage === "settings") return 6
                return 0
            }

            // 0. 项目列表页
            ProjectListView {
                id: projectListView
                onProjectClicked: {
                    mainWindow.currentProjectId = projectId
                    mainWindow.currentProjectName = projectName
                    mainWindow.currentPage = "workspace"
                    workspaceView.setProject(projectId, projectName)
                }
            }

            // 1. 项目工作区页
            WorkspaceView {
                id: workspaceView
                onBackToProjectList: {
                    mainWindow.currentPage = "projectList"
                }
            }

            // 2. 变更中心页
            ChangeCenterView {
                id: changeCenterView
                onBackToProjectList: {
                    mainWindow.currentPage = "projectList"
                }
            }

            // 3. 规范中心页（V0.8.0 Phase 2 实现，CHG-091）
            SpecCenterView {
                id: specCenterView
                onBackToProjectList: mainWindow.currentPage = "projectList"
            }

            // 4. 报告中心页（V0.8.0 Phase 2 实现，CHG-091）
            ReportView {
                id: reportView
                onBackToProjectList: mainWindow.currentPage = "projectList"
            }

            // 5. 模板管理页（V0.8.0 Phase 2 实现，CHG-091）
            TemplateView {
                id: templateView
                onBackToProjectList: mainWindow.currentPage = "projectList"
            }

            // 6. 设置页（V0.8.0 Phase 2 实现，CHG-091）
            SettingsView {
                id: settingsView
                onBackToProjectList: mainWindow.currentPage = "projectList"
            }
        }
    }

    // ── 状态栏 ──────────────────────────────────────────
    Rectangle {
        id: statusbar
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        height: 24
        color: Theme.surface

        Rectangle {
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            height: 1
            color: Theme.border
        }

        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: Theme.spacingMd
            anchors.rightMargin: Theme.spacingMd
            spacing: Theme.spacingMd

            Text {
                text: "● 就绪"
                color: Theme.success
                font.pixelSize: Theme.fontSizeXs
            }

            Text {
                text: "项目: " + (projectModel ? projectModel.rowCount() : 0)
                color: Theme.textSecondary
                font.pixelSize: Theme.fontSizeXs
            }

            Text {
                text: "变更: " + (typeof bridge !== "undefined" && bridge !== null && bridge.hasChangeService ? bridge.listAllChanges().length : "N/A")
                color: Theme.textSecondary
                font.pixelSize: Theme.fontSizeXs
            }

            Item { Layout.fillWidth: true }

            Text {
                text: "QML V0.8.0"
                color: Theme.textMuted
                font.pixelSize: Theme.fontSizeXs
            }
        }
    }

    // ── 监听 bridge.projectSelected 信号 ────────────────
    Connections {
        target: typeof bridge !== "undefined" && bridge !== null ? bridge : null
        function onProjectSelected(projectId, projectName) {
            mainWindow.currentProjectId = projectId
            mainWindow.currentProjectName = projectName
            mainWindow.currentPage = "workspace"
            workspaceView.setProject(projectId, projectName)
        }
    }

    // ── 启动时加载项目数据 ──────────────────────────────
    Component.onCompleted: {
        if (typeof bridge !== "undefined" && bridge !== null) {
            console.log("[QML main] bridge 可用，初始化数据...")
            var projects = bridge.listProjects()
            console.log("[QML main] 加载到 " + projects.length + " 个项目")
            projectModel.setProjects(projects)
        } else {
            console.warn("[QML main] bridge 未注入")
        }
    }
}
