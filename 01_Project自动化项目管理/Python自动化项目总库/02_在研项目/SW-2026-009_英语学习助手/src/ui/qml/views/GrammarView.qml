// GrammarView.qml - CEFR 语法动态讲解视图 (支持 A1~C2 全等级切换)
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../theme"
import "../components"

ColumnLayout {
    id: root
    spacing: Theme.spacingLg
    anchors.horizontalCenter: parent.horizontalCenter

    property string currentLevel: "A1"

    function loadGrammarPoints(level) {
        root.currentLevel = level;
        if (!qmlBridge) return;
        
        // 设为当前学习目标等级并同步全局
        qmlBridge.setUserLevelJson(level);

        var jsonStr = qmlBridge.getGrammarPointsJson(level);
        try {
            var list = JSON.parse(jsonStr);
            grammarModel.clear();
            for (var i = 0; i < list.length; i++) {
                grammarModel.append(list[i]);
            }
            if (list.length > 0) {
                grammarList.currentIndex = 0;
                displayPoint(list[0]);
            } else {
                pointTitle.text = "📖 " + level + " 语法知识点";
                pointMeta.text = "CEFR 等级: " + level;
                pointExplanation.text = "暂无相关语法数据，已为您切换目标等级为 " + level;
                pointExamples.text = "";
            }
        } catch (e) {
            console.log("加载语法点失败: " + e);
        }
    }

    function displayPoint(item) {
        if (!item) return;
        pointTitle.text = "📖 " + (item.title || item.name || "语法知识点");
        pointMeta.text = "CEFR 等级: " + root.currentLevel + " • 分类: " + (item.category || "常用结构");
        pointExplanation.text = "用法说明:\n" + (item.explanation || item.desc || "用于描述时态与句型范例。");
        
        var examples = item.examples || [];
        var exStr = "";
        for (var k = 0; k < examples.length; k++) {
            exStr += (k + 1) + ". " + examples[k] + "\n";
        }
        pointExamples.text = exStr || "1. I am a student.\n2. She is happy.";
    }

    Component.onCompleted: loadGrammarPoints("A1")

    // A1~C2 全等级选择器
    RowLayout {
        Layout.alignment: Qt.AlignHCenter
        spacing: Theme.spacingSm

        Button {
            text: "A1 入门"
            highlighted: root.currentLevel === "A1"
            onClicked: loadGrammarPoints("A1")
        }
        Button {
            text: "A2 基础"
            highlighted: root.currentLevel === "A2"
            onClicked: loadGrammarPoints("A2")
        }
        Button {
            text: "B1 商务/职场"
            highlighted: root.currentLevel === "B1"
            onClicked: loadGrammarPoints("B1")
        }
        Button {
            text: "B2 中级"
            highlighted: root.currentLevel === "B2"
            onClicked: loadGrammarPoints("B2")
        }
        Button {
            text: "C1 高级"
            highlighted: root.currentLevel === "C1"
            onClicked: loadGrammarPoints("C1")
        }
        Button {
            text: "C2 精通"
            highlighted: root.currentLevel === "C2"
            onClicked: loadGrammarPoints("C2")
        }
    }

    RowLayout {
        spacing: Theme.spacingLg

        GlassCard {
            Layout.preferredWidth: 260
            Layout.preferredHeight: 380

            Text {
                text: "语法知识点目录 (" + root.currentLevel + ")"
                color: Theme.textPrimary
                font.bold: true
            }

            ListView {
                id: grammarList
                width: parent.width
                height: parent.height - 40
                clip: true
                spacing: 4

                model: ListModel { id: grammarModel }

                delegate: Rectangle {
                    width: grammarList.width
                    height: 38
                    radius: Theme.radiusSm
                    color: grammarList.currentIndex === index ? Qt.rgba(99/255, 102/255, 241/255, 0.2) : Theme.backgroundTertiary

                    MouseArea {
                        anchors.fill: parent
                        onClicked: {
                            grammarList.currentIndex = index;
                            displayPoint(grammarModel.get(index));
                        }
                    }

                    Text {
                        anchors.centerIn: parent
                        text: model.title || model.name
                        color: Theme.textPrimary
                        font.pixelSize: Theme.fontSizeSm
                        elide: Text.ElideRight
                        width: parent.width - 20
                    }
                }
            }
        }

        GlassCard {
            Layout.preferredWidth: 420
            Layout.preferredHeight: 380

            Text {
                id: pointTitle
                text: "📖 语法标题"
                color: Theme.textPrimary
                font.pixelSize: Theme.fontSizeLg
                font.bold: true
            }

            Text {
                id: pointMeta
                text: "CEFR 等级: A1"
                color: Theme.secondary
                font.pixelSize: Theme.fontSizeSm
            }

            Text {
                id: pointExplanation
                width: parent.width
                text: "用法说明..."
                color: Theme.textSecondary
                font.pixelSize: Theme.fontSizeMd
                wrapMode: Text.Wrap
            }

            Rectangle {
                width: parent.width
                height: 1
                color: Theme.border
            }

            Text {
                text: "例句 (Examples):"
                color: Theme.textPrimary
                font.bold: true
            }

            Text {
                id: pointExamples
                text: "1. Sample sentence."
                color: Theme.textSecondary
                font.pixelSize: Theme.fontSizeMd
            }
        }
    }
}
