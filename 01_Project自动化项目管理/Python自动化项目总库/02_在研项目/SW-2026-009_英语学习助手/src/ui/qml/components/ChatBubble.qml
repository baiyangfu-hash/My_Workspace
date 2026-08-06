// ChatBubble.qml - 角色扮演双语对话气泡
import QtQuick
import QtQuick.Controls
import "../theme"

Rectangle {
    id: root

    property string enText: ""
    property string cnText: ""
    property bool isSpeakerB: false

    width: Math.min(contentCol.implicitWidth + 36, 560)
    height: contentCol.implicitHeight + 24
    radius: 16

    color: isSpeakerB ? Theme.primary : Theme.backgroundTertiary
    border.color: isSpeakerB ? "transparent" : Theme.border
    border.width: 1

    Column {
        id: contentCol
        anchors.fill: parent
        anchors.margins: 14
        spacing: 6

        Text {
            width: parent.width
            text: root.enText
            color: Theme.textOnPrimary
            font.pixelSize: Theme.fontSizeMd
            font.weight: Font.Medium
            wrapMode: Text.Wrap
        }

        Rectangle {
            width: parent.width
            height: 1
            color: Qt.rgba(1, 1, 1, 0.15)
            visible: root.cnText !== ""
        }

        Text {
            width: parent.width
            text: root.cnText
            color: isSpeakerB ? Qt.rgba(1, 1, 1, 0.85) : Theme.textSecondary
            font.pixelSize: Theme.fontSizeSm
            wrapMode: Text.Wrap
            visible: root.cnText !== ""
        }
    }
}
