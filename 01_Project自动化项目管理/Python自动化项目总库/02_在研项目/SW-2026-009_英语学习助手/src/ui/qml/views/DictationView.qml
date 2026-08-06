// DictationView.qml - 动态听写与多邻国连词成句练习视图
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../theme"
import "../components"

ColumnLayout {
    id: root
    spacing: Theme.spacingLg
    anchors.horizontalCenter: parent.horizontalCenter

    property string targetSentence: "Where is the nearest subway station?"
    property bool isWordBankMode: true

    GlassCard {
        Layout.preferredWidth: 620
        Layout.alignment: Qt.AlignHCenter

        RowLayout {
            width: parent.width

            Text {
                text: "🎧 听写研习 & 多邻国连词成句"
                color: Theme.textPrimary
                font.pixelSize: Theme.fontSizeXl
                font.bold: true
            }

            Item { Layout.fillWidth: true }

            // 模式切换按钮
            Button {
                text: root.isWordBankMode ? "⌨️ 切换键盘拼写" : "🧩 切换多邻国连词成句"
                onClicked: root.isWordBankMode = !root.isWordBankMode
            }
        }

        Text {
            text: "点击下方按钮听语音发音，支持连词成句与键盘打字双模式练习："
            color: Theme.textMuted
            font.pixelSize: Theme.fontSizeSm
        }

        Button {
            text: "🔊 播放完整发音 (Play Audio)"
            onClicked: {
                if (qmlBridge) {
                    qmlBridge.speakText(root.targetSentence);
                }
            }
        }

        // 模式 1: 多邻国连词成句互动组件
        WordBankBuilder {
            id: wordBank
            visible: root.isWordBankMode
            targetSentence: root.targetSentence
            onAnswerSubmitted: function(assembled, isCorrect) {
                if (isCorrect) {
                    feedbackBar.color = Qt.rgba(16/255, 185/255, 129/255, 0.2)
                    feedbackBar.border.color = Theme.success
                    feedbackText.text = "✅ 答对了！太棒了！ (+10 XP)"
                    feedbackText.color = Theme.success
                } else {
                    feedbackBar.color = Qt.rgba(239/255, 68/255, 68/255, 0.2)
                    feedbackBar.border.color = Theme.danger
                    feedbackText.text = "💡 标准答案: " + root.targetSentence
                    feedbackText.color = Theme.warning
                }
            }
        }

        // 模式 2: 键盘打字输入
        ColumnLayout {
            visible: !root.isWordBankMode
            width: parent.width
            spacing: 12

            TextField {
                id: userInput
                Layout.fillWidth: true
                placeholderText: "在此输入听到的英文句子..."
                color: Theme.textPrimary
                background: Rectangle {
                    color: Theme.backgroundTertiary
                    border.color: Theme.border
                    radius: Theme.radiusSm
                }
            }

            Button {
                text: "✅ 提交校验 (Check Answer)"
                onClicked: {
                    var input = userInput.text.trim().toLowerCase();
                    var target = root.targetSentence.trim().toLowerCase();
                    if (input === target) {
                        feedbackBar.color = Qt.rgba(16/255, 185/255, 129/255, 0.2)
                        feedbackBar.border.color = Theme.success
                        feedbackText.text = "✅ 匹配完美！完全正确！ (+10 XP)";
                        feedbackText.color = Theme.success;
                    } else {
                        feedbackBar.color = Qt.rgba(239/255, 68/255, 68/255, 0.2)
                        feedbackBar.border.color = Theme.danger
                        feedbackText.text = "💡 标准答案: " + root.targetSentence;
                        feedbackText.color = Theme.warning;
                    }
                }
            }
        }

        // 底部即时反馈条 (Duolingo Style Instant Feedback Banner)
        Rectangle {
            id: feedbackBar
            width: parent.width
            implicitHeight: 48
            color: Qt.rgba(15/255, 23/255, 42/255, 0.5)
            border.color: Theme.border
            radius: Theme.radiusSm

            RowLayout {
                anchors.fill: parent
                anchors.margins: 10

                Text {
                    id: feedbackText
                    text: "💡 点击发音或组装单词进行答题"
                    color: Theme.textMuted
                    font.pixelSize: Theme.fontSizeMd
                    font.bold: true
                }

                Item { Layout.fillWidth: true }

                Button {
                    text: "⏭️ 下一句 (Next)"
                    onClicked: {
                        userInput.text = "";
                        feedbackText.text = "💡 点击发音或组装单词进行答题";
                        feedbackText.color = Theme.textMuted;
                        feedbackBar.color = Qt.rgba(15/255, 23/255, 42/255, 0.5);
                        feedbackBar.border.color = Theme.border;

                        var samples = [
                            "Could you please show me the menu?",
                            "I would like to check in for my flight.",
                            "Where can I get a taxi to the hotel?",
                            "Excuse me, how much is this item?",
                            "Could you tell me where the peanut butter is?"
                        ];
                        var randIdx = Math.floor(Math.random() * samples.length);
                        root.targetSentence = samples[randIdx];
                        if (qmlBridge) qmlBridge.speakText(root.targetSentence);
                    }
                }
            }
        }
    }
}
