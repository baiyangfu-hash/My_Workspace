// ChangeCenterView.qml - V0.6.0 W2-S3 变更中心（列表 + 详情面板）
//
// 左侧变更单 ListView（状态/编号/标题/日期/申请人），右侧详情面板。
// 数据流：bridge.listAllChanges() → changeModel → ListView → 点击 → bridge.getChangeRequest(id) → 详情面板

import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../theme"
import "../components"

Rectangle {
    id: root
    color: Theme.background

    // ── 公开状态 ────────────────────────────────────────
    property string selectedChangeNumber: ""
    property var selectedChangeDetail: ({})
    property string statusFilter: "all"
    property string domainFilter: "all"
    property string searchText: ""

    // ── 信号 ────────────────────────────────────────────
    signal backToProjectList()

    // ── 过滤后的展示模型 ────────────────────────────────
    ListModel { id: filteredModel }

    // ── 加载数据 ────────────────────────────────────────
    function loadChanges() {
        if (typeof bridge === "undefined" || bridge === null || !bridge.hasChangeService) {
            console.warn("[QML] ChangeCenterView: ChangeService 未启用")
            filteredModel.clear()
            return
        }
        console.log("[QML] ChangeCenterView: 加载变更列表...")
        var changes = bridge.listAllChanges()
        console.log("[QML] ChangeCenterView: 收到 " + changes.length + " 条变更")
        applyFilters(changes)
    }

    function applyFilters(changes) {
        var source = changes || (typeof bridge !== "undefined" && bridge !== null ? bridge.listAllChanges() : [])
        var filtered = []

        for (var i = 0; i < source.length; i++) {
            var c = source[i]
            if (root.statusFilter !== "all" && c.status !== root.statusFilter) continue
            if (root.domainFilter !== "all" && c.domain !== root.domainFilter) continue
            if (root.searchText !== "") {
                var q = root.searchText.toLowerCase()
                if (!String(c.change_number).toLowerCase().includes(q) &&
                    !String(c.title).toLowerCase().includes(q) &&
                    !String(c.project_id).toLowerCase().includes(q)) {
                    continue
                }
            }
            filtered.push(c)
        }

        filteredModel.clear()
        for (var j = 0; j < filtered.length; j++) {
            filteredModel.append(filtered[j])
        }
    }

    function loadChangeDetail(changeNumber) {
        if (typeof bridge === "undefined" || bridge === null) return
        root.selectedChangeNumber = changeNumber
        root.selectedChangeDetail = bridge.getChangeRequest(changeNumber)
        console.log("[QML] ChangeCenterView: 加载变更详情 " + changeNumber + " → " + (Object.keys(root.selectedChangeDetail).length) + " 字段")
    }

    // ── 顶部导航 ────────────────────────────────────────
    Rectangle {
        id: navBar
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        height: 88
        color: Theme.surface

        Rectangle {
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            height: 1
            color: Theme.border
        }

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: Theme.spacingMd
            spacing: Theme.spacingSm

            RowLayout {
                Layout.fillWidth: true
                spacing: Theme.spacingSm

                PrimaryButton {
                    text: "← 返回"
                    type: "ghost"
                    Layout.preferredWidth: 80
                    onClicked: root.backToProjectList()
                }

                Text {
                    text: "变更中心"
                    font.pixelSize: Theme.fontSizeXl
                    font.bold: true
                    color: Theme.textPrimary
                }

                Item { Layout.fillWidth: true }

                PrimaryButton {
                    text: "刷新"
                    type: "ghost"
                    Layout.preferredWidth: 60
                    enabled: typeof bridge !== "undefined" && bridge !== null && bridge.hasChangeService
                    onClicked: {
                        if (typeof bridge !== "undefined" && bridge !== null) {
                            bridge.refreshChanges()
                        }
                        root.loadChanges()
                    }
                }
            }

            RowLayout {
                Layout.fillWidth: true
                spacing: Theme.spacingSm

                TextField {
                    id: searchField
                    Layout.preferredWidth: 240
                    Layout.preferredHeight: 28
                    placeholderText: "搜索变更编号/标题/项目..."
                    text: root.searchText
                    onTextChanged: {
                        root.searchText = text
                        root.applyFilters()
                    }
                    color: Theme.textPrimary
                    font.pixelSize: Theme.fontSizeSm
                    background: Rectangle {
                        color: Theme.background
                        radius: Theme.radiusSm
                        border.color: Theme.border
                        border.width: 1
                    }
                }

                ComboBox {
                    Layout.preferredWidth: 120
                    Layout.preferredHeight: 28
                    model: ["全部状态", "draft", "submitted", "approved", "implementing", "completed", "closed"]
                    onCurrentIndexChanged: {
                        var map = ["all", "draft", "submitted", "approved", "implementing", "completed", "closed"]
                        root.statusFilter = map[currentIndex]
                        root.applyFilters()
                    }
                }

                ComboBox {
                    Layout.preferredWidth: 120
                    Layout.preferredHeight: 28
                    model: ["全部领域", "ELEC", "MECH", "PLC", "HMI", "SCPT", "DOCU", "SAFE"]
                    onCurrentIndexChanged: {
                        var map = ["all", "ELEC", "MECH", "PLC", "HMI", "SCPT", "DOCU", "SAFE"]
                        root.domainFilter = map[currentIndex]
                        root.applyFilters()
                    }
                }

                Item { Layout.fillWidth: true }

                Text {
                    text: "共 " + filteredModel.count + " 条"
                    font.pixelSize: Theme.fontSizeSm
                    color: Theme.textSecondary
                }
            }
        }
    }

    // ── 主内容：左列表 + 右详情 ─────────────────────────
    RowLayout {
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: navBar.bottom
        anchors.bottom: parent.bottom
        spacing: 0

        // ─── 左侧变更单列表 ────────────────────────────
        Rectangle {
            Layout.preferredWidth: 480
            Layout.fillHeight: true
            color: Theme.surface

            Rectangle {
                anchors.right: parent.right
                height: parent.height
                width: 1
                color: Theme.border
            }

            ListView {
                id: changeListView
                anchors.fill: parent
                anchors.margins: Theme.spacingSm
                clip: true
                spacing: Theme.spacingXs
                model: filteredModel

                // 空状态
                Text {
                    anchors.centerIn: parent
                    visible: filteredModel.count === 0
                    text: "暂无变更单"
                    color: Theme.textMuted
                    font.pixelSize: Theme.fontSizeLg
                }

                delegate: Rectangle {
                    width: changeListView.width
                    height: 80
                    color: root.selectedChangeNumber === model.change_number ? Theme.primary : Theme.background
                    radius: Theme.radiusSm
                    border.color: root.selectedChangeNumber === model.change_number ? Theme.primary : Theme.border
                    border.width: root.selectedChangeNumber === model.change_number ? 2 : 1

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: Theme.spacingSm
                        spacing: 2

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: Theme.spacingXs

                            Text {
                                text: model.change_number || ""
                                font.pixelSize: Theme.fontSizeSm
                                font.bold: true
                                color: root.selectedChangeNumber === model.change_number ? "white" : Theme.textPrimary
                            }

                            Item { Layout.fillWidth: true }

                            Badge {
                                text: model.status || ""
                                type: model.status || "default"
                            }
                        }

                        Text {
                            text: model.title || "(无标题)"
                            font.pixelSize: Theme.fontSizeXs
                            color: root.selectedChangeNumber === model.change_number ? "white" : Theme.textSecondary
                            elide: Text.ElideRight
                            Layout.fillWidth: true
                        }

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: Theme.spacingXs

                            Text {
                                text: model.project_id || ""
                                font.pixelSize: Theme.fontSizeXs
                                color: root.selectedChangeNumber === model.change_number ? "#cbd5e1" : Theme.textMuted
                            }

                            Item { Layout.fillWidth: true }

                            Text {
                                text: (model.applicant || "") + " " + (model.apply_date || "")
                                font.pixelSize: Theme.fontSizeXs
                                color: root.selectedChangeNumber === model.change_number ? "#cbd5e1" : Theme.textMuted
                            }
                        }
                    }

                    MouseArea {
                        anchors.fill: parent
                        cursorShape: Qt.PointingHandCursor
                        onClicked: root.loadChangeDetail(model.change_number)
                    }
                }
            }
        }

        // ─── 右侧详情面板 ──────────────────────────────
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: Theme.background

            // 空状态：未选中变更单
            Text {
                anchors.centerIn: parent
                visible: root.selectedChangeNumber === ""
                text: "← 点击左侧变更单查看详情"
                color: Theme.textMuted
                font.pixelSize: Theme.fontSizeLg
            }

            // 详情内容
            ScrollView {
                anchors.fill: parent
                anchors.margins: Theme.spacingLg
                visible: root.selectedChangeNumber !== ""
                clip: true

                ColumnLayout {
                    width: parent.width
                    spacing: Theme.spacingMd

                    // 标题
                    Text {
                        text: root.selectedChangeDetail.change_number || ""
                        font.pixelSize: Theme.fontSizeXxl
                        font.bold: true
                        color: Theme.textPrimary
                    }

                    // 状态 + 领域 + 紧急程度
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: Theme.spacingSm

                        Badge {
                            text: root.selectedChangeDetail.status || ""
                            type: root.selectedChangeDetail.status || "default"
                        }

                        Badge {
                            text: root.selectedChangeDetail.domain || ""
                            type: "default"
                        }

                        Badge {
                            text: root.selectedChangeDetail.urgency || ""
                            type: root.selectedChangeDetail.urgency === "critical" ? "critical" :
                                  (root.selectedChangeDetail.urgency === "urgent" ? "urgent" : "default")
                        }

                        Item { Layout.fillWidth: true }
                    }

                    // 基本信息
                    Card {
                        Layout.fillWidth: true
                        title: "基本信息"
                        bodyText: "变更编号: " + (root.selectedChangeDetail.change_number || "") + "\n" +
                                  "项目编号: " + (root.selectedChangeDetail.project_id || "") + "\n" +
                                  "项目名称: " + (root.selectedChangeDetail.project_name || "") + "\n" +
                                  "技术领域: " + (root.selectedChangeDetail.domain || "") + "\n" +
                                  "业务性质: " + (root.selectedChangeDetail.business_nature || "") + "\n" +
                                  "影响范围: " + ((root.selectedChangeDetail.impact_scope || []).join(", ")) + "\n" +
                                  "申请人: " + (root.selectedChangeDetail.applicant || "") + "\n" +
                                  "申请日期: " + (root.selectedChangeDetail.apply_date || "") + "\n" +
                                  "计划日期: " + (root.selectedChangeDetail.planned_date || "")
                    }

                    // 变更背景
                    Card {
                        Layout.fillWidth: true
                        title: "§4 变更背景"
                        bodyText: root.selectedChangeDetail.background || "（未填写）"
                    }

                    // 变更必要性
                    Card {
                        Layout.fillWidth: true
                        title: "§4 变更必要性"
                        bodyText: root.selectedChangeDetail.necessity || "（未填写）"
                    }

                    // 风险评估
                    Card {
                        Layout.fillWidth: true
                        title: "§6 风险评估"
                        bodyText: "风险等级: " + (root.selectedChangeDetail.risk_level || "未评估") + "\n" +
                                  "缓解措施: " + (root.selectedChangeDetail.mitigation || "未填写") + "\n" +
                                  "传播链: " + (root.selectedChangeDetail.propagation_chain || "无")
                    }

                    // 参考依据
                    Card {
                        Layout.fillWidth: true
                        title: "§4 参考依据"
                        bodyText: root.selectedChangeDetail.references || "（无）"
                    }

                    // 文件路径
                    Card {
                        Layout.fillWidth: true
                        title: "变更单文件"
                        bodyText: root.selectedChangeDetail.file_path || "（未关联文件）"
                    }
                }
            }
        }
    }

    // ── 初始加载 ────────────────────────────────────────
    Component.onCompleted: {
        loadChanges()
    }
}
