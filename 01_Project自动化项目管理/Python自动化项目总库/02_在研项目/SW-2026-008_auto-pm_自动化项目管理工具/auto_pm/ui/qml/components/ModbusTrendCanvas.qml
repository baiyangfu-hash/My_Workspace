// ModbusTrendCanvas.qml — 物理量趋势波形 Canvas 组件（对齐 V13 原型）
//
// 功能：
//   - 使用 QML Canvas + Timer 定时刷新绘制实时动态折线图
//   - 双通道折线（蓝色=v1 设定值，绿色=v2 反馈值）带发光描边
//   - appendData(v1, v2)：追加新数据点（由 ModbusBridge.trendDataUpdated 信号驱动）
//   - 保留最多 maxPoints 个数据点，超出后循环移位
//   - 外部控制 running 属性启停内置 Timer
//
// 用法：
//   ModbusTrendCanvas {
//       id: trendCanvas
//       running: isConnected
//   }
//   // 外部数据注入（通过 Bridge Signal）：
//   Connections {
//       target: modbusBridge
//       function onTrendDataUpdated(v1, v2) { trendCanvas.appendData(v1, v2) }
//   }

import QtQuick
import "../theme"

Rectangle {
    id: root

    // ── 公开属性 ────────────────────────────────────────
    property bool running: false          // 控制是否启动内置 Timer
    property int maxPoints: 60            // 最大数据点数
    property int yMin: 0                  // Y 轴最小值
    property int yMax: 4000              // Y 轴最大值
    property string label1: "Fan_Speed_SP (设定值)"
    property string label2: "Temp_Zone_REAL (解码实数)"

    // ── 内部状态 ─────────────────────────────────────────
    property var _data1: []
    property var _data2: []

    color: Qt.rgba(0, 0, 0, 0.3)
    radius: Theme.radiusSm
    border.color: Theme.border
    border.width: 1
    clip: true

    // ── 外部数据注入接口 ──────────────────────────────────
    function appendData(v1, v2) {
        var d1 = _data1.slice()
        var d2 = _data2.slice()
        d1.push(v1)
        d2.push(v2)
        if (d1.length > root.maxPoints) d1 = d1.slice(d1.length - root.maxPoints)
        if (d2.length > root.maxPoints) d2 = d2.slice(d2.length - root.maxPoints)
        root._data1 = d1
        root._data2 = d2
        canvas.requestPaint()
    }

    function clearData() {
        root._data1 = []
        root._data2 = []
        canvas.requestPaint()
    }

    // ── 图例区域 ──────────────────────────────────────────
    Row {
        id: legendRow
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.margins: 10
        spacing: 16
        z: 10

        Row {
            spacing: 6
            Rectangle { width: 8; height: 8; radius: 4; color: "#6366f1"; anchors.verticalCenter: parent.verticalCenter }
            Text { text: root.label1; color: Theme.textMuted; font.pixelSize: Theme.fontSizeXs }
        }
        Row {
            spacing: 6
            Rectangle { width: 8; height: 8; radius: 4; color: "#10b981"; anchors.verticalCenter: parent.verticalCenter }
            Text { text: root.label2; color: Theme.textMuted; font.pixelSize: Theme.fontSizeXs }
        }
    }

    // ── Canvas 绘制区 ─────────────────────────────────────
    Canvas {
        id: canvas
        anchors.fill: parent
        anchors.topMargin: 30  // 留出图例空间

        onPaint: {
            var ctx = getContext("2d")
            var w = width
            var h = height

            ctx.clearRect(0, 0, w, h)

            // 网格线
            ctx.strokeStyle = "rgba(255, 255, 255, 0.04)"
            ctx.lineWidth = 1
            var gridX = 40, gridY = 30
            for (var x = 0; x < w; x += gridX) {
                ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, h); ctx.stroke()
            }
            for (var y = 0; y < h; y += gridY) {
                ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(w, y); ctx.stroke()
            }

            if (root._data1.length === 0) {
                ctx.fillStyle = "rgba(148, 163, 184, 0.3)"
                ctx.font = "12px Consolas"
                ctx.textAlign = "center"
                ctx.fillText("等待数据... (请先连接并切换到趋势图标签)", w / 2, h / 2)
                return
            }

            var mapY = function(val) {
                return h - ((val - root.yMin) / (root.yMax - root.yMin)) * (h - 10) - 5
            }

            var drawLine = function(data, color) {
                if (data.length < 2) return
                ctx.strokeStyle = color
                ctx.shadowColor = color
                ctx.shadowBlur = 8
                ctx.lineWidth = 2.5
                ctx.lineJoin = "round"
                ctx.beginPath()
                for (var i = 0; i < data.length; i++) {
                    var px = (i / (root.maxPoints - 1)) * w
                    var py = mapY(data[i])
                    if (i === 0) ctx.moveTo(px, py)
                    else ctx.lineTo(px, py)
                }
                ctx.stroke()
                ctx.shadowBlur = 0
            }

            drawLine(root._data1, "#6366f1")  // 蓝色：设定值
            drawLine(root._data2, "#10b981")  // 绿色：反馈值

            // 当前值标注（最新数据点）
            if (root._data1.length > 0) {
                var lastV1 = root._data1[root._data1.length - 1]
                var lastV2 = root._data2.length > 0 ? root._data2[root._data2.length - 1] : 0
                var lx = w - 2
                ctx.font = "10px Consolas"
                ctx.textAlign = "right"
                ctx.fillStyle = "#6366f1"
                ctx.fillText(lastV1.toFixed(0), lx, mapY(lastV1) - 4)
                ctx.fillStyle = "#10b981"
                ctx.fillText(lastV2.toFixed(0), lx, mapY(lastV2) + 12)
            }
        }
    }

    // ── 无数据占位文字（data 为空时显示） ────────────────
    Text {
        visible: root._data1.length === 0
        anchors.centerIn: parent
        text: "📈 连接设备并切换到此标签后自动开始绘制趋势曲线"
        color: Theme.textMuted
        font.pixelSize: Theme.fontSizeSm
    }
}
