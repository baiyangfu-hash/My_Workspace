// TemplateApplyDialog.qml - 模板应用对话框（M4 CHG-115）
//
// 列出可用模板，选择后应用到指定项目
// 调用 systemBridge.applyTemplate() 执行

import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../theme"
import "../components"

Item {
    id: root

    property bool _isOpen: false
    property string projectId: ""
    property string projectName: ""
    property var templates: []
    property string selectedTemplate: ""

    // 信号
    signal templateApplied(string projectId, string templateName)
    signal cancelled()

    visible: _isOpen
    anchors.fill: parent
    z: 998

    function open(pid, pname) {
        root.projectId = pid
        root.projectName = pname
        root.selectedTemplate = ""
        // 加载模板列表
        if (typeof systemBridge !== "undefined" && systemBridge !== null) {
            if (typeof systemBridge.listTemplates === "function") {
                root.templates = systemBridge.listTemplates()
            } else {
                root.templates = []
            }
        }
        root._isOpen = true
    }

    function close() {
        root._isOpen = false
    }

    // 遮罩层
    Rectangle {
        anchors.fill: parent
        color: "#80000000"
        MouseArea {
            anchors.fill: parent
            onClicked: root.cancelled()
        }
    }

    // 对话框主体
    GlassPanel {
        width: 480
        height: Math.min(500, columnLayout.implicitHeight + Theme.spacingXl * 2)
        anchors.centerIn: parent
        radius: Theme.radiusLg

        ColumnLayout {
            id: columnLayout
            anchors.fill: parent
            anchors.margins: Theme.spacingLg
            spacing: Theme.spacingMd

            // 标题
            Text {
                text: "应用模板到: " + root.projectName
                color: Theme.textPrimary
                font.pixelSize: Theme.fontSizeXl
                font.bold: true
            }

            Text {
                text: "选择模板后将覆盖项目中的自动区文档内容"
                color: Theme.textMuted
                font.pixelSize: Theme.fontSizeSm
                wrapMode: Text.WordWrap
                Layout.fillWidth: true
            }

            // 模板列表
            ListView {
                id: templateList
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.preferredHeight: 200
                model: root.templates
                clip: true

                delegate: Rectangle {
                    width: templateList.width
                    height: 40
                    color: root.selectedTemplate === modelData ? Theme.glassHighlight : "transparent"
                    radius: Theme.radiusSm

                    Text {
                        anchors.verticalCenter: parent.verticalCenter
                        anchors.left: parent.left
                        anchors.leftMargin: Theme.spacingMd
                        text: modelData
                        color: Theme.textPrimary
                        font.pixelSize: Theme.fontSizeMd
                    }

                    MouseArea {
                        anchors.fill: parent
                        onClicked: root.selectedTemplate = modelData
                    }
                }
            }

            // 空状态
            Text {
                visible: root.templates.length === 0
                text: "没有可用的模板"
                color: Theme.textMuted
                font.pixelSize: Theme.fontSizeMd
                anchors.horizontalCenter: parent.horizontalCenter
            }

            // 按钮栏
            RowLayout {
                Layout.fillWidth: true
                Layout.topMargin: Theme.spacingMd

                Item { Layout.fillWidth: true }

                Button {
                    text: "取消"
                    onClicked: root.cancelled()
                }

                Button {
                    text: "应用模板"
                    enabled: root.selectedTemplate !== ""
                    onClicked: {
                        if (typeof systemBridge === "undefined" || systemBridge === null) return
                        var result = systemBridge.applyTemplate(root.projectId, root.selectedTemplate)
                        if (result && result.success) {
                            console.log("[QML] TemplateApplyDialog: 模板应用成功")
                            root.templateApplied(root.projectId, root.selectedTemplate)
                        } else {
                            console.warn("[QML] TemplateApplyDialog: 模板应用失败 -", result ? result.message : "")
                        }
                    }
                }
            }
        }
    }
}