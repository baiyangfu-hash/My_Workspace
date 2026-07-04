// NewProjectWizard.qml - 新建项目向导（V0.6.0 W3-S10）
//
// 3 步分步向导：
// 1. 基本信息（项目 ID + 名称 + 技术栈 + 业务线）
// 2. 模式选择（标准单机/多项目共用 + PLC/Python 选项）
// 3. 确认创建（预览配置 + 调用 bridge.createProject）
//
// 通过 context property 访问：bridge（QmlBridge）

import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../theme"
import "../components"

Item {
    id: root

    // ── 公开属性 ────────────────────────────────────────
    property bool _isOpen: false
    property int currentStep: 0
    property int totalSteps: 3

    // 步骤 1 数据
    property string projectId: ""
    property string projectName: ""
    property string stack: "python"
    property string businessLine: "SW"

    // 步骤 2 数据
    property string mode: "standard"
    property bool createPlcStructure: true

    // ── 信号 ────────────────────────────────────────────
    signal projectCreated(string projectId, string projectName)
    signal cancelled()

    visible: _isOpen
    anchors.fill: parent

    // ── 遮罩层 ──────────────────────────────────────────
    Rectangle {
        anchors.fill: parent
        color: "#000000"
        opacity: 0.4
        visible: root._isOpen
        MouseArea {
            anchors.fill: parent
            onClicked: {}  // 阻止穿透
        }
    }

    // ── 向导主体 ────────────────────────────────────────
    Rectangle {
        id: wizardContent
        anchors.centerIn: parent
        width: 640
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
                Layout.preferredHeight: 56
                color: Theme.primary

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: Theme.spacingLg
                    anchors.rightMargin: Theme.spacingLg

                    Text {
                        text: "新建项目向导（步骤 " + (root.currentStep + 1) + "/" + root.totalSteps + "）"
                        color: "white"
                        font.pixelSize: Theme.fontSizeLg
                        font.bold: true
                    }

                    Item { Layout.fillWidth: true }

                    // 步骤指示器
                    Repeater {
                        model: root.totalSteps
                        Rectangle {
                            width: 24
                            height: 24
                            radius: 12
                            color: index <= root.currentStep ? "white" : "transparent"
                            border.color: "white"
                            border.width: 1

                            Text {
                                anchors.centerIn: parent
                                text: index + 1
                                color: index <= root.currentStep ? Theme.primary : "white"
                                font.pixelSize: Theme.fontSizeSm
                                font.bold: true
                            }
                        }
                    }
                }
            }

            // 内容区
            StackLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                currentIndex: root.currentStep

                // 步骤 1：基本信息
                ColumnLayout {
                    Layout.margins: Theme.spacingLg
                    spacing: Theme.spacingMd

                    Text {
                        text: "基本信息"
                        font.pixelSize: Theme.fontSizeXl
                        font.bold: true
                        color: Theme.textPrimary
                    }

                    // 项目 ID
                    RowLayout {
                        Layout.fillWidth: true
                        Text { text: "项目 ID"; width: 100; color: Theme.textSecondary }
                        TextField {
                            id: idInput
                            Layout.fillWidth: true
                            placeholderText: "如 SW-2026-008 / DJ-2026-005"
                            text: root.projectId
                            onTextChanged: root.projectId = text
                        }
                    }

                    // 项目名称
                    RowLayout {
                        Layout.fillWidth: true
                        Text { text: "项目名称"; width: 100; color: Theme.textSecondary }
                        TextField {
                            id: nameInput
                            Layout.fillWidth: true
                            placeholderText: "如 auto-pm 自动化项目管理工具"
                            text: root.projectName
                            onTextChanged: root.projectName = text
                        }
                    }

                    // 技术栈
                    RowLayout {
                        Layout.fillWidth: true
                        Text { text: "技术栈"; width: 100; color: Theme.textSecondary }
                        ComboBox {
                            model: ["python", "plc", "unknown"]
                            currentIndex: 0
                            onActivated: root.stack = currentText
                        }
                    }

                    // 业务线
                    RowLayout {
                        Layout.fillWidth: true
                        Text { text: "业务线"; width: 100; color: Theme.textSecondary }
                        ComboBox {
                            model: ["SW", "DJ", "ZD", "XT", "WX"]
                            currentIndex: 0
                            onActivated: root.businessLine = currentText
                        }
                    }
                }

                // 步骤 2：模式选择
                ColumnLayout {
                    Layout.margins: Theme.spacingLg
                    spacing: Theme.spacingMd

                    Text {
                        text: "模式选择"
                        font.pixelSize: Theme.fontSizeXl
                        font.bold: true
                        color: Theme.textPrimary
                    }

                    // 标准单机模式
                    RadioButton {
                        text: "标准单机模式（生成 02_PLC程序/PLC_ST/ 或 Python 项目骨架）"
                        checked: root.mode === "standard"
                        onClicked: root.mode = "standard"
                    }

                    // 多项目共用模式
                    RadioButton {
                        text: "多项目共用模式（仅创建基础目录）"
                        checked: root.mode === "shared"
                        onClicked: root.mode = "shared"
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 1
                        color: Theme.border
                    }

                    CheckBox {
                        text: "创建 PLC 标准目录结构（02_PLC程序/PLC_ST/）"
                        checked: root.createPlcStructure
                        onToggled: root.createPlcStructure = checked
                    }
                }

                // 步骤 3：确认创建
                ColumnLayout {
                    Layout.margins: Theme.spacingLg
                    spacing: Theme.spacingMd

                    Text {
                        text: "确认创建"
                        font.pixelSize: Theme.fontSizeXl
                        font.bold: true
                        color: Theme.textPrimary
                    }

                    Text {
                        text: "请确认以下配置："
                        font.pixelSize: Theme.fontSizeSm
                        color: Theme.textSecondary
                    }

                    // 配置预览
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 200
                        color: Theme.surface
                        radius: Theme.radiusMd
                        border.color: Theme.border

                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: Theme.spacingMd
                            spacing: Theme.spacingSm

                            Text { text: "项目 ID: " + root.projectId; color: Theme.textPrimary }
                            Text { text: "项目名称: " + root.projectName; color: Theme.textPrimary }
                            Text { text: "技术栈: " + root.stack; color: Theme.textPrimary }
                            Text { text: "业务线: " + root.businessLine; color: Theme.textPrimary }
                            Text { text: "模式: " + root.mode; color: Theme.textPrimary }
                            Text {
                                text: "PLC 结构: " + (root.createPlcStructure ? "创建" : "不创建")
                                color: Theme.textPrimary
                            }
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
                    spacing: Theme.spacingSm

                    Item { Layout.fillWidth: true }

                    PrimaryButton {
                        text: "取消"
                        type: "ghost"
                        Layout.preferredWidth: 80
                        onClicked: {
                            root._isOpen = false
                            root.cancelled()
                        }
                    }

                    PrimaryButton {
                        text: root.currentStep === 0 ? "下一步 →" : (root.currentStep === 1 ? "下一步 →" : "完成")
                        type: "primary"
                        Layout.preferredWidth: 100
                        enabled: root.currentStep !== 0 || (root.projectId !== "" && root.projectName !== "")
                        onClicked: {
                            if (root.currentStep < root.totalSteps - 1) {
                                root.currentStep += 1
                            } else {
                                // 调用 bridge 创建项目
                                if (typeof bridge !== "undefined" && bridge !== null) {
                                    bridge.createProject(
                                        root.projectId, root.projectName,
                                        root.stack, root.mode, root.businessLine
                                    )
                                }
                                root.projectCreated(root.projectId, root.projectName)
                                root._isOpen = false
                                root.currentStep = 0
                            }
                        }
                    }

                    PrimaryButton {
                        text: "← 上一步"
                        type: "ghost"
                        Layout.preferredWidth: 80
                        visible: root.currentStep > 0
                        onClicked: root.currentStep -= 1
                    }
                }
            }
        }
    }
}
