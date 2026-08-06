// DashboardView.qml - 动态学习驾驶舱视图
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../theme"
import "../components"

ScrollView {
    id: root

    contentWidth: availableWidth

    function refreshDashboard() {
        if (!qmlBridge) return;

        // 1. 获取进度
        var progStr = qmlBridge.getUserProgressJson();
        try {
            var prog = JSON.parse(progStr);
            statVocab.valueText = (prog.vocab_mastered || 60) + " / " + (prog.total_vocab || 500);
            statStreak.valueText = (prog.streak_days || 5) + " 天";
        } catch (e) {}

        // 2. 获取每日计划
        var planStr = qmlBridge.getDailyPlanJson();
        try {
            var plan = JSON.parse(planStr);
            if (plan.tasks && plan.tasks.length > 0) {
                planTaskModel.clear();
                for (var i = 0; i < plan.tasks.length; i++) {
                    var t = plan.tasks[i];
                    planTaskModel.append({
                        "name": t.name || t.description || "学习任务",
                        "minutes": (t.estimated_minutes || 10) + " 分钟"
                    });
                }
            }
        } catch (e) {}
    }

    Component.onCompleted: refreshDashboard()

    ColumnLayout {
        width: parent.width
        spacing: Theme.spacingLg

        // 4大指标卡行
        RowLayout {
            Layout.fillWidth: true
            spacing: Theme.spacingMd

            StatCard {
                id: statVocab
                Layout.fillWidth: true
                iconText: "📚"
                titleText: "已掌握词汇"
                valueText: "60 / 500"
                iconBgColor: Qt.rgba(99/255, 102/255, 241/255, 0.2)
                iconTextColor: Theme.primary
            }

            StatCard {
                id: statStreak
                Layout.fillWidth: true
                iconText: "🔥"
                titleText: "连续打卡天数"
                valueText: "5 天"
                iconBgColor: Qt.rgba(56/255, 189/255, 248/255, 0.2)
                iconTextColor: Theme.secondary
            }

            StatCard {
                Layout.fillWidth: true
                iconText: "⏱️"
                titleText: "今日学习时长"
                valueText: "19 分钟"
                iconBgColor: Qt.rgba(16/255, 185/255, 129/255, 0.2)
                iconTextColor: Theme.success
            }

            StatCard {
                Layout.fillWidth: true
                iconText: "⚡"
                titleText: "FSRS 待复习"
                valueText: "10 个"
                iconBgColor: Qt.rgba(245/255, 158/255, 11/255, 0.2)
                iconTextColor: Theme.warning
            }
        }

        // FSRS 未来 7 天待复习负荷预测柱状图
        FutureReviewChart {
            id: futureChart
            Layout.fillWidth: true
        }

        // 双列布局：今日计划 + 6个月路线图
        RowLayout {
            Layout.fillWidth: true
            spacing: Theme.spacingLg

            // 今日计划
            GlassCard {
                Layout.fillWidth: true
                Layout.preferredWidth: 1

                Text {
                    text: "📋 今日推荐学习计划"
                    color: Theme.textPrimary
                    font.pixelSize: Theme.fontSizeLg
                    font.bold: true
                }

                ListView {
                    id: planListView
                    width: parent.width
                    height: 160
                    spacing: Theme.spacingSm
                    clip: true

                    model: ListModel {
                        id: planTaskModel
                        ListElement { name: "📝 新词学习 (10 个)"; minutes: "15 分钟" }
                        ListElement { name: "🔄 FSRS 单词复习"; minutes: "10 分钟" }
                        ListElement { name: "💬 出差对话 (机场海关)"; minutes: "10 分钟" }
                        ListElement { name: "🎧 听写练习 (10 句)"; minutes: "10 分钟" }
                    }

                    delegate: Rectangle {
                        width: planListView.width
                        height: 38
                        color: Theme.backgroundTertiary
                        radius: Theme.radiusSm

                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: 10
                            Text { text: model.name; color: Theme.textPrimary; font.pixelSize: Theme.fontSizeSm }
                            Item { Layout.fillWidth: true }
                            Text { text: model.minutes; color: Theme.secondary; font.pixelSize: Theme.fontSizeSm }
                        }
                    }
                }
            }

            // 路线图
            GlassCard {
                Layout.fillWidth: true
                Layout.preferredWidth: 1

                Text {
                    text: "🗺️ 美国出差 6 个月阶段路线图"
                    color: Theme.textPrimary
                    font.pixelSize: Theme.fontSizeLg
                    font.bold: true
                }

                Text {
                    width: parent.width
                    text: "阶段 1 (1-3月): 掌握 A1/A2 基础 1500 词汇，熟练应对美国机场过关、打车问路、酒店入住、星巴克点餐等 15 个高频生活场景。\n\n阶段 2 (4-6月): 进阶 B1 3000 词汇，掌握商务会议闲聊、租车服务、紧急求助与邮件书写。"
                    color: Theme.textSecondary
                    font.pixelSize: Theme.fontSizeMd
                    wrapMode: Text.Wrap
                }
            }
        }
    }
}
