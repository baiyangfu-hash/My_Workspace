// StatCard.qml - 驾驶舱指标统计卡片
import QtQuick
import QtQuick.Controls
import "../theme"

Rectangle {
    id: root

    property string iconText: "📚"
    property string titleText: "指标名称"
    property string valueText: "0"
    property color iconBgColor: Qt.rgba(99/255, 102/255, 241/255, 0.2)
    property color iconTextColor: Theme.primary

    radius: Theme.radiusLg
    color: Theme.bgCard
    border.color: Theme.border
    border.width: 1

    implicitWidth: 200
    implicitHeight: 90

    Row {
        anchors.fill: parent
        anchors.margins: Theme.spacingMd
        spacing: Theme.spacingMd

        Rectangle {
            width: 48
            height: 48
            radius: Theme.radiusMd
            color: root.iconBgColor
            anchors.verticalCenter: parent.verticalCenter

            Text {
                anchors.centerIn: parent
                text: root.iconText
                font.pixelSize: 22
            }
        }

        Column {
            anchors.verticalCenter: parent.verticalCenter
            spacing: 4

            Text {
                text: root.titleText
                color: Theme.textMuted
                font.pixelSize: Theme.fontSizeSm
                font.weight: Font.Medium
            }

            Text {
                text: root.valueText
                color: Theme.textPrimary
                font.pixelSize: Theme.fontSizeXl
                font.bold: true
            }
        }
    }
}
