// PrimaryButton.qml - 可复用按钮组件（V0.6.0 W2-S4）
//
// 主题化按钮，支持 primary/secondary/danger/ghost 4 种样式。
// 含 hover/pressed 状态动画。
//
// 用法：
//   PrimaryButton { text: "新建项目"; onClicked: openDialog() }
//   PrimaryButton { text: "删除"; type: "danger" }

import QtQuick
import "../theme"

Rectangle {
    id: root

    // ── 公开属性 ────────────────────────────────────────
    property string text: ""
    property string type: "primary"  // primary/secondary/danger/ghost
    // enabled 继承自 Rectangle（Item），无需重定义

    // ── 信号 ────────────────────────────────────────────
    signal clicked()

    // ── 颜色映射 ────────────────────────────────────────
    readonly property var _typeColorMap: ({
        "primary": Theme.primary,
        "secondary": Theme.textSecondary,
        "danger": Theme.error,
        "ghost": "transparent"
    })
    readonly property color _baseColor: _typeColorMap[type] || Theme.primary
    readonly property bool _isGhost: type === "ghost"

    // ── 视觉样式 ────────────────────────────────────────
    implicitWidth: buttonText.implicitWidth + 24
    implicitHeight: 32
    color: _isGhost ? "transparent" : (_baseColor)
    radius: Theme.radiusSm
    border.color: _isGhost ? Theme.border : _baseColor
    border.width: _isGhost ? 1 : 0
    opacity: enabled ? 1.0 : 0.5

    // hover/pressed 状态
    states: [
        State { name: "hover"; when: mouseArea.containsMouse && enabled && !mouseArea.pressed },
        State { name: "pressed"; when: mouseArea.pressed && enabled }
    ]

    transitions: [
        Transition { to: "hover"; ColorAnimation { duration: 100 } },
        Transition { to: "pressed"; ColorAnimation { duration: 50 } }
    ]

    Text {
        id: buttonText
        anchors.centerIn: parent
        text: root.text
        color: _isGhost ? Theme.textPrimary : "white"
        font.pixelSize: Theme.fontSizeSm
        font.bold: true
    }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        cursorShape: enabled ? Qt.PointingHandCursor : Qt.ArrowCursor
        hoverEnabled: true
        enabled: root.enabled
        onClicked: {
            if (root.enabled) root.clicked()
        }
    }
}
