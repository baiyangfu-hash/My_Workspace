// KpiCard.qml - KPI 卡片组件（CHG-106 T3）
//
// 单个 KPI 卡片：标题行（标题+图标）+ 主数值 + 副文本
// 对齐 V7 原型 .kpi-card（02_设计/Html原型预览/012_UI架构原型_V7.html L1001-1026）
//
// 用法：
//   KpiCard {
//       title: "遗留技术债"
//       value: "0"
//       valueSuffix: "项"
//       subtitle: "V0.9.2 已偿还全部 34 项"
//       iconText: "⚠"
//       iconColor: Theme.warning
//   }

import QtQuick
import QtQuick.Layouts
import "../theme"

GlassPanel {
    id: root

    // ── 公开属性 ────────────────────────────────────────
    property string title: ""        // 卡片标题
    property string value: "0"       // 主数值
    property string valueSuffix: ""  // 数值后缀（如"项"，小号灰色）
    property string subtitle: ""     // 副文本
    property color valueColor: Theme.textPrimary  // 数值颜色
    property color iconColor: Theme.primary       // 图标颜色
    property string iconText: ""     // 图标字符（Unicode/emoji）

    implicitHeight: 120

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Theme.spacingMd
        spacing: Theme.spacingXs

        // 标题行：标题（左）+ 图标（右）
        RowLayout {
            Layout.fillWidth: true
            spacing: Theme.spacingSm

            Text {
                text: root.title
                color: Theme.textMuted
                font.pixelSize: Theme.fontSizeMd
                Layout.fillWidth: true
            }

            Text {
                text: root.iconText
                color: root.iconColor
                font.pixelSize: 20
                visible: root.iconText !== ""
            }
        }

        // 主数值 + 后缀
        RowLayout {
            Layout.fillWidth: true
            spacing: Theme.spacingXs

            Text {
                text: root.value
                color: root.valueColor
                font.pixelSize: Theme.fontSizeXxl
                font.bold: true
            }

            Text {
                text: root.valueSuffix
                color: Theme.textMuted
                font.pixelSize: Theme.fontSizeMd
                font.weight: Font.Normal
                visible: root.valueSuffix !== ""
                Layout.alignment: Qt.AlignBottom
                bottomPadding: 2
            }
        }

        // 副文本
        Text {
            text: root.subtitle
            color: Theme.textMuted
            font.pixelSize: Theme.fontSizeSm
            Layout.fillWidth: true
            wrapMode: Text.WordWrap
            visible: root.subtitle !== ""
        }

        // 弹性占位，让内容顶部对齐
        Item {
            Layout.fillHeight: true
            Layout.fillWidth: true
        }
    }
}
