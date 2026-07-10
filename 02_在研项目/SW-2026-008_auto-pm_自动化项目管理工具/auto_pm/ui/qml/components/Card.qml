// Card.qml - 可复用卡片组件（V0.6.0 W2-S4）
//
// 通用卡片容器：圆角 + 边框 + 阴影 + 标题/副标题/内容区。
// 用于项目卡片、变更卡片、信息卡片等场景。
//
// 用法：
//   Card {
//       title: "项目名称"
//       subtitle: "SW-2026-008"
//       bodyText: "项目描述..."
//   }
//
// 也可通过默认插槽嵌入自定义内容：
//   Card { title: "标题"; ColumnLayout { Text { text: "自定义" } } }

import QtQuick
import QtQuick.Layouts
import "../theme"

Rectangle {
    id: root

    // ── 公开属性 ────────────────────────────────────────
    property string title: ""
    property string subtitle: ""
    property string bodyText: ""
    property color cardColor: Theme.surface
    property color borderColor: Theme.border
    property int elevation: 1

    // ── 私有属性 ────────────────────────────────────────
    implicitHeight: contentLayout.implicitHeight + 2 * Theme.spacingMd
    implicitWidth: 320
    color: cardColor
    radius: Theme.radiusMd
    border.color: borderColor
    border.width: 1

    // ── 内容布局 ────────────────────────────────────────
    ColumnLayout {
        id: contentLayout
        anchors.fill: parent
        anchors.margins: Theme.spacingMd
        spacing: Theme.spacingXs

        // 标题
        Text {
            visible: root.title !== ""
            text: root.title
            font.pixelSize: Theme.fontSizeLg
            font.bold: true
            color: Theme.textPrimary
            elide: Text.ElideRight
            Layout.fillWidth: true
        }

        // 副标题
        Text {
            visible: root.subtitle !== ""
            text: root.subtitle
            font.pixelSize: Theme.fontSizeSm
            color: Theme.textSecondary
            elide: Text.ElideRight
            Layout.fillWidth: true
        }

        // 正文
        Text {
            visible: root.bodyText !== ""
            text: root.bodyText
            font.pixelSize: Theme.fontSizeSm
            color: Theme.textPrimary
            wrapMode: Text.WordWrap
            Layout.fillWidth: true
        }

        // 默认插槽：嵌入自定义内容
        default property alias children: slot.children
        Item {
            id: slot
            Layout.fillWidth: true
            implicitHeight: childrenRect.height
        }
    }
}
