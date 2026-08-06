// FlashCard.qml - FSRS 翻转背词卡片组件
import QtQuick
import QtQuick.Controls
import "../theme"

Item {
    id: root

    property string wordText: "itinerary"
    property string phoneticText: "/aɪˈtɪnəreri/"
    property string definitionText: "n. 旅行日程；行程单"
    property string exampleText: "Here is your business trip itinerary."
    property bool isFlipped: false

    implicitWidth: 520
    implicitHeight: 300
    width: 520
    height: 300

    Rectangle {
        id: cardContainer
        anchors.fill: parent
        radius: Theme.radiusLg
        color: root.isFlipped ? Qt.rgba(30/255, 41/255, 59/255, 0.95) : Qt.rgba(15/255, 23/255, 42/255, 0.90)
        border.color: root.isFlipped ? Theme.secondary : Theme.primary
        border.width: 2

        MouseArea {
            id: mouseArea
            anchors.fill: parent
            cursorShape: Qt.PointingHandCursor
            hoverEnabled: true
            onClicked: {
                root.isFlipped = !root.isFlipped;
            }
        }

        // 正面内容 (Front)
        Column {
            anchors.centerIn: parent
            spacing: Theme.spacingMd
            visible: !root.isFlipped

            Text {
                text: root.wordText
                color: Theme.textPrimary
                font.pixelSize: 38
                font.bold: true
                anchors.horizontalCenter: parent.horizontalCenter
            }

            Text {
                text: root.phoneticText ? "/" + root.phoneticText.replace(/^\/+|\/+$/g, '') + "/" : ""
                color: Theme.secondary
                font.pixelSize: Theme.fontSizeXl
                anchors.horizontalCenter: parent.horizontalCenter
            }

            Rectangle {
                color: Qt.rgba(99/255, 102/255, 241/255, 0.2)
                border.color: Theme.primary
                radius: 20
                implicitWidth: 220
                implicitHeight: 36
                anchors.horizontalCenter: parent.horizontalCenter

                Text {
                    anchors.centerIn: parent
                    text: "💡 点击卡片或下方按钮翻转"
                    color: Theme.textPrimary
                    font.pixelSize: Theme.fontSizeSm
                    font.bold: true
                }
            }
        }

        // 背面内容 (Back)
        Column {
            anchors.centerIn: parent
            spacing: Theme.spacingMd
            width: parent.width - 60
            visible: root.isFlipped

            Text {
                text: root.definitionText
                color: Theme.secondary
                font.pixelSize: 22
                font.bold: true
                anchors.horizontalCenter: parent.horizontalCenter
                horizontalAlignment: Text.AlignHCenter
                wrapMode: Text.Wrap
                width: parent.width
            }

            Rectangle {
                width: parent.width
                height: 1
                color: Theme.border
            }

            Text {
                text: root.exampleText
                color: Theme.textSecondary
                font.pixelSize: Theme.fontSizeMd
                anchors.horizontalCenter: parent.horizontalCenter
                horizontalAlignment: Text.AlignHCenter
                wrapMode: Text.Wrap
                width: parent.width
            }

            Text {
                text: "↺ 再按一次翻回正面"
                color: Theme.textMuted
                font.pixelSize: Theme.fontSizeXs
                anchors.horizontalCenter: parent.horizontalCenter
            }
        }
    }
}
