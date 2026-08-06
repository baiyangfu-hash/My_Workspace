// VocabView.qml - FSRS 动态记忆背词视图
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../theme"
import "../components"

ColumnLayout {
    id: root
    spacing: Theme.spacingMd
    anchors.horizontalCenter: parent.horizontalCenter

    property string currentWord: "itinerary"

    function loadNextCard() {
        if (!qmlBridge) return;
        var jsonStr = qmlBridge.getRandomVocabCardJson();
        try {
            var data = JSON.parse(jsonStr);
            root.currentWord = data.word || "itinerary";
            card.wordText = data.word || "itinerary";
            card.phoneticText = data.phonetic || "";
            card.definitionText = (data.pos ? "[" + data.pos + "] " : "") + (data.translation || "");
            card.exampleText = data.example || "";
            card.isFlipped = false;
        } catch (e) {
            console.log("加载新卡片失败: " + e);
        }
    }

    function submitRating(rating) {
        if (qmlBridge && root.currentWord) {
            qmlBridge.recordReviewJson(root.currentWord, rating, 2);
        }
        loadNextCard();
    }

    Component.onCompleted: loadNextCard()

    Text {
        text: "🎴 FSRS-v4 算法抽词卡片"
        color: Theme.textPrimary
        font.pixelSize: Theme.fontSizeXl
        font.bold: true
        Layout.alignment: Qt.AlignHCenter
    }

    Text {
        text: "点击卡片或下方‘翻转卡片’按钮查看释义，根据记忆程度选择评分"
        color: Theme.textMuted
        font.pixelSize: Theme.fontSizeSm
        Layout.alignment: Qt.AlignHCenter
    }

    FlashCard {
        id: card
        Layout.preferredWidth: 520
        Layout.preferredHeight: 300
        Layout.alignment: Qt.AlignHCenter
    }

    // 控制按钮区 (翻转 + TTS 朗读)
    RowLayout {
        Layout.alignment: Qt.AlignHCenter
        spacing: Theme.spacingMd

        Button {
            text: card.isFlipped ? "🔄 翻回正面" : "🔄 翻转卡片 (查看释义)"
            onClicked: card.isFlipped = !card.isFlipped
        }

        Button {
            text: "🔊 朗读发音 (SAPI5)"
            onClicked: {
                if (qmlBridge && root.currentWord) {
                    qmlBridge.speakText(root.currentWord);
                }
            }
        }
    }

    Rectangle {
        Layout.preferredWidth: 520
        Layout.preferredHeight: 1
        color: Theme.border
        Layout.alignment: Qt.AlignHCenter
    }

    Text {
        text: "请评定对当前单词的记忆掌握度："
        color: Theme.textSecondary
        font.pixelSize: Theme.fontSizeSm
        Layout.alignment: Qt.AlignHCenter
    }

    // 4级 FSRS 评分按钮
    RowLayout {
        Layout.alignment: Qt.AlignHCenter
        spacing: Theme.spacingMd

        Button {
            text: "1. 忘记 (Again) • 0天"
            onClicked: submitRating("again")
        }
        Button {
            text: "2. 困难 (Hard) • 1天"
            onClicked: submitRating("hard")
        }
        Button {
            text: "3. 良好 (Good) • 3天"
            onClicked: submitRating("good")
        }
        Button {
            text: "4. 简单 (Easy) • 5天"
            onClicked: submitRating("easy")
        }
    }
}
