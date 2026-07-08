// GlassPanel.qml - 毛玻璃容器组件（对齐原型 V7 .glass-panel）
//
// CHG-SCPT-2026-102 T2：深色玻璃拟物基底组件
//
// 用法：作为卡片/面板的容器，内部放内容
//   GlassPanel {
//       width: 200; height: 100
//       Text { text: "内容"; anchors.centerIn: parent; color: Theme.textPrimary }
//   }
import QtQuick
import "../theme"

Rectangle {
    id: root

    // 玻璃拟物基底（半透明 + 边框 + 圆角）
    color: Theme.glassBg
    border.color: Theme.glassBorder
    border.width: 1
    radius: Theme.radiusLg

    // 顶部高光渐变（模拟玻璃质感，限顶部 50% 区域不干扰下半内容）
    Rectangle {
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        height: parent.height * 0.5
        radius: parent.radius
        clip: true
        gradient: Gradient {
            GradientStop { position: 0.0; color: Qt.rgba(1, 1, 1, 0.04) }
            GradientStop { position: 1.0; color: "transparent" }
        }
    }
}
