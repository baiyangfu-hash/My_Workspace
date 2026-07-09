// main.qml - V1.0.0 三轨道导航 + 深色玻璃拟物（CHG-SCPT-2026-102 T5 + CHG-107 T3 收尾）
//
// V0.6.0 W2 → V0.8.0 单轨道扁平 7 入口 → V0.9.3 三轨道分组导航 → V1.0.0 收尾落地
//
// V1.0.0 升级内容（CHG-107）：
// - 新增 LoadingOverlay 组件（异步操作加载指示，对齐 V7 .loading-overlay）
// - 新增 FutureCapability 组件（未实现功能灰化占位，对齐 V7 .future-capability）
// - WorkspaceView 文档/变量表 Tab 占位升级为 FutureCapability
// - PlatformDashboardView 集成 LoadingOverlay
// - 版本号 V0.9.3 → V1.0.0
//
// V0.9.3 升级内容（CHG-SCPT-2026-102）：
// - Header 48px → 72px + 搜索栏 + 操作按钮（对齐原型 V7 .header）
// - 侧边栏单轨道 7 入口 → 三轨道分组（Platform Cockpit / Active Project / Settings）
// - 集成 ContextCard（当前项目上下文卡片，Active Project 头部）
// - 集成 SidebarBadge（变更中心/规范中心待办数徽标）
// - 集成 BackendStatus（侧边栏底部 DB 连接状态指示灯）
// - 背景层新增 AmbientOrb 光晕装饰
// - 版本号 V0.8.0 → V0.9.3
//
// 保留约束（不破坏 138 个 qml 测试）：
// - currentPage 状态值不变：projectList/workspace/changeCenter/specCenter/reportCenter/templateManage/settings
// - StackLayout 7 个分支（0-6）和 currentIndex 映射逻辑不变
// - 7 个 view 的 id 不变：projectListView/workspaceView/changeCenterView/specCenterView/reportView/templateView/settingsView
// - onProjectClicked/onBackToProjectList 信号处理不变
// - Connections { workbenchBridge.onProjectSelected } 不变
// - Component.onCompleted 启动逻辑不变
//
// 通过 context property 访问：workbenchBridge/changeBridge/specBridge/deliveryBridge/systemBridge（5 个域 Bridge）/ projectModel（ProjectListModel）/ changeModel（ChangeListModel）

import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "theme"
import "views"
import "components"
import "dialogs"

ApplicationWindow {
    id: mainWindow
    visible: true
    width: 1280
    height: 800
    title: "auto-pm V1.0.0 (QML)"
    color: Theme.background

    // ── 当前页面状态（CHG-106 新增 platformDashboard 分支）────
    // "projectList" / "workspace" / "changeCenter" / "specCenter" / "reportCenter" / "templateManage" / "settings" / "platformDashboard"
    property string currentPage: "projectList"
    property string currentProjectId: ""
    property string currentProjectName: ""
    property string currentProjectPhase: "developing"
    property string currentProjectStack: "python"

    // ── 背景层：AmbientOrb 光晕装饰（对齐原型 V7 .ambient-orb）──
    Item {
        id: ambientLayer
        anchors.fill: parent
        z: -1

        // 左上角靛蓝光晕球（部分溢出视口）
        AmbientOrb {
            width: 480
            height: 480
            glowColor: Theme.primary
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.margins: -180
        }

        // 右下角天蓝光晕球
        AmbientOrb {
            width: 520
            height: 520
            glowColor: Theme.secondary
            anchors.bottom: parent.bottom
            anchors.right: parent.right
            anchors.margins: -200
        }
    }

    // ── 顶部标题栏（72px + 搜索栏 + 操作按钮）──────────────
    Rectangle {
        id: header
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        height: 72
        color: Qt.rgba(0.02, 0.02, 0.09, 0.85)  // 深色半透明（玻璃拟物基底）

        // 底部玻璃边框分隔线
        Rectangle {
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            height: 1
            color: Theme.glassBorder
        }

        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: Theme.spacingLg
            anchors.rightMargin: Theme.spacingLg
            spacing: Theme.spacingMd

            // 应用标识（圆形 logo + 标题 + 版本）
            Rectangle {
                Layout.preferredWidth: 40
                Layout.preferredHeight: 40
                radius: width / 2
                color: Theme.primary
                opacity: 0.9

                Text {
                    anchors.centerIn: parent
                    text: "A"
                    color: "white"
                    font.pixelSize: Theme.fontSizeXl
                    font.bold: true
                }
            }

            ColumnLayout {
                spacing: 0

                Text {
                    text: "auto-pm"
                    color: Theme.textPrimary
                    font.pixelSize: Theme.fontSizeLg
                    font.bold: true
                }

                Text {
                    text: "V1.0.0"
                    color: Theme.textMuted
                    font.pixelSize: Theme.fontSizeXs
                }
            }

            // 全局搜索栏（对齐原型 V7 .search-bar）
            TextField {
                id: globalSearch
                Layout.fillWidth: true
                Layout.maximumWidth: 480
                Layout.preferredHeight: 36
                placeholderText: "搜索项目 / 变更 / 规范..."
                color: Theme.textPrimary
                font.pixelSize: Theme.fontSizeSm
                background: Rectangle {
                    color: Theme.glassBg
                    radius: Theme.radiusMd
                    border.color: Theme.glassBorder
                    border.width: 1
                }
            }

            // 操作按钮组
            PrimaryButton {
                text: "🔄 刷新"
                type: "ghost"
                Layout.preferredHeight: 36
                onClicked: {
                    if (typeof workbenchBridge !== "undefined" && workbenchBridge !== null) {
                        workbenchBridge.refreshProjects()
                        var projects = workbenchBridge.listProjects()
                        projectModel.setProjects(projects)
                    }
                    if (typeof changeBridge !== "undefined" && changeBridge !== null && changeBridge.hasService) {
                        changeBridge.refreshChanges()
                    }
                }
            }

            // 工作空间路径指示
            Text {
                text: {
                    if (typeof workspace_root !== "undefined") {
                        return "📁 " + workspace_root
                    }
                    return ""
                }
                color: Theme.textMuted
                font.pixelSize: Theme.fontSizeXs
                elide: Text.ElideRight
                Layout.maximumWidth: 240
            }
        }
    }

    // ── 主内容区：侧边栏 + 页面 StackView ──────────────────
    RowLayout {
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: header.bottom
        anchors.bottom: statusbar.top
        spacing: 0

        // ── 侧边栏（三轨道分组导航，280px）──────────────────
        Rectangle {
            Layout.preferredWidth: Theme.sidebarWidth
            Layout.fillHeight: true
            color: Theme.sidebarBg

            // 右侧玻璃边框分隔线
            Rectangle {
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                width: 1
                color: Theme.glassBorder
            }

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: Theme.spacingMd
                spacing: Theme.spacingSm

                // ═══ 轨道 1：Platform Cockpit ════════════════════
                Text {
                    text: "PLATFORM COCKPIT 🚀"
                    color: Theme.textMuted
                    font.pixelSize: Theme.fontSizeXs
                    font.bold: true
                    font.letterSpacing: 1.5
                    Layout.topMargin: Theme.spacingSm
                }

                // 平台卡片 (ContextCard, 绑定自身 SW-2026-008)
                ContextCard {
                    Layout.fillWidth: true
                    projectId: "SW-2026-008"
                    projectName: "auto-pm 研发管理平台"
                    phase: "developing"
                    stack: "python"
                    hasProject: true
                    onClicked: {
                        mainWindow.currentPage = "platformDashboard"
                        platformDashboardView.loadData()
                    }
                }

                // 平台驾驶舱大盘入口
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 36
                    color: mainWindow.currentPage === "platformDashboard" ? Theme.primary : "transparent"
                    radius: Theme.radiusSm

                    RowLayout {
                        anchors.fill: parent
                        anchors.leftMargin: Theme.spacingSm
                        anchors.rightMargin: Theme.spacingSm
                        spacing: Theme.spacingSm

                        Text {
                            text: "📊"
                            color: mainWindow.currentPage === "platformDashboard" ? "white" : Theme.textSecondary
                            font.pixelSize: Theme.fontSizeSm
                        }

                        Text {
                            text: "平台驾驶舱大盘"
                            color: mainWindow.currentPage === "platformDashboard" ? "white" : Theme.textPrimary
                            font.pixelSize: Theme.fontSizeSm
                            Layout.fillWidth: true
                        }
                    }

                    MouseArea {
                        anchors.fill: parent
                        cursorShape: Qt.PointingHandCursor
                        onClicked: {
                            mainWindow.currentPage = "platformDashboard"
                            platformDashboardView.loadData()
                        }
                    }
                }

                // 平台变更管控入口 + Badge
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 36
                    color: mainWindow.currentPage === "changeCenter" ? Theme.primary : "transparent"
                    radius: Theme.radiusSm

                    RowLayout {
                        anchors.fill: parent
                        anchors.leftMargin: Theme.spacingSm
                        anchors.rightMargin: Theme.spacingSm
                        spacing: Theme.spacingSm

                        Text {
                            text: "🔄"
                            color: mainWindow.currentPage === "changeCenter" ? "white" : Theme.textSecondary
                            font.pixelSize: Theme.fontSizeSm
                        }

                        Text {
                            text: "平台变更管控"
                            color: mainWindow.currentPage === "changeCenter" ? "white" : Theme.textPrimary
                            font.pixelSize: Theme.fontSizeSm
                            Layout.fillWidth: true
                        }

                        SidebarBadge {
                            count: changeBridge ? changeBridge.changeCount : 0
                        }
                    }

                    MouseArea {
                        anchors.fill: parent
                        cursorShape: Qt.PointingHandCursor
                        onClicked: {
                            mainWindow.currentPage = "changeCenter"
                            changeCenterView.loadChanges()
                        }
                    }
                }

                // 平台架构规范检查入口
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 36
                    color: mainWindow.currentPage === "specCenter" ? Theme.primary : "transparent"
                    radius: Theme.radiusSm

                    RowLayout {
                        anchors.fill: parent
                        anchors.leftMargin: Theme.spacingSm
                        anchors.rightMargin: Theme.spacingSm
                        spacing: Theme.spacingSm

                        Text {
                            text: "📐"
                            color: mainWindow.currentPage === "specCenter" ? "white" : Theme.textSecondary
                            font.pixelSize: Theme.fontSizeSm
                        }

                        Text {
                            text: "平台架构规范检查"
                            color: mainWindow.currentPage === "specCenter" ? "white" : Theme.textPrimary
                            font.pixelSize: Theme.fontSizeSm
                            Layout.fillWidth: true
                        }
                    }

                    MouseArea {
                        anchors.fill: parent
                        cursorShape: Qt.PointingHandCursor
                        onClicked: {
                            mainWindow.currentPage = "specCenter"
                            specCenterView.loadOverview()
                            specCenterView.loadEntries()
                        }
                    }
                }

                // 平台迭代与发布入口
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 36
                    color: mainWindow.currentPage === "reportCenter" ? Theme.primary : "transparent"
                    radius: Theme.radiusSm

                    RowLayout {
                        anchors.fill: parent
                        anchors.leftMargin: Theme.spacingSm
                        anchors.rightMargin: Theme.spacingSm
                        spacing: Theme.spacingSm

                        Text {
                            text: "📄"
                            color: mainWindow.currentPage === "reportCenter" ? "white" : Theme.textSecondary
                            font.pixelSize: Theme.fontSizeSm
                        }

                        Text {
                            text: "平台迭代与发布"
                            color: mainWindow.currentPage === "reportCenter" ? "white" : Theme.textPrimary
                            font.pixelSize: Theme.fontSizeSm
                            Layout.fillWidth: true
                        }
                    }

                    MouseArea {
                        anchors.fill: parent
                        cursorShape: Qt.PointingHandCursor
                        onClicked: {
                            mainWindow.currentPage = "reportCenter"
                            reportView.loadData()
                        }
                    }
                }

                // ═══ 分隔线 ════════════════════════════════════
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 1
                    color: Theme.glassBorder
                    Layout.topMargin: Theme.spacingSm
                    Layout.bottomMargin: Theme.spacingSm
                }

                // ═══ 轨道 2：Workspace ══════════════════════════
                Text {
                    text: "WORKSPACE 🌐"
                    color: Theme.textMuted
                    font.pixelSize: Theme.fontSizeXs
                    font.bold: true
                    font.letterSpacing: 1.5
                }

                // 业务项目大厅入口
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 36
                    color: mainWindow.currentPage === "projectList" ? Theme.primary : "transparent"
                    radius: Theme.radiusSm

                    RowLayout {
                        anchors.fill: parent
                        anchors.leftMargin: Theme.spacingSm
                        anchors.rightMargin: Theme.spacingSm
                        spacing: Theme.spacingSm

                        Text {
                            text: "🏠"
                            color: mainWindow.currentPage === "projectList" ? "white" : Theme.textSecondary
                            font.pixelSize: Theme.fontSizeSm
                        }

                        Text {
                            text: "业务项目大厅"
                            color: mainWindow.currentPage === "projectList" ? "white" : Theme.textPrimary
                            font.pixelSize: Theme.fontSizeSm
                            Layout.fillWidth: true
                        }

                        Text {
                            text: (projectModel ? projectModel.count : 0).toString()
                            color: mainWindow.currentPage === "projectList" ? "white" : Theme.textMuted
                            font.pixelSize: Theme.fontSizeXs
                        }
                    }

                    MouseArea {
                        anchors.fill: parent
                        cursorShape: Qt.PointingHandCursor
                        onClicked: mainWindow.currentPage = "projectList"
                    }
                }

                // ═══ 分隔线 ════════════════════════════════════
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 1
                    color: Theme.glassBorder
                    Layout.topMargin: Theme.spacingSm
                    Layout.bottomMargin: Theme.spacingSm
                }

                // ═══ 轨道 3：Active Project ══════════════════════
                Text {
                    text: "ACTIVE BUSINESS PROJECT 💻"
                    color: Theme.textMuted
                    font.pixelSize: Theme.fontSizeXs
                    font.bold: true
                    font.letterSpacing: 1.5
                }

                // ContextCard：当前项目上下文卡片（Active Project 头部）
                ContextCard {
                    Layout.fillWidth: true
                    projectId: mainWindow.currentProjectId
                    projectName: mainWindow.currentProjectName
                    phase: mainWindow.currentProjectPhase
                    stack: mainWindow.currentProjectStack
                    hasProject: mainWindow.currentProjectId !== ""
                    onClicked: {
                        if (mainWindow.currentProjectId !== "") {
                            mainWindow.currentPage = "workspace"
                            workspaceView.switchTab(0)
                        } else {
                            mainWindow.currentPage = "projectList"
                        }
                    }
                }

                // 工程健康度概览
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 36
                    color: (mainWindow.currentPage === "workspace" && workspaceView.currentTabIndex === 0) ? Theme.primary : "transparent"
                    opacity: mainWindow.currentProjectId !== "" ? 1.0 : 0.4
                    radius: Theme.radiusSm

                    RowLayout {
                        anchors.fill: parent
                        anchors.leftMargin: Theme.spacingSm
                        anchors.rightMargin: Theme.spacingSm
                        spacing: Theme.spacingSm

                        Text {
                            text: "📊"
                            color: (mainWindow.currentPage === "workspace" && workspaceView.currentTabIndex === 0) ? "white" : Theme.textSecondary
                            font.pixelSize: Theme.fontSizeSm
                        }

                        Text {
                            text: "工程健康度概览"
                            color: (mainWindow.currentPage === "workspace" && workspaceView.currentTabIndex === 0) ? "white" : Theme.textPrimary
                            font.pixelSize: Theme.fontSizeSm
                            Layout.fillWidth: true
                        }
                    }

                    MouseArea {
                        anchors.fill: parent
                        cursorShape: mainWindow.currentProjectId !== "" ? Qt.PointingHandCursor : Qt.ArrowCursor
                        enabled: mainWindow.currentProjectId !== ""
                        onClicked: {
                            mainWindow.currentPage = "workspace"
                            workspaceView.switchTab(0)
                        }
                    }
                }

                // 变量表与 IO 资产
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 36
                    color: (mainWindow.currentPage === "workspace" && workspaceView.currentTabIndex === 4) ? Theme.primary : "transparent"
                    opacity: mainWindow.currentProjectId !== "" ? 1.0 : 0.4
                    radius: Theme.radiusSm

                    RowLayout {
                        anchors.fill: parent
                        anchors.leftMargin: Theme.spacingSm
                        anchors.rightMargin: Theme.spacingSm
                        spacing: Theme.spacingSm

                        Text {
                            text: "📋"
                            color: (mainWindow.currentPage === "workspace" && workspaceView.currentTabIndex === 4) ? "white" : Theme.textSecondary
                            font.pixelSize: Theme.fontSizeSm
                        }

                        Text {
                            text: "变量表与 IO 资产"
                            color: (mainWindow.currentPage === "workspace" && workspaceView.currentTabIndex === 4) ? "white" : Theme.textPrimary
                            font.pixelSize: Theme.fontSizeSm
                            Layout.fillWidth: true
                        }
                    }

                    MouseArea {
                        anchors.fill: parent
                        cursorShape: mainWindow.currentProjectId !== "" ? Qt.PointingHandCursor : Qt.ArrowCursor
                        enabled: mainWindow.currentProjectId !== ""
                        onClicked: {
                            mainWindow.currentPage = "workspace"
                            workspaceView.switchTab(4)
                        }
                    }
                }

                // 工程变更控制矩阵
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 36
                    color: (mainWindow.currentPage === "workspace" && workspaceView.currentTabIndex === 1) ? Theme.primary : "transparent"
                    opacity: mainWindow.currentProjectId !== "" ? 1.0 : 0.4
                    radius: Theme.radiusSm

                    RowLayout {
                        anchors.fill: parent
                        anchors.leftMargin: Theme.spacingSm
                        anchors.rightMargin: Theme.spacingSm
                        spacing: Theme.spacingSm

                        Text {
                            text: "🔀"
                            color: (mainWindow.currentPage === "workspace" && workspaceView.currentTabIndex === 1) ? "white" : Theme.textSecondary
                            font.pixelSize: Theme.fontSizeSm
                        }

                        Text {
                            text: "工程变更控制矩阵"
                            color: (mainWindow.currentPage === "workspace" && workspaceView.currentTabIndex === 1) ? "white" : Theme.textPrimary
                            font.pixelSize: Theme.fontSizeSm
                            Layout.fillWidth: true
                        }
                    }

                    MouseArea {
                        anchors.fill: parent
                        cursorShape: mainWindow.currentProjectId !== "" ? Qt.PointingHandCursor : Qt.ArrowCursor
                        enabled: mainWindow.currentProjectId !== ""
                        onClicked: {
                            mainWindow.currentPage = "workspace"
                            workspaceView.switchTab(1)
                        }
                    }
                }

                // 工程规范与死区检查
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 36
                    color: (mainWindow.currentPage === "workspace" && workspaceView.currentTabIndex === 2) ? Theme.primary : "transparent"
                    opacity: mainWindow.currentProjectId !== "" ? 1.0 : 0.4
                    radius: Theme.radiusSm

                    RowLayout {
                        anchors.fill: parent
                        anchors.leftMargin: Theme.spacingSm
                        anchors.rightMargin: Theme.spacingSm
                        spacing: Theme.spacingSm

                        Text {
                            text: "🛡️"
                            color: (mainWindow.currentPage === "workspace" && workspaceView.currentTabIndex === 2) ? "white" : Theme.textSecondary
                            font.pixelSize: Theme.fontSizeSm
                        }

                        Text {
                            text: "工程规范与死区检查"
                            color: (mainWindow.currentPage === "workspace" && workspaceView.currentTabIndex === 2) ? "white" : Theme.textPrimary
                            font.pixelSize: Theme.fontSizeSm
                            Layout.fillWidth: true
                        }
                    }

                    MouseArea {
                        anchors.fill: parent
                        cursorShape: mainWindow.currentProjectId !== "" ? Qt.PointingHandCursor : Qt.ArrowCursor
                        enabled: mainWindow.currentProjectId !== ""
                        onClicked: {
                            mainWindow.currentPage = "workspace"
                            workspaceView.switchTab(2)
                        }
                    }
                }

                // 工程交付与试运行报告
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 36
                    color: (mainWindow.currentPage === "workspace" && workspaceView.currentTabIndex === 3) ? Theme.primary : "transparent"
                    opacity: mainWindow.currentProjectId !== "" ? 1.0 : 0.4
                    radius: Theme.radiusSm

                    RowLayout {
                        anchors.fill: parent
                        anchors.leftMargin: Theme.spacingSm
                        anchors.rightMargin: Theme.spacingSm
                        spacing: Theme.spacingSm

                        Text {
                            text: "🚀"
                            color: (mainWindow.currentPage === "workspace" && workspaceView.currentTabIndex === 3) ? "white" : Theme.textSecondary
                            font.pixelSize: Theme.fontSizeSm
                        }

                        Text {
                            text: "工程交付与试运行报告"
                            color: (mainWindow.currentPage === "workspace" && workspaceView.currentTabIndex === 3) ? "white" : Theme.textPrimary
                            font.pixelSize: Theme.fontSizeSm
                            Layout.fillWidth: true
                        }
                    }

                    MouseArea {
                        anchors.fill: parent
                        cursorShape: mainWindow.currentProjectId !== "" ? Qt.PointingHandCursor : Qt.ArrowCursor
                        enabled: mainWindow.currentProjectId !== ""
                        onClicked: {
                            mainWindow.currentPage = "workspace"
                            workspaceView.switchTab(3)
                        }
                    }
                }

                // 弹性填充
                Item { Layout.fillHeight: true }

                // ═══ 分隔线 ════════════════════════════════════
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 1
                    color: Theme.glassBorder
                    Layout.bottomMargin: Theme.spacingSm
                }

                // ═══ 轨道 4：Settings ═══════════════════════════
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 36
                    color: mainWindow.currentPage === "settings" ? Theme.primary : "transparent"
                    radius: Theme.radiusSm

                    RowLayout {
                        anchors.fill: parent
                        anchors.leftMargin: Theme.spacingSm
                        anchors.rightMargin: Theme.spacingSm
                        spacing: Theme.spacingSm

                        Text {
                            text: "⚙️"
                            color: mainWindow.currentPage === "settings" ? "white" : Theme.textSecondary
                            font.pixelSize: Theme.fontSizeSm
                        }

                        Text {
                            text: "设置"
                            color: mainWindow.currentPage === "settings" ? "white" : Theme.textPrimary
                            font.pixelSize: Theme.fontSizeSm
                            Layout.fillWidth: true
                        }
                    }

                    MouseArea {
                        anchors.fill: parent
                        cursorShape: Qt.PointingHandCursor
                        onClicked: mainWindow.currentPage = "settings"
                    }
                }

                // BackendStatus：DB 连接状态指示灯
                BackendStatus {
                    Layout.fillWidth: true
                    Layout.topMargin: Theme.spacingSm
                    connected: typeof systemBridge !== "undefined" && systemBridge !== null && systemBridge.hasService
                }
            }
        }

        // ── 页面内容区（StackLayout，保留 7 个分支不变）──────
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
                if (mainWindow.currentPage === "platformDashboard") return 7
                return 0
            }

            // 0. 项目列表页
            ProjectListView {
                id: projectListView
                onRequestNewProject: newProjectWizard._isOpen = true
                onRequestImportProject: importProjectDialog._isOpen = true
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
                onRequestNewChange: newChangeDialog._isOpen = true
                onRequestEditChange: {
                    editChangeDialog.prefill(changeCenterView.selectedChangeDetail)
                    editChangeDialog._isOpen = true
                }
                onBackToProjectList: {
                    mainWindow.currentPage = "projectList"
                }
            }

            // 3. 规范中心页
            SpecCenterView {
                id: specCenterView
                onBackToProjectList: mainWindow.currentPage = "projectList"
            }

            // 4. 报告中心页
            ReportView {
                id: reportView
                onBackToProjectList: mainWindow.currentPage = "projectList"
            }

            // 5. 模板管理页
            TemplateView {
                id: templateView
                currentProjectId: mainWindow.currentProjectId  // 绑定当前选中项目
                onBackToProjectList: mainWindow.currentPage = "projectList"
            }

            // 6. 设置页
            SettingsView {
                id: settingsView
                onBackToProjectList: mainWindow.currentPage = "projectList"
            }

            // 7. 平台驾驶舱大盘页（CHG-106 新增）
            PlatformDashboardView {
                id: platformDashboardView
                onBackToProjectList: mainWindow.currentPage = "projectList"
            }
        }
    }

    // ── 对话框覆盖层 ────────────────────────────────────
    NewProjectWizard {
        id: newProjectWizard
        anchors.fill: parent
        z: 999
        onProjectCreated: {
            console.log("[QML main] 项目创建成功: " + projectId)
            if (typeof workbenchBridge !== "undefined" && workbenchBridge !== null) {
                workbenchBridge.refreshProjects()
                var projects = workbenchBridge.listProjects()
                projectModel.setProjects(projects)
            }
        }
    }

    ImportProjectDialog {
        id: importProjectDialog
        anchors.fill: parent
        z: 999
        onImported: {
            console.log("[QML main] 项目导入成功: " + projectId)
            if (typeof workbenchBridge !== "undefined" && workbenchBridge !== null) {
                workbenchBridge.refreshProjects()
                var projects = workbenchBridge.listProjects()
                projectModel.setProjects(projects)
            }
        }
    }

    NewChangeDialog {
        id: newChangeDialog
        anchors.fill: parent
        z: 999
        onChangeCreated: {
            console.log("[QML main] 变更单创建成功: " + changeNumber)
            if (typeof changeBridge !== "undefined" && changeBridge !== null) {
                changeBridge.refreshChanges()
                changeBridge.listAllChanges()
            }
            if (mainWindow.currentPage === "changeCenter") {
                changeCenterView.loadChanges()
            }
        }
    }

    EditChangeDialog {
        id: editChangeDialog
        anchors.fill: parent
        z: 999
        onChangeSaved: {
            console.log("[QML main] 变更单更新成功: " + changeNumber)
            if (typeof changeBridge !== "undefined" && changeBridge !== null) {
                changeBridge.refreshChanges()
                changeBridge.listAllChanges()
            }
            if (mainWindow.currentPage === "changeCenter") {
                changeCenterView.loadChanges()
                changeCenterView.loadChangeDetail(changeNumber)
            }
        }
    }

    // ── 状态栏（24px，版本号 V1.0.0）─────────────────────
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
            color: Theme.glassBorder
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
                text: "项目: " + (projectModel ? projectModel.count : 0)
                color: Theme.textSecondary
                font.pixelSize: Theme.fontSizeXs
            }

            Text {
                text: "变更: " + (changeBridge ? changeBridge.changeCount : 0)
                color: Theme.textSecondary
                font.pixelSize: Theme.fontSizeXs
            }

            Item { Layout.fillWidth: true }

            Text {
                text: "QML V1.0.0"
                color: Theme.textMuted
                font.pixelSize: Theme.fontSizeXs
            }
        }
    }

    // ── 监听 workbenchBridge.projectSelected 信号 ────────
    Connections {
        target: typeof workbenchBridge !== "undefined" && workbenchBridge !== null ? workbenchBridge : null
        function onProjectSelected(projectId, projectName) {
            mainWindow.currentProjectId = projectId
            mainWindow.currentProjectName = projectName
            mainWindow.currentPage = "workspace"
            workspaceView.setProject(projectId, projectName)
        }
    }

    // ── 启动时加载项目数据 ───────────────────────────────
    Component.onCompleted: {
        if (typeof workbenchBridge !== "undefined" && workbenchBridge !== null) {
            console.log("[QML main] workbenchBridge 可用，初始化数据...")
            var projects = workbenchBridge.listProjects()
            console.log("[QML main] 加载了 " + projects.length + " 个项目")
            projectModel.setProjects(projects)
        } else {
            console.warn("[QML main] workbenchBridge 未注入")
        }
        // 触发变更列表加载（changeCount 属性会自动更新状态栏）
        if (typeof changeBridge !== "undefined" && changeBridge !== null && changeBridge.hasService) {
            changeBridge.listAllChanges()
        }
    }
}
