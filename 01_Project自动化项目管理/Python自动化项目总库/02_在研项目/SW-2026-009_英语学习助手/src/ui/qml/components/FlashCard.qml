// FlashCard.qml - FSRS 翻转背词卡片组件 (支持 Windows 触屏滑动手势)
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

    signal swipedLeft()   // 左滑：标记为重背/忘记
    signal swipedRight()  // 右滑：标记为掌握/良好

    implicitWidth: 520
    implicitHeight: 300
    width: 520
    height: 300

    Rectangle {
        id: cardContainer
        anchors.fill: parent
        radius: Theme.radiusLg
        color: root.isFlipped ? Qt.rgba(30/255, 41/255, 59/255, 0.95) : Qt.rgba(15/255, 23/255, 42/255, 0.90)
        border.color: dragHintText.text !== "" ? (dragHintText.color) : (root.isFlipped ? Theme.secondary : Theme.primary)
        border.width: 3

        property real startX: 0
        property real startY: 0
        property bool isDragging: false

        MouseArea {
            id: touchArea
            anchors.fill: parent
            cursorShape: Qt.PointingHandCursor
            hoverEnabled: true

            onPressed: function(mouse) {
                cardContainer.startX = mouse.x;
                cardContainer.startY = mouse.y;
                cardContainer.isDragging = false;
            }

            onPositionChanged: function(mouse) {
                var dx = mouse.x - cardContainer.startX;
                if (Math.abs(dx) > 30) {
                    cardContainer.isDragging = true;
                    if (dx > 60) {
                        dragHintText.text = "👉 右滑: 记得 (Good)";
                        dragHintText.color = Theme.success;
                    } else if (dx < -60) {
                        dragHintText.text = "👈 左滑: 忘记 (Again)";
                        dragHintText.color = Theme.danger;
                    }
                }
            }

            onReleased: function(mouse) {
                var dx = mouse.x - cardContainer.startX;
                dragHintText.text = "";
                if (cardContainer.isDragging && Math.abs(dx) > 70) {
                    if (dx > 70) {
                        root.swipedRight();
                    } else {
                        root.swipedLeft();
                    }
                } else {
                    root.isFlipped = !root.isFlipped;
                }
                cardContainer.isDragging = false;
            }
        }

        // 触屏滑动实时提示
        Text {
            id: dragHintText
            anchors.top: parent.top
            anchors.topMargin: 16
            anchors.horizontalCenter: parent.horizontalCenter
            text: ""
            font.pixelSize: Theme.fontSizeLg
            font.bold: true
            z: 10
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
                implicitWidth: 260
                implicitHeight: 36
                anchors.horizontalCenter: parent.horizontalCenter

                Text {
                    anchors.centerIn: parent
                    text: "👈左滑忘记 | 点击翻牌 | 右滑记得👉"
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
