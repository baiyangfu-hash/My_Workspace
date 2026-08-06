// GlassCard.qml - 深色玻璃拟物卡片容器
import QtQuick
import QtQuick.Controls
import "../theme"

Rectangle {
    id: root

    default property alias contentData: contentColumn.data

    property int padding: Theme.spacingLg
    property color cardColor: Theme.bgCard
    property color borderColor: Theme.border

    radius: Theme.radiusLg
    color: cardColor
    border.color: borderColor
    border.width: 1

    implicitWidth: contentColumn.implicitWidth + padding * 2
    implicitHeight: contentColumn.implicitHeight + padding * 2

    Column {
        id: contentColumn
        anchors.fill: parent
        anchors.margins: root.padding
        spacing: Theme.spacingMd
    }
}
