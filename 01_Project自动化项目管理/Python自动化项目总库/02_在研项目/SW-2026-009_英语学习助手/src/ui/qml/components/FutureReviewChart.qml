// FutureReviewChart.qml - 未来 7 天待复习预测柱状图组件
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../theme"

GlassCard {
    id: root
    Layout.fillWidth: true
    implicitHeight: 180

    function refreshChart() {
        if (!qmlBridge) return;
        var jsonStr = qmlBridge.getFutureReviewStatsJson();
        try {
            var list = JSON.parse(jsonStr);
            chartModel.clear();
            var maxCnt = 1;
            for (var i = 0; i < list.length; i++) {
                if (list[i].count > maxCnt) maxCnt = list[i].count;
            }
            for (var j = 0; j < list.length; j++) {
                var item = list[j];
                var ratio = Math.max(item.count / maxCnt, 0.08);
                chartModel.append({
                    "day": item.day,
                    "date": item.date,
                    "count": item.count,
                    "barRatio": ratio
                });
            }
        } catch (e) {
            console.log("加载 7 天预测图表失败: " + e);
        }
    }

    Component.onCompleted: refreshChart()

    Connections {
        target: qmlBridge
        function onProgressUpdated() {
            root.refreshChart();
        }
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: Theme.spacingMd

        RowLayout {
            width: parent.width

            Text {
                text: "📈 未来 7 天待复习负荷预测 (FSRS Prediction)"
                color: Theme.textPrimary
                font.bold: true
                font.pixelSize: Theme.fontSizeLg
            }

            Item { Layout.fillWidth: true }

            Text {
                text: "智能规划复习节奏"
                color: Theme.textMuted
                font.pixelSize: Theme.fontSizeSm
            }
        }

        // 7 天柱状图容器
        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 16

            Repeater {
                model: ListModel { id: chartModel }

                delegate: ColumnLayout {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    spacing: 6

                    // 柱状顶部数字
                    Text {
                        Layout.alignment: Qt.AlignHCenter
                        text: model.count + "个"
                        color: model.count > 0 ? Theme.secondary : Theme.textMuted
                        font.pixelSize: Theme.fontSizeXs
                        font.bold: true
                    }

                    // 柱状体容器
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        color: "transparent"

                        Rectangle {
                            anchors.bottom: parent.bottom
                            anchors.horizontalCenter: parent.horizontalCenter
                            width: parent.width * 0.6
                            height: Math.max(parent.height * model.barRatio, 6)
                            radius: 6
                            color: index === 0 ? Theme.primary : Qt.rgba(56/255, 189/255, 248/255, 0.6)
                            border.color: index === 0 ? Theme.success : Theme.secondary
                        }
                    }

                    // 日期标签
                    Text {
                        Layout.alignment: Qt.AlignHCenter
                        text: model.day
                        color: index === 0 ? Theme.primary : Theme.textSecondary
                        font.pixelSize: Theme.fontSizeSm
                        font.bold: index === 0
                    }
                }
            }
        }
    }
}
