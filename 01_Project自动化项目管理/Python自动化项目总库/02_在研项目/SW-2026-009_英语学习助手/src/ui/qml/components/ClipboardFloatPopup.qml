// ClipboardFloatPopup.qml - 剪贴板自动划词离线查询迷你弹窗
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../theme"

Rectangle {
    id: root
    width: 320
    height: 120
    radius: Theme.radiusMd
    color: Qt.rgba(15/255, 23/255, 42/255, 0.95)
    border.color: Theme.primary
    border.width: 2
    visible: false

    property string copiedWord: ""
    property string wordTranslation: ""
    property string wordPhonetic: ""

    function popup(word, detailJsonStr) {
        root.copiedWord = word;
        try {
            var detail = JSON.parse(detailJsonStr);
            root.wordTranslation = detail.translation || "本地词典已匹配词条";
            root.wordPhonetic = detail.phonetic ? "/" + detail.phonetic + "/" : "";
        } catch (e) {
            root.wordTranslation = "查无此词释义";
            root.wordPhonetic = "";
        }
        root.visible = true;
        hideTimer.restart();
    }

    Timer {
        id: hideTimer
        interval: 6000
        onTriggered: root.visible = false
    }

    Connections {
        target: qmlBridge
        function onWordCopiedFromClipboard(word, detailJsonStr) {
            root.popup(word, detailJsonStr);
        }
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 12
        spacing: 6

        RowLayout {
            width: parent.width

            Text {
                text: "📋 剪贴板自动划词: " + root.copiedWord
                color: Theme.primary
                font.bold: true
                font.pixelSize: Theme.fontSizeMd
            }

            Item { Layout.fillWidth: true }

            Text {
                text: "✕"
                color: Theme.textMuted
                font.pixelSize: 14
                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    onClicked: root.visible = false
                }
            }
        }

        Text {
            text: root.wordPhonetic
            color: Theme.secondary
            font.pixelSize: Theme.fontSizeSm
            visible: root.wordPhonetic !== ""
        }

        Text {
            text: root.wordTranslation
            color: Theme.textSecondary
            font.pixelSize: Theme.fontSizeSm
            elide: Text.ElideRight
            Layout.fillWidth: true
        }

        Button {
            text: "⭐ 一键加入生词本 (Add to FSRS)"
            Layout.alignment: Qt.AlignRight
            onClicked: {
                if (qmlBridge && root.copiedWord) {
                    qmlBridge.recordReviewJson(root.copiedWord, "again", 1);
                    root.wordTranslation = "✅ 已成功收藏至生词本！";
                }
            }
        }
    }
}
