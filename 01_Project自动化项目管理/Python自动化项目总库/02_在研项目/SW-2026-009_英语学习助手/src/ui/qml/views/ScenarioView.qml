// ScenarioView.qml - 出差情景对话视图 (支持 27+ 场景点击切换与双语朗读)
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../theme"
import "../components"

RowLayout {
    id: root
    spacing: Theme.spacingLg

    property var currentScenarioData: null

    function loadScenarioList() {
        if (!qmlBridge) return;
        var jsonStr = qmlBridge.getScenariosJson();
        try {
            var list = JSON.parse(jsonStr);
            scenarioModel.clear();
            for (var i = 0; i < list.length; i++) {
                scenarioModel.append(list[i]);
            }
            if (list.length > 0) {
                scenarioList.currentIndex = 0;
                loadScenarioDetail(list[0].id);
            }
        } catch (e) {
            console.log("解析场景列表失败: " + e);
        }
    }

    function loadScenarioDetail(scenarioId) {
        if (!qmlBridge) return;
        var jsonStr = qmlBridge.getScenarioDetailJson(scenarioId);
        try {
            var detail = JSON.parse(jsonStr);
            root.currentScenarioData = detail;

            // 更新标题与分类
            var title = detail.title || identifier;
            var titleEn = detail.title_en || "";
            headerTitle.text = "📍 " + title + (titleEn ? " (" + titleEn + ")" : "");
            headerCategory.text = "场景分类: " + (detail.category || "日常交流") + " • 难度: " + (detail.difficulty || "初级");

            // 填充对话气泡流
            chatModel.clear();
            var lines = detail.lines || detail.dialogue || [];
            for (var j = 0; j < lines.length; j++) {
                var line = lines[j];
                var speaker = line.speaker || "";
                var isB = (speaker.toLowerCase() === "staff" || speaker.toLowerCase() === "b" || speaker.toLowerCase() === "clerk" || speaker.toLowerCase() === "officer");
                chatModel.append({
                    "enText": line.text || "",
                    "cnText": line.translation || "",
                    "isSpeakerB": isB
                });
            }
        } catch (e) {
            console.log("加载场景详情失败: " + e);
        }
    }

    Component.onCompleted: loadScenarioList()

    // 左侧：27+ 实战场景列表
    GlassCard {
        Layout.preferredWidth: 320
        Layout.fillHeight: true

        Text {
            text: "💬 出差实战场景 (" + scenarioModel.count + ")"
            color: Theme.textPrimary
            font.pixelSize: Theme.fontSizeLg
            font.bold: true
        }

        ListView {
            id: scenarioList
            width: parent.width
            height: parent.height - 40
            clip: true
            spacing: Theme.spacingSm

            model: ListModel { id: scenarioModel }

            delegate: Rectangle {
                width: scenarioList.width
                height: 62
                radius: Theme.radiusMd
                color: scenarioList.currentIndex === index ? Qt.rgba(99/255, 102/255, 241/255, 0.25) : Theme.backgroundTertiary
                border.color: scenarioList.currentIndex === index ? Theme.primary : Theme.border
                border.width: 1

                MouseArea {
                    anchors.fill: parent
                    onClicked: {
                        scenarioList.currentIndex = index;
                        loadScenarioDetail(model.id);
                    }
                }

                Column {
                    anchors.fill: parent
                    anchors.margins: 10
                    spacing: 2

                    Row {
                        width: parent.width
                        Text { text: model.title; color: Theme.textPrimary; font.bold: true; font.pixelSize: Theme.fontSizeMd }
                        Item { Layout.fillWidth: true; width: 1; height: 1 }
                        Rectangle {
                            color: Qt.rgba(56/255, 189/255, 248/255, 0.15)
                            radius: 4
                            implicitWidth: levelText.implicitWidth + 8
                            implicitHeight: 18
                            Text { id: levelText; anchors.centerIn: parent; text: model.level; color: Theme.secondary; font.pixelSize: 10 }
                        }
                    }

                    Text { text: model.title_en; color: Theme.textSecondary; font.pixelSize: Theme.fontSizeSm; elide: Text.ElideRight; width: parent.width }
                }
            }
        }
    }

    // 右侧：动态对话流与 TTS 朗读窗口
    GlassCard {
        Layout.fillWidth: true
        Layout.fillHeight: true

        RowLayout {
            width: parent.width

            Column {
                Layout.fillWidth: true
                Text {
                    id: headerTitle
                    text: "📍 场景标题"
                    color: Theme.textPrimary
                    font.pixelSize: Theme.fontSizeLg
                    font.bold: true
                }
                Text {
                    id: headerCategory
                    text: "场景分类信息"
                    color: Theme.textMuted
                    font.pixelSize: Theme.fontSizeSm
                }
            }

            Button {
                text: "🔊 朗读完整对话 (SAPI5)"
                onClicked: {
                    if (!qmlBridge || !root.currentScenarioData) return;
                    var lines = root.currentScenarioData.lines || [];
                    var fullText = "";
                    for (var i = 0; i < lines.length; i++) {
                        fullText += lines[i].text + ". ";
                    }
                    qmlBridge.speakText(fullText);
                }
            }
        }

        Rectangle {
            width: parent.width
            height: 1
            color: Theme.border
        }

        ScrollView {
            width: parent.width
            height: parent.height - 80
            clip: true

            ListView {
                id: chatListView
                width: parent.width
                spacing: Theme.spacingMd

                model: ListModel { id: chatModel }

                delegate: Item {
                    width: chatListView.width
                    height: bubble.height + 6

                    ChatBubble {
                        id: bubble
                        enText: model.enText
                        cnText: model.cnText
                        isSpeakerB: model.isSpeakerB
                        anchors.right: model.isSpeakerB ? parent.right : undefined
                        anchors.left: model.isSpeakerB ? undefined : parent.left
                    }
                }
            }
        }
    }
}
