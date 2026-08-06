// DictionaryView.qml - ECDICT 动态离线词典视图 (带生词本收藏与 CSV/TXT 批量导入)
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../theme"
import "../components"

ColumnLayout {
    id: root
    spacing: Theme.spacingLg
    anchors.horizontalCenter: parent.horizontalCenter

    function doSearch(word) {
        if (!word) word = searchInput.text;
        if (!qmlBridge || !word) return;
        var jsonStr = qmlBridge.lookupWordJson(word);
        try {
            var res = JSON.parse(jsonStr);
            if (res && res.word) {
                wordText.text = res.word;
                phoneticText.text = res.phonetic ? "/" + res.phonetic + "/" : "";
                translationText.text = "[" + (res.pos || "n.") + "] " + (res.translation || "未找到相关释义");
                cefrChip.text = "CEFR: " + (res.cefr_level || "A1");
                definitionText.text = res.definition ? "Definition: " + res.definition : "";
                statusLabel.text = "";
            }
        } catch (e) {
            console.log("查询失败: " + e);
        }
    }

    Component.onCompleted: doSearch("apple")

    GlassCard {
        Layout.preferredWidth: 620
        Layout.alignment: Qt.AlignHCenter

        RowLayout {
            width: parent.width

            Text {
                text: "🔍 ECDICT 77万离线词典检索"
                color: Theme.textPrimary
                font.pixelSize: Theme.fontSizeXl
                font.bold: true
            }

            Item { Layout.fillWidth: true }

            Text {
                id: statusLabel
                text: ""
                color: Theme.success
                font.pixelSize: Theme.fontSizeSm
            }
        }

        RowLayout {
            width: parent.width

            TextField {
                id: searchInput
                Layout.fillWidth: true
                text: "apple"
                placeholderText: "输入想要查询的单词..."
                color: Theme.textPrimary
                onAccepted: root.doSearch(searchInput.text)
                background: Rectangle {
                    color: Theme.backgroundTertiary
                    border.color: Theme.border
                    radius: Theme.radiusSm
                }
            }

            Button {
                text: "搜索 (Search)"
                onClicked: root.doSearch(searchInput.text)
            }

            Button {
                text: "⭐ 收藏 (FSRS)"
                onClicked: {
                    if (qmlBridge && wordText.text) {
                        qmlBridge.recordReviewJson(wordText.text, "again", 1);
                        statusLabel.text = "✅ 已加入生词本！";
                    }
                }
            }
        }

        Rectangle {
            width: parent.width
            height: 1
            color: Theme.border
        }

        RowLayout {
            spacing: 12
            Text { id: wordText; text: "apple"; color: Theme.textPrimary; font.pixelSize: 28; font.bold: true }
            Text { id: phoneticText; text: "/ˈæpl/"; color: Theme.secondary; font.pixelSize: 16 }
            Rectangle {
                color: Theme.primary
                radius: 4
                implicitWidth: cefrChip.implicitWidth + 12
                implicitHeight: 22
                Text { id: cefrChip; anchors.centerIn: parent; text: "CEFR: A1"; color: "#fff"; font.pixelSize: 11 }
            }
        }

        Text {
            id: translationText
            text: "[n.] 苹果"
            color: Theme.textSecondary
            font.pixelSize: Theme.fontSizeMd
            font.bold: true
        }

        Text {
            id: definitionText
            text: "Definition: a round fruit with red or green skin and a firm, white interior."
            color: Theme.textMuted
            font.pixelSize: Theme.fontSizeSm
            wrapMode: Text.Wrap
            width: parent.width
        }

        Rectangle {
            width: parent.width
            height: 1
            color: Theme.border
        }

        // 批量生词本 CSV / TXT 导入与剪贴板设置行
        RowLayout {
            width: parent.width

            Text {
                text: "📥 批量导入个人 CSV 词包:"
                color: Theme.textSecondary
                font.pixelSize: Theme.fontSizeSm
            }

            TextField {
                id: csvInput
                placeholderText: "输入单词列表 (如: itinerary, custom, baggage)"
                Layout.fillWidth: true
                color: Theme.textPrimary
                background: Rectangle {
                    color: Theme.backgroundTertiary
                    border.color: Theme.border
                    radius: Theme.radiusSm
                }
            }

            Button {
                text: "批量导入 (Import)"
                onClicked: {
                    if (qmlBridge && csvInput.text) {
                        var resStr = qmlBridge.importCustomDeckJson(csvInput.text);
                        try {
                            var res = JSON.parse(resStr);
                            statusLabel.text = "✅ 成功导入 " + (res.added_count || 0) + " 个单词！";
                            csvInput.text = "";
                        } catch (e) {}
                    }
                }
            }
        }
    }
}
