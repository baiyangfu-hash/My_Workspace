// DashboardStateMachine.qml - 平台驾驶舱 4 节点状态机（CHG-106 T4）
//
// 对齐 V7 原型 .state-machine（012_UI架构原型_V7.html L1038-1059）
// 4 节点：Draft → Review → Implementing → Closed
// 含进度条 + 当前节点脉冲动画
//
// 用法：
//   DashboardStateMachine {
//       title: "主线流转 (CHG-106)"
//       tagText: "V1.0 迭代"
//       stateMachine: bridge.getActiveChangeStatus("SW-2026-008").state_machine
//   }

import QtQuick
import QtQuick.Layouts
import "../theme"

GlassPanel {
    id: root

    // ── 公开属性 ────────────────────────────────────────
    property string title: "主线流转"  // 标题
    property string tagText: ""        // 右上角标签
    property var stateMachine: ({      // 状态机数据（来自 getActiveChangeStatus）
        "current_node": 0,
        "current_node_name": "",
        "progress": 0,
        "nodes": []
    })

    implicitHeight: 200

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        // ── 头部：标题 + 标签 ────────────────────────────
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 52
            color: "transparent"

            // 底部分隔线
            Rectangle {
                anchors.bottom: parent.bottom
                anchors.left: parent.left
                anchors.right: parent.right
                height: 1
                color: Theme.glassBorder
            }

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: Theme.spacingLg
                anchors.rightMargin: Theme.spacingLg
                spacing: Theme.spacingSm

                Text {
                    text: "🔀 " + root.title
                    color: Theme.textPrimary
                    font.pixelSize: Theme.fontSizeLg
                    font.bold: true
                    Layout.fillWidth: true
                }

                // 标签胶囊
                Rectangle {
                    visible: root.tagText !== ""
                    Layout.maximumWidth: 250
                    Layout.preferredWidth: Math.min(250, tagLabel.implicitWidth + 16)
                    height: 24
                    radius: 12
                    color: Theme.primary

                    Text {
                        id: tagLabel
                        anchors.fill: parent
                        anchors.leftMargin: 8
                        anchors.rightMargin: 8
                        verticalAlignment: Text.AlignVCenter
                        horizontalAlignment: Text.AlignHCenter
                        text: root.tagText
                        color: "white"
                        font.pixelSize: Theme.fontSizeSm
                        elide: Text.ElideRight
                    }
                }
            }
        }

        // ── 状态机主体 ────────────────────────────────────
        Item {
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.margins: Theme.spacingLg

            // 背景线（从第一节点中心到末节点中心）
            Rectangle {
                id: bgLine
                anchors.verticalCenter: parent.verticalCenter
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.leftMargin: parent.width / 8
                anchors.rightMargin: parent.width / 8
                height: 2
                color: Theme.glassBorder
                radius: 1
            }

            // 进度线（从第一节点到当前进度位置）
            Rectangle {
                id: progressLine
                anchors.verticalCenter: parent.verticalCenter
                anchors.left: bgLine.left
                height: 2
                width: bgLine.width * (root.stateMachine.progress / 100)
                color: Theme.primary
                radius: 1

                Behavior on width {
                    NumberAnimation { duration: 400; easing.type: Easing.OutCubic }
                }
            }

            // 4 节点行
            Row {
                anchors.fill: parent

                Repeater {
                    model: root.stateMachine.nodes

                    Item {
                        width: parent.width / 4
                        height: parent.height

                        // 节点圆圈
                        Rectangle {
                            id: circle
                            anchors.horizontalCenter: parent.horizontalCenter
                            anchors.verticalCenter: parent.verticalCenter
                            width: 40
                            height: 40
                            radius: 20
                            color: modelData.status === "pending" ? Theme.surface : Theme.primary
                            border.color: modelData.status === "pending" ? Theme.glassBorder : Theme.primary
                            border.width: modelData.status === "active" ? 2 : 1

                            // 脉冲动画（仅 active 节点）
                            SequentialAnimation on scale {
                                running: modelData.status === "active"
                                loops: Animation.Infinite
                                NumberAnimation { to: 1.1; duration: 800; easing.type: Easing.InOutSine }
                                NumberAnimation { to: 1.0; duration: 800; easing.type: Easing.InOutSine }
                            }

                            // 节点图标
                            Text {
                                anchors.centerIn: parent
                                text: _nodeIcon(modelData.name || "")
                                color: modelData.status === "pending" ? Theme.textMuted : "white"
                                font.pixelSize: 18
                                font.bold: true
                            }
                        }

                        // 节点标签
                        Text {
                            anchors.top: circle.bottom
                            anchors.topMargin: Theme.spacingSm
                            anchors.horizontalCenter: parent.horizontalCenter
                            text: modelData.name || ""
                            color: modelData.status === "active" ? Theme.primary :
                                   modelData.status === "done" ? Theme.textSecondary : Theme.textMuted
                            font.pixelSize: Theme.fontSizeSm
                            font.bold: modelData.status === "active"
                        }
                    }
                }
            }
        }
    }

    // ── 辅助函数 ────────────────────────────────────────
    function _nodeIcon(name: string): string {
        if (name.indexOf("Draft") >= 0) return "✏"
        if (name.indexOf("Review") >= 0) return "📤"
        if (name.indexOf("Implementing") >= 0) return "💻"
        if (name.indexOf("Closed") >= 0) return "✓"
        return "•"
    }
}
