// WorkspaceView.qml - V0.6.0 W2-S2 项目工作区（5 Tab）
//
// 项目工作区主页面，使用 TabBar 组件实现 5 个 Tab：
// - 概览 Tab：项目元信息卡片网格
// - 变更 Tab：项目变更单 ListView + 状态徽标
// - 检查 Tab：specmgr 报告渲染
// - 文档 Tab：文档树 + Markdown 渲染（占位）
// - 变量表 Tab：变量表编辑器（占位，W3 实现）
//
// 数据流：bridge.projectSelected 信号 → setProject(projectId, projectName) → 加载各 Tab 数据

import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../theme"
import "../components"

Rectangle {
    id: root
    color: Theme.background

    // ── 公开属性 ────────────────────────────────────────
    property string currentProjectId: ""
    property string currentProjectName: ""
    property var currentProjectDetail: ({})  // bridge.getProjectById 返回的 dict
    property var changesList: []              // 当前项目的变更列表
    property var specCheckResult: ({})        // 规范检查结果

    // ── 信号 ────────────────────────────────────────────
    signal backToProjectList()

    // ── 加载项目数据 ────────────────────────────────────
    function setProject(projectId, projectName) {
        root.currentProjectId = projectId
        root.currentProjectName = projectName
        console.log("[QML] WorkspaceView: 加载项目 " + projectId + " - " + projectName)

        // 加载项目详情
        if (typeof bridge !== "undefined" && bridge !== null) {
            root.currentProjectDetail = bridge.getProjectById(projectId)
            console.log("[QML] WorkspaceView: 项目详情 " + (Object.keys(root.currentProjectDetail).length) + " 字段")

            // 加载项目变更列表
            if (bridge.hasChangeService) {
                root.changesList = bridge.listChanges(projectId)
                console.log("[QML] WorkspaceView: 项目变更 " + root.changesList.length + " 条")
            } else {
                root.changesList = []
            }
        }

        // 重置 Tab 到概览
        tabBar.currentTabIndex = 0
        loadCurrentTab()
    }

    function loadCurrentTab() {
        switch (tabBar.currentTabIndex) {
            case 0: loadOverviewTab(); break
            case 1: loadChangeTab(); break
            case 2: loadCheckTab(); break
            case 3: loadDocTab(); break
            case 4: loadVarTableTab(); break
        }
    }

    function loadOverviewTab() {
        // 已通过 currentProjectDetail 加载
    }

    function loadChangeTab() {
        if (typeof bridge !== "undefined" && bridge !== null && bridge.hasChangeService) {
            root.changesList = bridge.listChanges(root.currentProjectId)
        }
    }

    function loadCheckTab() {
        if (typeof bridge !== "undefined" && bridge !== null && bridge.hasSpecService) {
            console.log("[QML] WorkspaceView: 运行规范检查...")
            root.specCheckResult = bridge.runSpecCheck()
            console.log("[QML] WorkspaceView: 规范检查完成 " +
                "error=" + (root.specCheckResult.error_count || 0) +
                " warn=" + (root.specCheckResult.warning_count || 0))
        } else {
            root.specCheckResult = {"error_count": -1, "message": "未启用规范检查服务"}
        }
    }

    function loadDocTab() {
        // W2 占位：W3 实现 Markdown 渲染
    }

    function loadVarTableTab() {
        // W2 占位：W3 实现变量表编辑器
    }

    // ── 顶部导航栏 ──────────────────────────────────────
    Rectangle {
        id: navBar
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        height: 56
        color: Theme.surface

        Rectangle {
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            height: 1
            color: Theme.border
        }

        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: Theme.spacingLg
            anchors.rightMargin: Theme.spacingLg
            spacing: Theme.spacingSm

            PrimaryButton {
                text: "← 返回"
                type: "ghost"
                Layout.preferredWidth: 80
                onClicked: root.backToProjectList()
            }

            Text {
                text: root.currentProjectName || "(未选择项目)"
                font.pixelSize: Theme.fontSizeXl
                font.bold: true
                color: Theme.textPrimary
            }

            Text {
                text: root.currentProjectId
                font.pixelSize: Theme.fontSizeSm
                color: Theme.textSecondary
                Layout.leftMargin: Theme.spacingSm
            }

            Item { Layout.fillWidth: true }

            Badge {
                text: root.currentProjectDetail.stack || ""
                type: root.currentProjectDetail.stack || "unknown"
            }

            Badge {
                text: {
                    var phaseMap = {
                        "developing": "在研",
                        "commissioning": "调试",
                        "production": "生产",
                        "archived": "归档"
                    }
                    return phaseMap[root.currentProjectDetail.phase] || "未分类"
                }
                type: root.currentProjectDetail.phase || "default"
            }

            Text {
                text: root.currentProjectDetail.version ? "v" + root.currentProjectDetail.version : "v-"
                font.pixelSize: Theme.fontSizeSm
                color: Theme.textSecondary
            }
        }
    }

    // ── Tab 栏 ──────────────────────────────────────────
    TabBar {
        id: tabBar
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: navBar.bottom
        tabs: ["概览", "变更", "检查", "文档", "变量表"]
        onCurrentTabChanged: loadCurrentTab()
    }

    // ── Tab 内容区（StackLayout 切换） ─────────────────
    Rectangle {
        id: tabContent
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: tabBar.bottom
        anchors.bottom: parent.bottom
        color: "transparent"

        // ─── 概览 Tab ────────────────────────────────────
        Rectangle {
            id: overviewTab
            anchors.fill: parent
            visible: tabBar.currentTabIndex === 0
            color: "transparent"

            ScrollView {
                anchors.fill: parent
                anchors.margins: Theme.spacingLg
                clip: true

                GridLayout {
                    width: parent.width
                    columns: 3
                    rowSpacing: Theme.spacingMd
                    columnSpacing: Theme.spacingMd

                    // 基本信息
                    Card {
                        Layout.columnSpan: 3
                        Layout.fillWidth: true
                        title: "基本信息"
                        bodyText: "项目编号: " + (root.currentProjectDetail.project_id || "") + "\n" +
                                  "项目名称: " + (root.currentProjectDetail.name || "") + "\n" +
                                  "技术栈: " + (root.currentProjectDetail.stack || "") + "\n" +
                                  "阶段: " + (root.currentProjectDetail.phase || "") + "\n" +
                                  "版本: " + (root.currentProjectDetail.version || "") + "\n" +
                                  "业务线: " + (root.currentProjectDetail.business_line || "")
                    }

                    // PLC 信息
                    Card {
                        Layout.fillWidth: true
                        title: "PLC 信息"
                        bodyText: "PLC 品牌: " + (root.currentProjectDetail.plc_vendor || "未配置") + "\n" +
                                  "PLC 型号: " + (root.currentProjectDetail.plc_model || "未配置") + "\n" +
                                  "设备类型: " + (root.currentProjectDetail.equipment_type || "未配置")
                    }

                    // 项目类型
                    Card {
                        Layout.fillWidth: true
                        title: "项目分类"
                        bodyText: "项目类型: " + (root.currentProjectDetail.project_type || "未配置") + "\n" +
                                  "业务线: " + (root.currentProjectDetail.business_line || "")
                    }

                    // 描述
                    Card {
                        Layout.fillWidth: true
                        title: "项目描述"
                        bodyText: root.currentProjectDetail.description || "暂无描述"
                    }

                    // 路径
                    Card {
                        Layout.columnSpan: 3
                        Layout.fillWidth: true
                        title: "项目路径"
                        bodyText: root.currentProjectDetail.path || ""
                    }
                }
            }
        }

        // ─── 变更 Tab ────────────────────────────────────
        Rectangle {
            id: changeTab
            anchors.fill: parent
            visible: tabBar.currentTabIndex === 1
            color: "transparent"

            ListView {
                id: changeListView
                anchors.fill: parent
                anchors.margins: Theme.spacingLg
                clip: true
                spacing: Theme.spacingSm
                model: root.changesList

                // 空状态
                Text {
                    anchors.centerIn: parent
                    visible: root.changesList.length === 0
                    text: "该项目暂无变更单"
                    color: Theme.textMuted
                    font.pixelSize: Theme.fontSizeLg
                }

                delegate: Rectangle {
                    width: changeListView.width
                    height: 64
                    color: Theme.surface
                    radius: Theme.radiusMd
                    border.color: Theme.border
                    border.width: 1

                    RowLayout {
                        anchors.fill: parent
                        anchors.margins: Theme.spacingMd
                        spacing: Theme.spacingSm

                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 2

                            Text {
                                text: modelData.change_number || ""
                                font.pixelSize: Theme.fontSizeMd
                                font.bold: true
                                color: Theme.textPrimary
                            }

                            Text {
                                text: modelData.title || "(无标题)"
                                font.pixelSize: Theme.fontSizeSm
                                color: Theme.textSecondary
                                elide: Text.ElideRight
                                Layout.fillWidth: true
                            }
                        }

                        Badge {
                            text: modelData.domain || ""
                            type: "default"
                        }

                        Badge {
                            text: modelData.status || ""
                            type: modelData.status || "default"
                        }

                        Text {
                            text: modelData.apply_date || ""
                            font.pixelSize: Theme.fontSizeXs
                            color: Theme.textMuted
                        }
                    }
                }
            }
        }

        // ─── 检查 Tab ────────────────────────────────────
        Rectangle {
            id: checkTab
            anchors.fill: parent
            visible: tabBar.currentTabIndex === 2
            color: "transparent"

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: Theme.spacingLg
                spacing: Theme.spacingMd

                // 检查摘要
                Card {
                    Layout.fillWidth: true
                    title: "规范检查报告"
                    bodyText: {
                        var r = root.specCheckResult
                        if (r.error_count === -1) {
                            return "未启用规范检查服务或检查失败"
                        }
                        return "错误: " + (r.error_count || 0) + "\n" +
                               "警告: " + (r.warning_count || 0) + "\n" +
                               "信息: " + (r.info_count || 0) + "\n" +
                               "退出码: " + (r.exit_code || 0)
                    }
                }

                PrimaryButton {
                    text: "重新运行检查"
                    type: "primary"
                    Layout.preferredWidth: 120
                    enabled: typeof bridge !== "undefined" && bridge !== null && bridge.hasSpecService
                    onClicked: loadCheckTab()
                }

                // 检查结果列表
                ListView {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    clip: true
                    spacing: Theme.spacingXs
                    model: root.specCheckResult.results || []

                    delegate: Rectangle {
                        width: parent ? parent.width : 0
                        height: 56
                        color: Theme.surface
                        radius: Theme.radiusSm
                        border.color: Theme.border
                        border.width: 1

                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: Theme.spacingSm
                            spacing: 2

                            RowLayout {
                                spacing: Theme.spacingSm

                                Badge {
                                    text: modelData.severity || ""
                                    type: modelData.severity === "ERROR" ? "critical" :
                                          (modelData.severity === "WARNING" ? "urgent" : "default")
                                }

                                Text {
                                    text: modelData.check_id || ""
                                    font.pixelSize: Theme.fontSizeXs
                                    font.bold: true
                                    color: Theme.textSecondary
                                }

                                Text {
                                    text: modelData.message || ""
                                    font.pixelSize: Theme.fontSizeSm
                                    color: Theme.textPrimary
                                    elide: Text.ElideRight
                                    Layout.fillWidth: true
                                }
                            }

                            Text {
                                text: modelData.details || ""
                                font.pixelSize: Theme.fontSizeXs
                                color: Theme.textMuted
                                elide: Text.ElideRight
                                visible: (modelData.details || "") !== ""
                                Layout.fillWidth: true
                            }
                        }
                    }
                }
            }
        }

        // ─── 文档 Tab（W2 占位） ─────────────────────────
        Rectangle {
            id: docTab
            anchors.fill: parent
            visible: tabBar.currentTabIndex === 3
            color: "transparent"

            Text {
                anchors.centerIn: parent
                text: "文档 Tab\n\nW3 实现：\n- 文档树（项目目录结构）\n- Markdown 渲染\n- 自动区标记"
                color: Theme.textMuted
                font.pixelSize: Theme.fontSizeLg
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }
        }

        // ─── 变量表 Tab（W2 占位） ───────────────────────
        Rectangle {
            id: varTableTab
            anchors.fill: parent
            visible: tabBar.currentTabIndex === 4
            color: "transparent"

            Text {
                anchors.centerIn: parent
                text: "变量表 Tab\n\nW3 实现：\n- QML TableView 8 列\n- 单元格编辑 + 校验\n- 批量操作 + 撤销重做\n- 万行虚拟化"
                color: Theme.textMuted
                font.pixelSize: Theme.fontSizeLg
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }
        }
    }
}
