// WordBankBuilder.qml - 多邻国/博树风格“连词成句”互动组件
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../theme"

ColumnLayout {
    id: root
    spacing: Theme.spacingMd
    width: parent ? parent.width : 540

    property string targetSentence: "Excuse me, where is the subway station?"
    property var selectedWords: []

    signal answerSubmitted(string userSentence, bool isCorrect)

    function initWordBank(sentence) {
        root.targetSentence = sentence || "Excuse me, where is the subway station?";
        root.selectedWords = [];
        targetModel.clear();
        poolModel.clear();

        // 拆分关键词并加入干扰词
        var clean = root.targetSentence.replace(/[.,!?]/g, "");
        var words = clean.split(/\s+/);
        var pool = words.slice();

        // 干扰词
        var distractors = ["airport", "coffee", "ticket", "hotel", "please"];
        for (var d = 0; d < 2; d++) {
            var randD = distractors[Math.floor(Math.random() * distractors.length)];
            if (pool.indexOf(randD) === -1) {
                pool.push(randD);
            }
        }

        // 打乱顺序
        for (var i = pool.length - 1; i > 0; i--) {
            var j = Math.floor(Math.random() * (i + 1));
            var temp = pool[i];
            pool[i] = pool[j];
            pool[j] = temp;
        }

        for (var k = 0; k < pool.length; k++) {
            poolModel.append({ "word": pool[k], "used": false });
        }
    }

    Component.onCompleted: initWordBank(root.targetSentence)

    onTargetSentenceChanged: initWordBank(root.targetSentence)

    // 目标组装框 (Target Sentence Box)
    Rectangle {
        Layout.fillWidth: true
        Layout.preferredHeight: 70
        color: Qt.rgba(15/255, 23/255, 42/255, 0.8)
        border.color: Theme.primary
        border.width: 2
        radius: Theme.radiusMd

        Flow {
            anchors.fill: parent
            anchors.margins: 10
            spacing: 8

            Repeater {
                model: ListModel { id: targetModel }

                delegate: Rectangle {
                    implicitWidth: targetText.implicitWidth + 24
                    implicitHeight: 36
                    color: Qt.rgba(56/255, 189/255, 248/255, 0.2)
                    border.color: Theme.secondary
                    radius: 10

                    MouseArea {
                        anchors.fill: parent
                        cursorShape: Qt.PointingHandCursor
                        onClicked: {
                            // 点击从目标框退回词库
                            var word = model.word;
                            var poolIdx = model.poolIndex;
                            if (poolIdx >= 0 && poolIdx < poolModel.count) {
                                poolModel.setProperty(poolIdx, "used", false);
                            }
                            targetModel.remove(index);
                        }
                    }

                    Text {
                        id: targetText
                        anchors.centerIn: parent
                        text: model.word
                        color: Theme.textPrimary
                        font.pixelSize: Theme.fontSizeMd
                        font.bold: true
                    }
                }
            }
        }
    }

    Text {
        text: "💡 点击下方单词气泡拼出正确英文句子："
        color: Theme.textMuted
        font.pixelSize: Theme.fontSizeSm
    }

    // 词块候选池 (Word Bank Pool)
    Flow {
        Layout.fillWidth: true
        spacing: 10

        Repeater {
            model: ListModel { id: poolModel }

            delegate: Rectangle {
                implicitWidth: poolText.implicitWidth + 24
                implicitHeight: 40
                color: model.used ? Qt.rgba(255/255, 255/255, 255/255, 0.05) : Theme.backgroundTertiary
                border.color: model.used ? "transparent" : Theme.border
                radius: Theme.radiusMd
                opacity: model.used ? 0.3 : 1.0

                MouseArea {
                    anchors.fill: parent
                    cursorShape: model.used ? Qt.ArrowCursor : Qt.PointingHandCursor
                    onClicked: {
                        if (model.used) return;
                        poolModel.setProperty(index, "used", true);
                        targetModel.append({ "word": model.word, "poolIndex": index });
                    }
                }

                Text {
                    id: poolText
                    anchors.centerIn: parent
                    text: model.word
                    color: model.used ? Theme.textMuted : Theme.textPrimary
                    font.pixelSize: Theme.fontSizeMd
                    font.bold: true
                }
            }
        }
    }

    // 检查答案按钮
    Button {
        text: "✅ 检查组合 (Check Sentence)"
        Layout.alignment: Qt.AlignHCenter
        onClicked: {
            var assembled = "";
            for (var i = 0; i < targetModel.count; i++) {
                assembled += targetModel.get(i).word + " ";
            }
            assembled = assembled.trim().toLowerCase();
            var targetClean = root.targetSentence.replace(/[.,!?]/g, "").trim().toLowerCase();

            var isCorrect = (assembled === targetClean);
            root.answerSubmitted(assembled, isCorrect);
        }
    }
}
