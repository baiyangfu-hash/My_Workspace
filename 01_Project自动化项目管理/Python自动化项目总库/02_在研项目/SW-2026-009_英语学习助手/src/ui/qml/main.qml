// main.qml - 英语学习助手 SW-2026-009 QML 主窗口架构 (多邻国/博树游戏化挂载版)
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "theme"
import "components"
import "views"

ApplicationWindow {
    id: window
    width: 1200
    height: 780
    visible: true
    title: "英语学习助手 SW-2026-009 (QML 深色玻璃拟物版)"

    color: Theme.background

    function syncUserLevel() {
        if (!qmlBridge) return;
        var progStr = qmlBridge.getUserProgressJson();
        try {
            var prog = JSON.parse(progStr);
            var lvl = prog.current_level || "A1";
            var levels = ["A1", "A2", "B1", "B2", "C1", "C2"];
            var idx = levels.indexOf(lvl.toUpperCase());
            if (idx >= 0) {
                levelSelector.currentIndex = idx;
            }
            if (prog.streak_days !== undefined) {
                streakBadgeText.text = "🔥 " + prog.streak_days + " 天连胜";
            }
        } catch (e) {}
    }

    Component.onCompleted: syncUserLevel()

    Connections {
        target: qmlBridge
        function onProgressUpdated() {
            window.syncUserLevel();
            dashboardView.refreshDashboard();
        }
    }

    RowLayout {
        anchors.fill: parent
        spacing: 0

        // 侧边栏 (Sidebar)
        Rectangle {
            Layout.preferredWidth: Theme.sidebarWidth
            Layout.fillHeight: true
            color: Theme.sidebarBg
            border.color: Theme.border
            border.width: 1

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: Theme.spacingMd
                spacing: Theme.spacingMd

                // Brand 品牌信息
                RowLayout {
                    spacing: 12
                    Rectangle {
                        width: 40
                        height: 40
                        radius: 12
                        color: Theme.primary
                        Text { anchors.centerIn: parent; text: "✈️"; font.pixelSize: 20 }
                    }
                    Column {
                        Text { text: "English Learning"; color: Theme.textOnPrimary; font.bold: true; font.pixelSize: 16 }
                        Text { text: "v1.6.0 QML 离线版"; color: Theme.textMuted; font.pixelSize: 11 }
                    }
                }

                Rectangle { Layout.fillWidth: true; height: 1; color: Theme.border }

                Text {
                    text: "核心学习模块"
                    color: Theme.textMuted
                    font.pixelSize: Theme.fontSizeXs
                    font.bold: true
                }

                // 导航菜单
                ListView {
                    id: navList
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    spacing: 6
                    clip: true

                    model: ListModel {
                        ListElement { title: "学习驾驶舱"; iconText: "📊"; viewIndex: 0 }
                        ListElement { title: "出差情景对话"; iconText: "💬"; viewIndex: 1 }
                        ListElement { title: "FSRS 记忆背词"; iconText: "🎴"; viewIndex: 2 }
                        ListElement { title: "听写&连词成句"; iconText: "🎧"; viewIndex: 3 }
                        ListElement { title: "CEFR 语法精讲"; iconText: "📖"; viewIndex: 4 }
                        ListElement { title: "ECDICT 离线词典"; iconText: "🔍"; viewIndex: 5 }
                    }

                    delegate: Rectangle {
                        width: navList.width
                        height: 44
                        radius: Theme.radiusMd
                        color: ListView.isCurrentItem ? Qt.rgba(99/255, 102/255, 241/255, 0.15) : "transparent"
                        border.color: ListView.isCurrentItem ? Qt.rgba(99/255, 102/255, 241/255, 0.4) : "transparent"

                        MouseArea {
                            anchors.fill: parent
                            onClicked: {
                                navList.currentIndex = index
                                mainStack.currentIndex = model.viewIndex
                            }
                        }

                        RowLayout {
                            anchors.fill: parent
                            anchors.leftMargin: 14
                            anchors.rightMargin: 14
                            spacing: 12

                            Text { text: model.iconText; font.pixelSize: 18 }
                            Text {
                                text: model.title
                                color: ListView.isCurrentItem ? Theme.textOnPrimary : Theme.textSecondary
                                font.pixelSize: Theme.fontSizeMd
                                font.weight: ListView.isCurrentItem ? Font.Bold : Font.Normal
                            }
                        }
                    }
                }
            }
        }

        // 主视图展示区域
        ColumnLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 0

            // 顶栏 (Topbar) - 挂载多邻国/博树游戏化勋章
            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: Theme.topbarHeight
                color: Qt.rgba(15/255, 23/255, 42/255, 0.5)
                border.color: Theme.border
                border.width: 1

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: Theme.spacingLg
                    spacing: 12

                    Column {
                        Text {
                            text: mainStack.currentIndex === 0 ? "📊 学习驾驶舱" :
                                  mainStack.currentIndex === 1 ? "💬 出差情景对话" :
                                  mainStack.currentIndex === 2 ? "🎴 FSRS 记忆背词" :
                                  mainStack.currentIndex === 3 ? "🎧 听写&多邻国连词成句" :
                                  mainStack.currentIndex === 4 ? "📖 CEFR 语法精讲" : "🔍 ECDICT 离线词典"
                            color: Theme.textPrimary
                            font.pixelSize: Theme.fontSizeXl
                            font.bold: true
                        }
                        Text {
                            text: "纯本地离线运行 • 5大过程组治理"
                            color: Theme.textMuted
                            font.pixelSize: Theme.fontSizeSm
                        }
                    }

                    Item { Layout.fillWidth: true }

                    // 真实 SQLite 数据库绑定的连续打卡天数勋章
                    Rectangle {
                        color: Qt.rgba(255/255, 150/255, 0/255, 0.15)
                        border.color: Qt.rgba(255/255, 150/255, 0/255, 0.5)
                        radius: 16
                        implicitWidth: 110
                        implicitHeight: 30
                        Text {
                            id: streakBadgeText
                            anchors.centerIn: parent
                            text: "🔥 1 天打卡"
                            color: "#ff9600"
                            font.bold: true
                            font.pixelSize: 12
                        }
                    }

                    TextField {
                        id: topbarSearch
                        placeholderText: "🔍 快捷查询单词..."
                        color: Theme.textPrimary
                        implicitWidth: 160
                        onAccepted: {
                            if (topbarSearch.text) {
                                mainStack.currentIndex = 5;
                                navList.currentIndex = 5;
                                dictionaryView.doSearch(topbarSearch.text);
                            }
                        }
                        background: Rectangle {
                            color: Theme.backgroundTertiary
                            border.color: Theme.border
                            radius: Theme.radiusSm
                        }
                    }

                    // 可自由切换的 CEFR 等级选择下拉框
                    ComboBox {
                        id: levelSelector
                        implicitWidth: 175
                        implicitHeight: 34
                        model: [
                            "🎯 目标: A1 (入门)",
                            "🎯 目标: A2 (基础)",
                            "🎯 目标: B1 (商务/进阶)",
                            "🎯 目标: B2 (中级)",
                            "🎯 目标: C1 (高级)",
                            "🎯 目标: C2 (精通)"
                        ]
                        currentIndex: 0
                        onActivated: function(index) {
                            var levels = ["A1", "A2", "B1", "B2", "C1", "C2"];
                            var selLevel = levels[index];
                            if (qmlBridge) {
                                qmlBridge.setUserLevelJson(selLevel);
                            }
                        }
                    }
                }
            }

            // StackLayout 视图容器
            StackLayout {
                id: mainStack
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.margins: Theme.spacingLg
                currentIndex: 0

                DashboardView { id: dashboardView }
                ScenarioView { id: scenarioView }
                VocabView { id: vocabView }
                DictationView { id: dictationView }
                GrammarView { id: grammarView }
                DictionaryView { id: dictionaryView }
            }
        }
    }
}
