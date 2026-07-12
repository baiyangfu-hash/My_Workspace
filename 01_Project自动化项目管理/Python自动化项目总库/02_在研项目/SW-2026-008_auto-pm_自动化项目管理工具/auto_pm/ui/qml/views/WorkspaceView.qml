// WorkspaceView.qml - V0.6.0 W2-S2 项目工作区（5 Tab）
//
// 项目工作区主页面，使用 TabBar 组件实现 5 个 Tab
// - 概览 Tab：项目元信息卡片网格
// - 变更 Tab：项目变更单 ListView + 状态徽章
// - 检查 Tab：specmgr 报告渲染
// - 文档 Tab：文档树 + Markdown 渲染（占位）
// - 变量表 Tab：变量表编辑器（占位，W3 实现）
//
// 数据流：workbenchBridge.projectSelected 信号 → setProject(projectId, projectName) → 加载各 Tab 数据

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
    property var currentProjectDetail: ({})  // workbenchBridge.getProjectById 返回的 dict
    property var changesList: []              // 当前项目的变更列表
    property var selectedChangeDetail: ({})   // 选中的变更详情（CHG-123：驾驶舱模式）
    property var specCheckResult: ({})        // 规范检查结果
    property var assetSummary: ({})           // 资产汇总（仅 PLC 项目）
    property alias currentTabIndex: tabBar.currentTabIndex

    // ── 变更Tab辅助属性（CHG-123：驾驶舱模式）─────────────────
    property var _changeSummary: ({})         // 变更聚合摘要（后端预计算）
    property string searchKeyword: ""         // 搜索关键字
    property string selectedStatusFilter: "ALL" // 状态过滤
    property string selectedDomainFilter: "ALL" // 领域过滤

    // 过滤后的变更单列表模型
    readonly property var filteredChangesList: {
        var list = root.changesList || []
        return list.filter(function(item) {
            // 1. 过滤搜索关键字
            var kw = root.searchKeyword.trim().toLowerCase()
            if (kw !== "") {
                var chgNum = (item.change_number || "").toLowerCase()
                var title = (item.title || "").toLowerCase()
                if (chgNum.indexOf(kw) === -1 && title.indexOf(kw) === -1) {
                    return false
                }
            }
            // 2. 过滤技术领域
            if (root.selectedDomainFilter !== "ALL") {
                if ((item.domain || "").toUpperCase() !== root.selectedDomainFilter) {
                    return false
                }
            }
            // 3. 过滤状态
            if (root.selectedStatusFilter !== "ALL") {
                if ((item.status || "").toLowerCase() !== root.selectedStatusFilter.toLowerCase()) {
                    return false
                }
            }
            return true
        })
    }

    onSearchKeywordChanged: autoSelectFirstChange()
    onSelectedStatusFilterChanged: autoSelectFirstChange()
    onSelectedDomainFilterChanged: autoSelectFirstChange()

    function autoSelectFirstChange() {
        if (root.filteredChangesList && root.filteredChangesList.length > 0) {
            if (typeof changeBridge !== "undefined" && changeBridge !== null && changeBridge.hasService) {
                root.selectedChangeDetail = changeBridge.getChangeRequest(root.filteredChangesList[0].change_number, root.currentProjectId) || {}
            }
        } else {
            root.selectedChangeDetail = {}
        }
    }

    // 基于选中的变更单动态计算状态机，确保流转状态和当前选中变更单绝对一致
    readonly property var _currentChangeStateMachine: {
        var status = "draft"
        if (root.selectedChangeDetail && root.selectedChangeDetail.status) {
            status = root.selectedChangeDetail.status
        } else if (root.filteredChangesList && root.filteredChangesList.length > 0) {
            status = root.filteredChangesList[0].status
        }
        return _computeStateMachineForStatus(status)
    }

    readonly property string _currentChangeNumber: {
        if (root.selectedChangeDetail && root.selectedChangeDetail.change_number) {
            return root.selectedChangeDetail.change_number
        } else if (root.filteredChangesList && root.filteredChangesList.length > 0) {
            return root.filteredChangesList[0].change_number
        }
        return ""
    }

    function _computeStateMachineForStatus(status) {
        var statusOrder = [
            "draft", "submitted", "under_review", "approved", "implementing",
            "pending_acceptance", "accepting", "completed", "closed"
        ]
        var statusNames = {
            "draft": "草稿",
            "submitted": "已提交",
            "under_review": "审核中",
            "approved": "已批准",
            "implementing": "实施中",
            "pending_acceptance": "待验收",
            "accepting": "验收中",
            "completed": "已完成",
            "closed": "已关闭"
        }
        var latestStatus = status || "draft"
        var latestIdx = statusOrder.indexOf(latestStatus)
        if (latestIdx === -1) latestIdx = 0

        var nodes = []
        for (var i = 0; i < statusOrder.length; i++) {
            var nodeStatus = statusOrder[i]
            nodes.push({
                "name": statusNames[nodeStatus],
                "status": nodeStatus,
                "active": nodeStatus === latestStatus,
                "completed": i <= latestIdx
            })
        }

        return {
            "current_node": latestIdx + 1,
            "current_node_name": statusNames[latestStatus] || latestStatus,
            "progress": ((latestIdx + 1) / statusOrder.length) * 100,
            "nodes": nodes
        }
    }

    // ── 信号 ────────────────────────────────────────────
    signal backToProjectList()
    signal requestEditProject()
    signal requestDeleteProject()
    signal requestApplyTemplate()

    // ── 加载项目数据 ────────────────────────────────────
    function setProject(projectId, projectName) {
        root.currentProjectId = projectId
        root.currentProjectName = projectName
        console.log("[QML] WorkspaceView: 加载项目 " + projectId + " - " + projectName)

        // 加载项目详情
        if (typeof workbenchBridge !== "undefined" && workbenchBridge !== null) {
            root.currentProjectDetail = workbenchBridge.getProjectById(projectId)
            console.log("[QML] WorkspaceView: 项目详情 " + (Object.keys(root.currentProjectDetail).length) + " 字段")

            // 加载项目变更列表
            if (changeBridge.hasService) {
                root.changesList = changeBridge.listChanges(projectId)
                console.log("[QML] WorkspaceView: 项目变更 " + root.changesList.length + " 条")
            } else {
                root.changesList = []
            }
        }

        // 重置 Tab 到概览
        tabBar.currentTabIndex = 0
        loadCurrentTab()

        // 加载资产汇总（仅 PLC 项目）
        loadAssetSummary()
    }

    function loadAssetSummary() {
        // M5: 资产汇总卡片接入 deliveryBridge.getAssetSummary
        if (typeof deliveryBridge === "undefined" || deliveryBridge === null || !deliveryBridge.hasService) {
            root.assetSummary = {}
            return
        }
        if (root.currentProjectDetail.stack !== "plc") {
            root.assetSummary = {}  // 仅 PLC 项目支持资产汇总
            return
        }
        var res = deliveryBridge.getAssetSummary(root.currentProjectId)
        if (res && res.data) {
            root.assetSummary = res.data
            console.log("[QML] WorkspaceView: 资产汇总加载 status=" + (res.data.status || "unknown"))
        } else {
            root.assetSummary = {}
        }
    }

    function switchTab(index) {
        tabBar.currentTabIndex = index
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
        if (typeof changeBridge !== "undefined" && changeBridge !== null && changeBridge.hasService) {
            root.changesList = changeBridge.listChanges(root.currentProjectId)
            console.log("[QML] WorkspaceView: 项目变更 " + root.changesList.length + " 条")
        }

        if (typeof workbenchBridge !== "undefined" && workbenchBridge !== null && workbenchBridge.hasService) {
            root._changeSummary = workbenchBridge.getProjectChangeSummary(root.currentProjectId) || {}
            console.log("[QML] WorkspaceView: 变更聚合摘要加载完成, kpi.total=" +
                (root._changeSummary.kpi ? root._changeSummary.kpi.total : 0))
        } else {
            root._changeSummary = {}
        }

        // 默认加载变更列表第一项的详情，以便右侧详情和状态流转能同步正确显示
        if (root.changesList.length > 0) {
            if (typeof changeBridge !== "undefined" && changeBridge !== null && changeBridge.hasService) {
                root.selectedChangeDetail = changeBridge.getChangeRequest(root.changesList[0].change_number, root.currentProjectId) || {}
            }
        } else {
            root.selectedChangeDetail = {}
        }
    }

    function loadCheckTab() {
        if (typeof specBridge !== "undefined" && specBridge !== null && specBridge.hasService) {
            console.log("[QML] WorkspaceView: 运行规范检查...")
            root.specCheckResult = specBridge.runSpecCheck(root.currentProjectId)
            console.log("[QML] WorkspaceView: 规范检查完成: " +
                "error=" + (root.specCheckResult.error_count || 0) +
                " warn=" + (root.specCheckResult.warning_count || 0))
        } else {
            root.specCheckResult = {"error_count": -1, "message": "未启用规范检查服务"}
        }
    }

    function loadDocTab() {
        console.log("[QML] WorkspaceView: 加载文档目录, projectId=" + root.currentProjectId)
        if (docBrowser) {
            docBrowser.loadDocs()
        }
    }

    function loadVarTableTab() {
        console.log("[QML] WorkspaceView: 加载变量表, projectId=" + root.currentProjectId)
        if (typeof deliveryBridge !== "undefined" && deliveryBridge !== null && deliveryBridge.hasService) {
            deliveryBridge.loadVarTable(root.currentProjectId, varTableModel)
        }
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
                text: "‹返回"
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

            // M4 CHG-115: 项目管理操作按钮
            PrimaryButton {
                text: "编辑"
                type: "ghost"
                Layout.preferredWidth: 60
                onClicked: root.requestEditProject()
            }

            PrimaryButton {
                text: "模板"
                type: "ghost"
                Layout.preferredWidth: 60
                onClicked: root.requestApplyTemplate()
            }

            PrimaryButton {
                text: "删除"
                type: "danger"
                Layout.preferredWidth: 60
                onClicked: root.requestDeleteProject()
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

    // ── Tab 内容区（StackLayout 切换）─────────────────
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

                    // 路径（CHG-111：自定义内容区，支持换行+选择+复制）
                    Card {
                        Layout.columnSpan: 3
                        Layout.fillWidth: true
                        title: "项目路径"

                        ColumnLayout {
                            Layout.fillWidth: true
                            height: implicitHeight
                            spacing: Theme.spacingSm

                            TextEdit {
                                Layout.fillWidth: true
                                text: root.currentProjectDetail.path || ""
                                color: Theme.textPrimary
                                font.pixelSize: Theme.fontSizeSm
                                wrapMode: TextEdit.WrapAnywhere
                                readOnly: true
                                selectByMouse: true
                                activeFocusOnPress: true
                                persistentSelection: true
                            }
                        }
                    }

                    // 资产汇总（仅 PLC 项目显示，CHG-111 布局重构 + M5 CHG-116 验证已接入）
                    Card {
                        Layout.columnSpan: 3
                        Layout.fillWidth: true
                        visible: root.currentProjectDetail.stack === "plc"
                        title: "资产汇总"

                        ColumnLayout {
                            Layout.fillWidth: true
                            height: implicitHeight
                            spacing: Theme.spacingMd

                            // 第一行：状态标签 + 问题数 Badge
                            RowLayout {
                                Layout.fillWidth: true
                                spacing: Theme.spacingSm

                                Text {
                                    text: {
                                        var s = root.assetSummary.status || "未加载"
                                        var labelMap = {
                                            "healthy": "健康",
                                            "warning": "告警",
                                            "missing": "缺失",
                                            "not_applicable": "不适用"
                                        }
                                        return "状态: " + (labelMap[s] || s)
                                    }
                                    font.pixelSize: Theme.fontSizeSm
                                    color: Theme.textPrimary
                                    Layout.fillWidth: true
                                }

                                Badge {
                                    text: {
                                        return root.assetSummary.total_issues || 0
                                    }
                                    type: {
                                        var s = root.assetSummary.status || ""
                                        if (s === "healthy") return "approved"
                                        if (s === "warning") return "urgent"
                                        if (s === "missing") return "critical"
                                        return "default"
                                    }
                                }
                            }

                            // 第二行：刷新按钮
                            PrimaryButton {
                                text: "刷新资产数据"
                                type: "primary"
                                Layout.preferredWidth: 120
                                enabled: typeof deliveryBridge !== "undefined" && deliveryBridge !== null && deliveryBridge.hasService
                                onClicked: {
                                    var res = deliveryBridge.refreshAssetSummary(root.currentProjectId)
                                    if (res && res.result) {
                                        root.assetSummary = res.result
                                        console.log("[QML] 资产汇总刷新完成")
                                    } else if (res && res.message) {
                                        console.warn("[QML] 资产汇总刷新失败: " + res.message)
                                    }
                                }
                            }

                            // 分隔线
                            Rectangle {
                                Layout.fillWidth: true
                                height: 1
                                color: Theme.glassBorder
                                visible: root.assetSummary && Object.keys(root.assetSummary).length > 0
                            }

                            // 资产详情
                            Text {
                                Layout.fillWidth: true
                                visible: root.assetSummary && Object.keys(root.assetSummary).length > 0
                                text: {
                                    var a = root.assetSummary
                                    if (!a || Object.keys(a).length === 0) {
                                        return "点击刷新加载资产数据"
                                    }
                                    var io = a.io_points || {}
                                    var blk = a.program_blocks || {}
                                    var comm = a.communications || {}
                                    return "IO 点数: " + (io.count || 0) + "（" + (io.exists ? "已配置" : "缺失") + "）\n" +
                                           "程序块: " + (blk.count || 0) + "（" + (blk.exists ? "已配置" : "缺失") + "）\n" +
                                           "通讯通道: " + (comm.count || 0) + "（" + (comm.exists ? "已配置" : "缺失") + "）\n" +
                                           "问题总数: " + (a.total_issues || 0)
                                }
                                font.pixelSize: Theme.fontSizeSm
                                color: Theme.textPrimary
                                wrapMode: Text.WordWrap
                            }

                            // 空状态提示
                            Text {
                                Layout.fillWidth: true
                                visible: !root.assetSummary || Object.keys(root.assetSummary).length === 0
                                text: "点击刷新加载资产数据"
                                font.pixelSize: Theme.fontSizeSm
                                color: Theme.textMuted
                            }

                            // 问题列表（若有）
                            Text {
                                Layout.fillWidth: true
                                visible: (root.assetSummary.issue_messages || []).length > 0
                                text: {
                                    var msgs = root.assetSummary.issue_messages || []
                                    return "问题明细:\n" + msgs.join("\n")
                                }
                                font.pixelSize: Theme.fontSizeXs
                                color: Theme.error
                                wrapMode: Text.WordWrap
                            }
                        }
                    }
                }
            }
        }

        // ─── 变更 Tab（CHG-123：驾驶舱模式）───────────────
        Rectangle {
            id: changeTab
            anchors.fill: parent
            visible: tabBar.currentTabIndex === 1
            color: "transparent"

            ScrollView {
                anchors.fill: parent
                anchors.margins: Theme.spacingLg
                clip: true

                ColumnLayout {
                    width: parent.width - 16
                    spacing: Theme.spacingLg
                    // CHG-123: 主体：状态流转与近期活动垂直平铺铺满宽度 (对齐 V10 原型设计)
                    DashboardStateMachine {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 180
                        title: root.changesList.length > 0 ? "变更状态流转" : "暂无变更"
                        tagText: root._currentChangeNumber
                        stateMachine: root._currentChangeStateMachine
                    }

                    ActivityTimeline {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 220
                        activities: root._changeSummary.activities || []
                    }

                    // CHG-123: 变更列表 + 详情面板（Split View）
                    RowLayout {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 520
                        spacing: Theme.spacingLg

                    // 左侧：变更列表
                    Rectangle {
                        Layout.preferredWidth: root.width * 0.5 - Theme.spacingLg
                        Layout.fillHeight: true
                        color: Theme.surface
                        radius: Theme.radiusMd
                        border.color: Theme.border
                        border.width: 1

                        ColumnLayout {
                            anchors.fill: parent
                            spacing: Theme.spacingSm

                            // 列表标题
                            RowLayout {
                                Layout.fillWidth: true
                                anchors.leftMargin: Theme.spacingMd
                                anchors.rightMargin: Theme.spacingMd
                                anchors.topMargin: Theme.spacingMd

                                Text {
                                    text: "变更列表"
                                    font.pixelSize: Theme.fontSizeMd
                                    font.bold: true
                                    color: Theme.textPrimary
                                }

                                Item { Layout.fillWidth: true }

                                Text {
                                    text: "共 " + root.filteredChangesList.length + " 条"
                                    font.pixelSize: Theme.fontSizeSm
                                    color: Theme.textMuted
                                }
                            }
                            // V11: 过滤搜索工具栏 (Search textfield + dropdown ComboBoxes)
                            RowLayout {
                                Layout.fillWidth: true
                                Layout.leftMargin: Theme.spacingMd
                                Layout.rightMargin: Theme.spacingMd
                                spacing: Theme.spacingSm

                                TextField {
                                    id: searchInput
                                    Layout.fillWidth: true
                                    Layout.preferredHeight: 28
                                    placeholderText: "搜索变更单号/标题..."
                                    font.pixelSize: Theme.fontSizeSm
                                    color: Theme.textPrimary
                                    background: Rectangle {
                                        color: Theme.glassBg
                                        radius: Theme.radiusSm
                                        border.color: Theme.glassBorder
                                        border.width: 1
                                    }
                                    onTextChanged: root.searchKeyword = text
                                }

                                ComboBox {
                                    id: statusCombo
                                    Layout.preferredWidth: 100
                                    Layout.preferredHeight: 28
                                    model: ["全部状态", "草稿", "已提交", "审核中", "已批准", "实施中", "已完成", "已关闭"]
                                    property var keys: ["ALL", "draft", "submitted", "under_review", "approved", "implementing", "completed", "closed"]
                                    onCurrentIndexChanged: {
                                        root.selectedStatusFilter = keys[currentIndex]
                                    }
                                }

                                ComboBox {
                                    id: domainCombo
                                    Layout.preferredWidth: 100
                                    Layout.preferredHeight: 28
                                    model: ["全部领域", "PLC", "HMI", "ELEC", "DOCU"]
                                    property var keys: ["ALL", "PLC", "HMI", "ELEC", "DOCU"]
                                    onCurrentIndexChanged: {
                                        root.selectedDomainFilter = keys[currentIndex]
                                    }
                                }
                            }

                            // 列表内容
                            ListView {
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                clip: true
                                spacing: Theme.spacingSm
                                model: root.filteredChangesList

                                Text {
                                    anchors.centerIn: parent
                                    visible: root.filteredChangesList.length === 0
                                    text: (root.selectedDomainFilter === "ALL" && root.selectedStatusFilter === "ALL" && root.searchKeyword.trim() === "") ? "该项目暂无变更单" : "该筛选条件下暂无变更单"
                                    color: Theme.textMuted
                                    font.pixelSize: Theme.fontSizeMd
                                }

                                delegate: Rectangle {
                                    width: parent.width
                                    height: 60
                                    color: Theme.background
                                    radius: Theme.radiusSm
                                    border.color: Theme.border
                                    border.width: 1

                                    RowLayout {
                                        anchors.fill: parent
                                        anchors.margins: Theme.spacingSm
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
                                    }

                                    MouseArea {
                                        anchors.fill: parent
                                        cursorShape: Qt.PointingHandCursor
                                        onClicked: {
                                            console.log("[QML] WorkspaceView: 点击变更 " + modelData.change_number)
                                            if (typeof changeBridge !== "undefined" && changeBridge !== null && changeBridge.hasService) {
                                                root.selectedChangeDetail = changeBridge.getChangeRequest(modelData.change_number, root.currentProjectId) || {}
                                                console.log("[QML] WorkspaceView: 变更详情字段数 " + Object.keys(root.selectedChangeDetail).length)
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }

                    // 右侧：详情面板
                    ChangeDetailPanel {
                        Layout.preferredWidth: root.width * 0.5 - Theme.spacingLg
                        Layout.fillHeight: true
                        changeDetail: root.selectedChangeDetail
                        changeNumber: root.selectedChangeDetail.change_number || ""
                        projectId: root.currentProjectId
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

                RowLayout {
                    spacing: Theme.spacingMd
                    PrimaryButton {
                        text: "重新运行检查"
                        type: "primary"
                        Layout.preferredWidth: 120
                        enabled: typeof specBridge !== "undefined" && specBridge !== null && specBridge.hasService
                        onClicked: loadCheckTab()
                    }

                    PrimaryButton {
                        text: "一键修复"
                        type: "accent"
                        Layout.preferredWidth: 120
                        visible: root.currentProjectDetail.stack === "plc"
                        enabled: typeof specBridge !== "undefined" && specBridge !== null && specBridge.hasService
                        onClicked: {
                            specBridge.repairSpec(root.currentProjectId)
                            loadCheckTab()
                        }
                    }
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

        // ─── 文档 Tab ──
        Rectangle {
            id: docTab
            anchors.fill: parent
            visible: tabBar.currentTabIndex === 3
            color: "transparent"

            DocBrowserView {
                id: docBrowser
                anchors.fill: parent
                projectId: root.currentProjectId
            }
        }

        // ─── 变量表 Tab ──
        Rectangle {
            id: varTableTab
            anchors.fill: parent
            visible: tabBar.currentTabIndex === 4
            color: "transparent"

            VarTableEditorView {
                id: varTableEditor
                anchors.fill: parent
                projectId: root.currentProjectId
            }
        }
    }
}

