// NewChangeDialog.qml - 变更单新建对话框（V0.6.0 W3-S11）
//
// 表单填写变更单信息，生成 CHG-*.md 文件。
// 字段：变更号/标题/类型/影响项目/紧急程度/描述

import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../theme"
import "../components"

Item {
    id: root

    property bool _isOpen: false

    // 表单字段
    property string changeTitle: ""
    property string changeType: "feature"
    property string impactProject: ""
    property string urgency: "normal"
    property string description: ""

    // ── 信号 ────────────────────────────────────────────
    signal changeCreated(string title, string type)
    signal cancelled()

    visible: _isOpen
    anchors.fill: parent

    Rectangle {
        anchors.fill: parent
        color: "#000000"
        opacity: 0.4
        visible: root._isOpen
        MouseArea { anchors.fill: parent; onClicked: {} }
    }

    Rectangle {
        anchors.centerIn: parent
        width: 560
        height: 480
        color: Theme.background
        radius: Theme.radiusLg
        border.color: Theme.border
        border.width: 1
        visible: root._isOpen

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 0
            spacing: 0

            // 标题栏
            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 48
                color: Theme.primary
                Text {
                    anchors.centerIn: parent
                    text: "新建变更单"
                    color: "white"
                    font.pixelSize: Theme.fontSizeLg
                    font.bold: true
                }
            }

            // 表单内容
            ColumnLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.margins: Theme.spacingLg
                spacing: Theme.spacingSm

                RowLayout {
                    Layout.fillWidth: true
                    Text { text: "标题"; width: 80; color: Theme.textSecondary }
                    TextField {
                        Layout.fillWidth: true
                        placeholderText: "简明描述变更内容"
                        onTextChanged: root.changeTitle = text
                    }
                }

                RowLayout {
                    Layout.fillWidth: true
                    Text { text: "类型"; width: 80; color: Theme.textSecondary }
                    ComboBox {
                        model: ["feature", "fix", "docs", "refactor", "chore", "test"]
                        onActivated: root.changeType = currentText
                    }
                }

                RowLayout {
                    Layout.fillWidth: true
                    Text { text: "影响项目"; width: 80; color: Theme.textSecondary }
                    TextField {
                        Layout.fillWidth: true
                        placeholderText: "如 SW-2026-008"
                        onTextChanged: root.impactProject = text
                    }
                }

                RowLayout {
                    Layout.fillWidth: true
                    Text { text: "紧急程度"; width: 80; color: Theme.textSecondary }
                    ComboBox {
                        model: ["normal", "urgent", "critical"]
                        onActivated: root.urgency = currentText
                    }
                }

                RowLayout {
                    Layout.fillWidth: true
                    Text { text: "描述"; width: 80; color: Theme.textSecondary }
                    ScrollView {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 120
                        TextArea {
                            placeholderText: "详细描述变更原因、范围、影响"
                            wrapMode: TextArea.Wrap
                            onTextChanged: root.description = text
                        }
                    }
                }
            }

            // 按钮区
            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 56
                color: Theme.surface
                Rectangle {
                    anchors.top: parent.top
                    anchors.left: parent.left
                    anchors.right: parent.right
                    height: 1
                    color: Theme.border
                }
                RowLayout {
                    anchors.fill: parent
                    anchors.margins: Theme.spacingMd
                    Item { Layout.fillWidth: true }
                    PrimaryButton {
                        text: "取消"
                        type: "ghost"
                        Layout.preferredWidth: 80
                        onClicked: { root._isOpen = false; root.cancelled() }
                    }
                    PrimaryButton {
                        text: "创建"
                        type: "primary"
                        Layout.preferredWidth: 80
                        enabled: root.changeTitle !== ""
                        onClicked: {
                            root.changeCreated(root.changeTitle, root.changeType)
                            root._isOpen = false
                        }
                    }
                }
            }
        }
    }
}
