// DocBrowserView.qml - 文档浏览器及 Markdown 渲染视图
//
// 提供项目内部文档目录树浏览、Markdown 实时渲染展示、自动区刷新操作。

import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../theme"
import "../components"

Rectangle {
    id: root
    color: "transparent"

    property string projectId: ""
    property var docList: []
    property int selectedIndex: -1
    property string htmlContent: ""
    property string statusMessage: ""

    onProjectIdChanged: {
        loadDocs()
    }

    function loadDocs() {
        if (!projectId) return
        selectedIndex = -1
        htmlContent = ""
        statusMessage = ""
        if (typeof deliveryBridge !== "undefined" && deliveryBridge !== null) {
            root.docList = deliveryBridge.listProjectDocs(root.projectId)
            if (root.docList.length > 0) {
                selectDoc(0)
            } else {
                statusMessage = "未在此项目中找到 Markdown 文档 (.md)"
            }
        }
    }

    function selectDoc(index) {
        if (index < 0 || index >= docList.length) return
        selectedIndex = index
        statusMessage = ""
        var doc = docList[index]
        if (typeof deliveryBridge !== "undefined" && deliveryBridge !== null) {
            htmlContent = deliveryBridge.renderMarkdown(doc.path)
        }
    }

    RowLayout {
        anchors.fill: parent
        spacing: Theme.spacingMd

        // ── 左侧文档列表 ──────────────────────────────────
        Rectangle {
            Layout.preferredWidth: 280
            Layout.fillHeight: true
            color: Theme.surface
            radius: Theme.radiusMd
            border.color: Theme.border
            border.width: 1

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: Theme.spacingMd
                spacing: Theme.spacingSm

                Text {
                    text: "📄 项目文档目录"
                    font.pixelSize: Theme.fontSizeMd
                    font.bold: true
                    color: Theme.textPrimary
                    Layout.fillWidth: true
                }

                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 1
                    color: Theme.border
                }

                ScrollView {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    clip: true

                    ListView {
                        id: docListView
                        model: root.docList
                        delegate: Item {
                            width: docListView.width
                            height: 48

                            Rectangle {
                                anchors.fill: parent
                                anchors.margins: 2
                                color: root.selectedIndex === index ? Theme.glassBg : "transparent"
                                border.color: root.selectedIndex === index ? Theme.primary : "transparent"
                                border.width: 1
                                radius: Theme.radiusSm

                                RowLayout {
                                    anchors.fill: parent
                                    anchors.leftMargin: Theme.spacingSm
                                    anchors.rightMargin: Theme.spacingSm
                                    spacing: Theme.spacingSm

                                    Text {
                                        text: "📝"
                                        font.pixelSize: 16
                                    }

                                    ColumnLayout {
                                        Layout.fillWidth: true
                                        spacing: 2
                                        Text {
                                            text: modelData.name.split("/").pop() // filename
                                            font.pixelSize: Theme.fontSizeSm
                                            font.bold: root.selectedIndex === index
                                            color: root.selectedIndex === index ? Theme.primary : Theme.textPrimary
                                            elide: Text.ElideRight
                                            Layout.fillWidth: true
                                        }
                                        Text {
                                            text: modelData.name.substring(0, modelData.name.lastIndexOf("/")) || "/"
                                            font.pixelSize: Theme.fontSizeXs
                                            color: Theme.textMuted
                                            elide: Text.ElideRight
                                            Layout.fillWidth: true
                                        }
                                    }
                                }

                                MouseArea {
                                    anchors.fill: parent
                                    cursorShape: Qt.PointingHandCursor
                                    onClicked: root.selectDoc(index)
                                }
                            }
                        }
                    }
                }
            }
        }

        // ── 右侧渲染预览区 ─────────────────────────────────
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: Theme.surface
            radius: Theme.radiusMd
            border.color: Theme.border
            border.width: 1

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 0
                spacing: 0

                // 渲染区工具栏
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 56
                    color: "transparent"

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
                        spacing: Theme.spacingMd

                        Text {
                            text: root.selectedIndex >= 0 ? "📖 " + root.docList[root.selectedIndex].name : "未选择文档"
                            font.pixelSize: Theme.fontSizeMd
                            font.bold: true
                            color: Theme.textPrimary
                            elide: Text.ElideMiddle
                            Layout.fillWidth: true
                        }

                        PrimaryButton {
                            text: "🔄 刷新自动区"
                            type: "accent"
                            Layout.preferredWidth: 120
                            enabled: root.selectedIndex >= 0
                            onClicked: {
                                refreshOverlay.visible = true
                                var result = deliveryBridge.refreshProjectDocs(root.projectId, false)
                                if (result && result.success) {
                                    root.statusMessage = "文档自动区刷新完成：" + (result.message || "")
                                    root.selectDoc(root.selectedIndex) // reload content
                                } else {
                                    root.statusMessage = "刷新失败：" + (result ? result.message : "")
                                }
                                refreshOverlay.visible = false
                            }
                        }
                    }
                }

                // 核心渲染区
                Item {
                    Layout.fillWidth: true
                    Layout.fillHeight: true

                    ScrollView {
                        anchors.fill: parent
                        anchors.margins: Theme.spacingLg
                        clip: true
                        visible: root.statusMessage === "" && root.selectedIndex >= 0

                        Text {
                            width: parent.width - Theme.spacingLg * 2
                            text: root.htmlContent
                            textFormat: Text.RichText
                            wrapMode: Text.WordWrap
                            color: Theme.textPrimary
                            font.pixelSize: Theme.fontSizeMd
                        }
                    }

                    // 状态/空信息提示
                    ColumnLayout {
                        anchors.centerIn: parent
                        spacing: Theme.spacingSm
                        visible: root.statusMessage !== "" || root.selectedIndex < 0

                        Text {
                            text: root.statusMessage || "请从左侧选择一个文档进行实时渲染浏览"
                            font.pixelSize: Theme.fontSizeMd
                            color: Theme.textSecondary
                            horizontalAlignment: Text.AlignHCenter
                            Layout.fillWidth: true
                        }
                    }

                    // 刷新中遮罩
                    Rectangle {
                        id: refreshOverlay
                        anchors.fill: parent
                        color: "#80000000"
                        visible: false

                        ColumnLayout {
                            anchors.centerIn: parent
                            spacing: Theme.spacingSm
                            Text {
                                text: "🔄 正在自动刷新文档数据区..."
                                font.pixelSize: Theme.fontSizeMd
                                color: "white"
                                font.bold: true
                            }
                        }
                    }
                }
            }
        }
    }

    Component.onCompleted: loadDocs()
}
