// ModbusDebuggerView.qml — PLC Modbus 联调测试工坊主视图（V13 原型落地）
//
// 功能对齐 018_UI架构原型_V13.html：
//   - 📡 Ping 链路诊断（建立 Modbus 连接前的网络层探路）
//   - Modbus TCP 连接参数配置（IP/Port/UnitID/仿真模式开关）
//   - 读取功能码选择：FC01/02/03/04/17/23
//   - 写入功能码选择：FC05/06/15/16
//   - 16位寄存器位解析器（LED 矩阵，双击表格行自动填入）
//   - 三标签子视图：实时监测表 / Canvas 趋势曲线 / 寄存器扫描探测器
//   - 物理报文 Hex 终端（实时 TX/RX/SYS 日志）
//   - 导入/导出 JSON 配置
//
// 数据流：
//   QML → modbusBridge.Slot → Python ModbusService
//   Python → modbusBridge.Signal → QML 更新 UI
//
// PLC-HMI 概念映射：
//   本视图 ≈ HMI 调试画面（PLC 操作员界面的 Modbus 诊断页）

import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs
import "../theme"
import "../components"

Item {
    id: root

    signal backToProjectList()

    // ── 连接状态 ──────────────────────────────────────────
    property bool _isConnected: false
    property int _subTabIndex: 0   // 0=监测 1=趋势 2=扫描

    // ── Bridge 信号连接 ────────────────────────────────────
    Connections {
        target: (typeof modbusBridge !== "undefined" && modbusBridge !== null) ? modbusBridge : null

        function onConnectionStateChanged(ok) {
            root._isConnected = ok
            if (ok) {
                connectBtn.text = "🔌 断开连接"
                connectBtn.palette.button = Theme.error
                _log("SYS", "连接已建立。")
                // 自动执行一次扫描
                _doRead()
            } else {
                connectBtn.text = "连接设备"
                connectBtn.palette.button = Theme.primary
            }
        }

        function onPingResultReceived(success, msg) {
            pingStatusRow.visible = true
            pingDot.color = success ? Theme.success : Theme.error
            pingText.text = msg
            pingText.color = success ? Theme.success : Theme.error
        }

        function onRegisterDataReceived(data) {
            // 清空并重建监测表
            registerModel.clear()
            for (var i = 0; i < data.length; i++) {
                registerModel.append(data[i])
            }
        }

        function onConsoleLogAppended(logType, hexStr) {
            var prefix = {
                "TX":   "<font color='#6366f1'>[TX]</font>",
                "RX":   "<font color='#10b981'>[RX]</font>",
                "SYS":  "<font color='#94a3b8'>[SYS]</font>",
                "ERR":  "<font color='#ef4444'>[ERR]</font>",
                "PING": "<font color='#f59e0b'>[PING]</font>",
            }[logType] || "[?]"
            consoleText.text += prefix + " " + hexStr + "\n"
            // 自动滚到底
            consoleFlickable.contentY = Math.max(0, consoleText.height - consoleFlickable.height)
        }

        function onScanCellUpdated(offset, isActive) {
            scannerGrid.updateCell(offset, isActive)
        }

        function onScanFinished() {
            startScanBtn.enabled = true
            startScanBtn.text = "⚡ 重新探测"
        }

        function onTrendDataUpdated(v1, v2) {
            trendCanvas.appendData(v1, v2)
        }
    }

    // ── 私有工具函数 ──────────────────────────────────────
    function _log(logType, msg) {
        if (typeof modbusBridge !== "undefined" && modbusBridge !== null) return  // Bridge 会推送
        // 无 Bridge 时直接写控制台（测试用）
        consoleText.text += "[" + logType + "] " + msg + "\n"
    }

    function _doRead() {
        if (!root._isConnected) return
        if (typeof modbusBridge === "undefined" || modbusBridge === null) return
        modbusBridge.readRegisters(
            fcCombo.currentValue,
            parseInt(startAddrField.text) || 0,
            parseInt(countField.text) || 10,
            endianCombo.currentValue,
            presetCombo.currentValue
        )
    }

    function _fillWriteSlot(addr, val, physicalAddr) {
        writeAddrField.text = addr.toString()
        writeValField.text = val.toString()
        // 同步到 16位解析器
        bitExpander.displayAddr = physicalAddr
        bitExpander.loadValue(val)
    }

    // ─────────────────────────────────────────────────────
    // 主布局
    // ─────────────────────────────────────────────────────

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Theme.spacingMd
        spacing: Theme.spacingMd

        // ── 页眉 ─────────────────────────────────────────
        RowLayout {
            Layout.fillWidth: true
            spacing: Theme.spacingMd

            Column {
                Layout.fillWidth: true
                spacing: 4
                Text {
                    text: "PLC Modbus 联调测试工坊"
                    font.pixelSize: Theme.fontSizeXxl
                    font.bold: true
                    color: Theme.textPrimary
                }
                Text {
                    text: "参考 GitHub 开源 (OpenPoll / ModbusMechanic) 设计 | 集成 Ping 诊断、16位解析器、趋势监控、区间扫描"
                    font.pixelSize: Theme.fontSizeSm
                    color: Theme.textMuted
                }
            }

            // 导入配置按钮
            Button {
                text: "⬆ 导入配置"
                font.pixelSize: Theme.fontSizeSm
                onClicked: importDialog.open()
            }

            // 导出配置按钮
            Button {
                text: "⬇ 导出配置"
                font.pixelSize: Theme.fontSizeSm
                onClicked: exportDialog.open()
            }
        }

        // ── 主双栏内容区 ─────────────────────────────────
        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: Theme.spacingMd

            // ────────────────────────────────────────────
            // 左栏（340px 固定宽，配置参数 + 位解析器）
            // ────────────────────────────────────────────
            ColumnLayout {
                Layout.preferredWidth: 340
                Layout.fillHeight: true
                spacing: Theme.spacingMd

                // ── 连接参数卡 ──────────────────────────
                GlassPanel {
                    Layout.fillWidth: true
                    implicitHeight: connectionCardCol.implicitHeight + Theme.spacingMd * 2

                    ColumnLayout {
                        id: connectionCardCol
                        anchors.fill: parent
                        anchors.margins: Theme.spacingMd
                        spacing: Theme.spacingSm

                        // 标题
                        RowLayout {
                            Layout.fillWidth: true
                            Text {
                                text: "🔌 Modbus TCP 连接参数"
                                color: Theme.textPrimary
                                font.pixelSize: Theme.fontSizeSm
                                font.bold: true
                                Layout.fillWidth: true
                            }
                            Rectangle {
                                width: simBadgeText.implicitWidth + 12
                                height: 18
                                radius: 9
                                color: Qt.rgba(0.96, 0.62, 0.04, 0.15)
                                border.color: Qt.rgba(0.96, 0.62, 0.04, 0.3)
                                Text {
                                    id: simBadgeText
                                    anchors.centerIn: parent
                                    text: "仿真就绪"
                                    color: Theme.warning
                                    font.pixelSize: Theme.fontSizeXs
                                }
                            }
                        }

                        // 分隔线
                        Rectangle { Layout.fillWidth: true; height: 1; color: Theme.border }

                        // IP 地址 + Ping 按钮
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 4
                            Text { text: "目标 PLC IP 地址"; color: Theme.textMuted; font.pixelSize: Theme.fontSizeXs }
                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 8
                                TextField {
                                    id: ipField
                                    Layout.fillWidth: true
                                    text: "192.168.1.10"
                                    placeholderText: "192.168.x.x"
                                    font.pixelSize: Theme.fontSizeSm
                                    color: Theme.textPrimary
                                    background: Rectangle {
                                        color: Qt.rgba(0,0,0,0.2)
                                        radius: Theme.radiusSm
                                        border.color: ipField.activeFocus ? Theme.primary : Theme.border
                                        border.width: 1
                                    }
                                }
                                Button {
                                    id: pingBtn
                                    text: "📡 Ping"
                                    font.pixelSize: Theme.fontSizeXs
                                    implicitHeight: 32
                                    onClicked: {
                                        if (typeof modbusBridge !== "undefined" && modbusBridge !== null) {
                                            modbusBridge.pingHost(ipField.text)
                                        } else {
                                            pingStatusRow.visible = true
                                            pingDot.color = Theme.success
                                            pingText.text = "Ping OK (仿真模式)"
                                            pingText.color = Theme.success
                                        }
                                    }
                                }
                            }
                            // Ping 状态行
                            RowLayout {
                                id: pingStatusRow
                                visible: false
                                spacing: 6
                                Rectangle {
                                    id: pingDot
                                    width: 6; height: 6; radius: 3
                                    color: Theme.textMuted
                                }
                                Text {
                                    id: pingText
                                    text: ""
                                    color: Theme.textMuted
                                    font.pixelSize: Theme.fontSizeXs
                                }
                            }
                        }

                        // Port + Unit ID
                        RowLayout {
                            Layout.fillWidth: true
                            spacing: Theme.spacingSm

                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 4
                                Text { text: "端口 (Port)"; color: Theme.textMuted; font.pixelSize: Theme.fontSizeXs }
                                TextField {
                                    id: portField
                                    Layout.fillWidth: true
                                    text: "502"
                                    validator: IntValidator { bottom: 1; top: 65535 }
                                    font.pixelSize: Theme.fontSizeSm
                                    color: Theme.textPrimary
                                    background: Rectangle {
                                        color: Qt.rgba(0,0,0,0.2)
                                        radius: Theme.radiusSm
                                        border.color: portField.activeFocus ? Theme.primary : Theme.border
                                        border.width: 1
                                    }
                                }
                            }
                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 4
                                Text { text: "站号 (Unit ID)"; color: Theme.textMuted; font.pixelSize: Theme.fontSizeXs }
                                TextField {
                                    id: slaveField
                                    Layout.fillWidth: true
                                    text: "1"
                                    validator: IntValidator { bottom: 1; top: 255 }
                                    font.pixelSize: Theme.fontSizeSm
                                    color: Theme.textPrimary
                                    background: Rectangle {
                                        color: Qt.rgba(0,0,0,0.2)
                                        radius: Theme.radiusSm
                                        border.color: slaveField.activeFocus ? Theme.primary : Theme.border
                                        border.width: 1
                                    }
                                }
                            }
                        }

                        // 仿真模式开关
                        RowLayout {
                            Layout.fillWidth: true
                            Text {
                                text: "启用本地仿真发生器"
                                color: Theme.textSecondary
                                font.pixelSize: Theme.fontSizeXs
                                Layout.fillWidth: true
                            }
                            CheckBox {
                                id: simChk
                                checked: true
                            }
                        }

                        // 连接/断开按钮
                        Button {
                            id: connectBtn
                            Layout.fillWidth: true
                            text: "连接设备"
                            font.pixelSize: Theme.fontSizeSm
                            font.bold: true
                            onClicked: {
                                if (typeof modbusBridge !== "undefined" && modbusBridge !== null) {
                                    if (root._isConnected) {
                                        modbusBridge.disconnectDevice()
                                    } else {
                                        modbusBridge.connectDevice(
                                            ipField.text,
                                            parseInt(portField.text) || 502,
                                            parseInt(slaveField.text) || 1,
                                            simChk.checked
                                        )
                                    }
                                } else {
                                    // 无 Bridge，纯仿真演示
                                    root._isConnected = !root._isConnected
                                    connectBtn.text = root._isConnected ? "🔌 断开连接" : "连接设备"
                                    if (root._isConnected) _doReadSim()
                                }
                            }
                        }
                    }
                }

                // ── 读取参数卡 ──────────────────────────
                GlassPanel {
                    Layout.fillWidth: true
                    implicitHeight: readCardCol.implicitHeight + Theme.spacingMd * 2

                    ColumnLayout {
                        id: readCardCol
                        anchors.fill: parent
                        anchors.margins: Theme.spacingMd
                        spacing: Theme.spacingSm

                        Text {
                            text: "🔍 寄存器读取测试"
                            color: Theme.textPrimary
                            font.pixelSize: Theme.fontSizeSm
                            font.bold: true
                        }
                        Rectangle { Layout.fillWidth: true; height: 1; color: Theme.border }

                        // 预设
                        ColumnLayout { Layout.fillWidth: true; spacing: 4
                            Text { text: "配置模板预设 (Presets)"; color: Theme.textMuted; font.pixelSize: Theme.fontSizeXs }
                            ComboBox {
                                id: presetCombo
                                Layout.fillWidth: true
                                font.pixelSize: Theme.fontSizeSm
                                model: ListModel {
                                    ListElement { text: "-- 自定义物理调试 --"; value: "custom" }
                                    ListElement { text: "西门子 S7-1200 风机控制"; value: "siemens_fan" }
                                    ListElement { text: "多路温度传感器读取"; value: "temp_monitor" }
                                }
                                textRole: "text"
                                property string currentValue: model.get(currentIndex).value
                            }
                        }

                        // 功能码
                        ColumnLayout { Layout.fillWidth: true; spacing: 4
                            Text { text: "寄存器区段 / 功能码"; color: Theme.textMuted; font.pixelSize: Theme.fontSizeXs }
                            ComboBox {
                                id: fcCombo
                                Layout.fillWidth: true
                                font.pixelSize: Theme.fontSizeSm
                                model: ListModel {
                                    ListElement { text: "03 读保持寄存器 (Holding)";  value: "03" }
                                    ListElement { text: "04 读输入寄存器 (Input)";     value: "04" }
                                    ListElement { text: "01 读线圈状态 (Coils)";       value: "01" }
                                    ListElement { text: "02 读离散输入 (Discrete)";    value: "02" }
                                    ListElement { text: "17 读设备描述字 (Slave ID)";  value: "17" }
                                    ListElement { text: "23 读写多寄存器 (RW Regs)";   value: "23" }
                                }
                                textRole: "text"
                                property string currentValue: model.get(currentIndex).value
                            }
                        }

                        // 起始地址 + 读取长度
                        RowLayout {
                            Layout.fillWidth: true; spacing: Theme.spacingSm
                            ColumnLayout { Layout.fillWidth: true; spacing: 4
                                Text { text: "起始地址"; color: Theme.textMuted; font.pixelSize: Theme.fontSizeXs }
                                TextField {
                                    id: startAddrField; Layout.fillWidth: true; text: "0"
                                    validator: IntValidator { bottom: 0; top: 65535 }
                                    font.pixelSize: Theme.fontSizeSm; color: Theme.textPrimary
                                    background: Rectangle { color: Qt.rgba(0,0,0,0.2); radius: Theme.radiusSm; border.color: startAddrField.activeFocus ? Theme.primary : Theme.border; border.width: 1 }
                                }
                            }
                            ColumnLayout { Layout.fillWidth: true; spacing: 4
                                Text { text: "读取长度"; color: Theme.textMuted; font.pixelSize: Theme.fontSizeXs }
                                TextField {
                                    id: countField; Layout.fillWidth: true; text: "10"
                                    validator: IntValidator { bottom: 1; top: 125 }
                                    font.pixelSize: Theme.fontSizeSm; color: Theme.textPrimary
                                    background: Rectangle { color: Qt.rgba(0,0,0,0.2); radius: Theme.radiusSm; border.color: countField.activeFocus ? Theme.primary : Theme.border; border.width: 1 }
                                }
                            }
                        }

                        // 字节序 + 轮询
                        RowLayout {
                            Layout.fillWidth: true
                            Text { text: "浮点字节序"; color: Theme.textMuted; font.pixelSize: Theme.fontSizeXs; Layout.fillWidth: true }
                            ComboBox {
                                id: endianCombo
                                implicitWidth: 150
                                font.pixelSize: Theme.fontSizeXs
                                model: ListModel {
                                    ListElement { text: "CDAB (Word Swap 西门子)"; value: "CDAB" }
                                    ListElement { text: "ABCD (Big-Endian)";       value: "ABCD" }
                                    ListElement { text: "BADC (Byte Swap)";        value: "BADC" }
                                    ListElement { text: "DCBA (Little-Endian)";    value: "DCBA" }
                                }
                                textRole: "text"
                                property string currentValue: model.get(currentIndex).value
                            }
                        }

                        RowLayout {
                            Layout.fillWidth: true
                            CheckBox {
                                id: pollChk
                                text: "周期性轮询 (1000ms)"
                                font.pixelSize: Theme.fontSizeXs
                                onCheckedChanged: {
                                    if (typeof modbusBridge !== "undefined" && modbusBridge !== null) {
                                        modbusBridge.setPolling(
                                            checked,
                                            fcCombo.currentValue,
                                            parseInt(startAddrField.text) || 0,
                                            parseInt(countField.text) || 10,
                                            endianCombo.currentValue,
                                            presetCombo.currentValue
                                        )
                                    }
                                }
                            }
                        }

                        Button {
                            id: readBtn
                            Layout.fillWidth: true
                            text: "单次扫描"
                            font.pixelSize: Theme.fontSizeSm
                            enabled: root._isConnected
                            onClicked: _doRead()
                        }
                    }
                }

                // ── 16位解析器卡 ────────────────────────
                GlassPanel {
                    Layout.fillWidth: true
                    implicitHeight: bitExpanderContent.implicitHeight + Theme.spacingMd * 2

                    ColumnLayout {
                        id: bitExpanderContent
                        anchors.fill: parent
                        anchors.margins: Theme.spacingMd
                        spacing: Theme.spacingSm

                        ModbusBitExpander {
                            id: bitExpander
                            Layout.fillWidth: true
                        }

                        Button {
                            Layout.fillWidth: true
                            text: "写入 PLC (FC06)"
                            font.pixelSize: Theme.fontSizeXs
                            enabled: root._isConnected
                            onClicked: {
                                writeAddrField.text = (parseInt(bitExpander.displayAddr) - 40001).toString()
                                writeValField.text = bitExpander.currentValue.toString()
                                writeFcCombo.currentIndex = 0  // FC06
                                if (typeof modbusBridge !== "undefined" && modbusBridge !== null) {
                                    modbusBridge.writeRegister("06", parseInt(writeAddrField.text), writeValField.text)
                                }
                            }
                        }
                    }
                }

                Item { Layout.fillHeight: true }  // 弹性填充

            } // 左栏结束

            // ────────────────────────────────────────────
            // 右栏（fill，子标签 + 数据面板）
            // ────────────────────────────────────────────
            ColumnLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                spacing: Theme.spacingMd

                // ── 子标签栏 ────────────────────────────
                TabBar {
                    id: subTabBar
                    Layout.fillWidth: true
                    tabs: ["📊 实时数据监测表", "📈 物理量趋势监测图", "🧭 寄存器扫描探测器"]
                    onCurrentTabChanged: {
                        root._subTabIndex = index
                        if (index === 1) {
                            // 切换到趋势图，启动数据推送
                            if (typeof modbusBridge !== "undefined" && modbusBridge !== null) {
                                modbusBridge.setTrendRunning(true)
                            }
                        } else {
                            if (typeof modbusBridge !== "undefined" && modbusBridge !== null) {
                                modbusBridge.setTrendRunning(false)
                            }
                        }
                    }
                }

                // ── 子视图 StackLayout ───────────────────
                StackLayout {
                    id: subStack
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    currentIndex: root._subTabIndex

                    // 标签 0：实时监测表
                    GlassPanel {
                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: Theme.spacingMd
                            spacing: Theme.spacingSm

                            RowLayout {
                                Layout.fillWidth: true
                                Text {
                                    text: "📊 物理通道监控 (双击行或点击「填入」可加载到写入槽和位解析器)"
                                    color: Theme.textPrimary
                                    font.pixelSize: Theme.fontSizeSm
                                    font.bold: true
                                    Layout.fillWidth: true
                                }
                                Text {
                                    id: pollStatusText
                                    text: "● 物理轮询中..."
                                    color: Theme.success
                                    font.pixelSize: Theme.fontSizeXs
                                    visible: pollChk.checked && root._isConnected
                                }
                            }

                            // 表头
                            Rectangle {
                                Layout.fillWidth: true
                                height: 36
                                color: Qt.rgba(0, 0, 0, 0.25)
                                radius: Theme.radiusSm

                                RowLayout {
                                    anchors.fill: parent
                                    anchors.leftMargin: Theme.spacingSm
                                    anchors.rightMargin: Theme.spacingSm
                                    spacing: 0

                                    Repeater {
                                        model: ["寄存器物理地址", "绑定符号 (Tag)", "十进制 (Dec)", "十六进制 (Hex)", "32位浮点解码", "操作"]
                                        Text {
                                            Layout.fillWidth: true
                                            text: modelData
                                            color: Theme.textSecondary
                                            font.pixelSize: Theme.fontSizeXs
                                            font.bold: true
                                            elide: Text.ElideRight
                                        }
                                    }
                                }
                            }

                            // 表格内容
                            ListView {
                                id: registerTableView
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                clip: true
                                model: ListModel { id: registerModel }

                                delegate: Rectangle {
                                    width: registerTableView.width
                                    height: 36
                                    color: index % 2 === 0 ? Qt.rgba(1,1,1,0.01) : "transparent"
                                    border.color: Theme.borderSubtle
                                    border.width: 1

                                    RowLayout {
                                        anchors.fill: parent
                                        anchors.leftMargin: Theme.spacingSm
                                        anchors.rightMargin: Theme.spacingSm
                                        spacing: 0

                                        Text {
                                            Layout.fillWidth: true
                                            text: model.physical || ""
                                            color: Theme.secondary
                                            font.pixelSize: Theme.fontSizeXs
                                            font.family: "Consolas, Courier New, monospace"
                                        }
                                        Text {
                                            Layout.fillWidth: true
                                            text: model.tag || ""
                                            color: Theme.textSecondary
                                            font.pixelSize: Theme.fontSizeXs
                                            elide: Text.ElideRight
                                        }
                                        Text {
                                            Layout.fillWidth: true
                                            text: model.dec !== undefined ? model.dec.toString() : ""
                                            color: Theme.textPrimary
                                            font.pixelSize: Theme.fontSizeXs
                                            font.family: "Consolas, Courier New, monospace"
                                        }
                                        Text {
                                            Layout.fillWidth: true
                                            text: model.hex || ""
                                            color: Theme.warning
                                            font.pixelSize: Theme.fontSizeXs
                                            font.family: "Consolas, Courier New, monospace"
                                        }
                                        Text {
                                            Layout.fillWidth: true
                                            text: model.float_decoded || ""
                                            color: Theme.textMuted
                                            font.pixelSize: Theme.fontSizeXs
                                        }
                                        Button {
                                            text: "✍ 填入"
                                            font.pixelSize: 10
                                            implicitHeight: 22
                                            implicitWidth: 50
                                            onClicked: {
                                                root._fillWriteSlot(model.address, model.dec, model.physical)
                                            }
                                        }
                                    }

                                    MouseArea {
                                        anchors.fill: parent
                                        acceptedButtons: Qt.NoButton
                                        onDoubleClicked: {
                                            root._fillWriteSlot(model.address, model.dec, model.physical)
                                        }
                                    }
                                }

                                Text {
                                    visible: registerModel.count === 0
                                    anchors.centerIn: parent
                                    text: "未连接设备，请配置参数后点击连接"
                                    color: Theme.textMuted
                                    font.pixelSize: Theme.fontSizeSm
                                }
                            }
                        }
                    }

                    // 标签 1：趋势图
                    GlassPanel {
                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: Theme.spacingMd
                            spacing: Theme.spacingSm

                            RowLayout {
                                Layout.fillWidth: true
                                Text {
                                    text: "📈 物理变送器动态波形曲线 (Trend Viewer)"
                                    color: Theme.textPrimary
                                    font.pixelSize: Theme.fontSizeSm
                                    font.bold: true
                                    Layout.fillWidth: true
                                }
                                Text {
                                    text: "追踪: 40002 (Speed_SP) / 40003 (Temp_REAL)"
                                    color: Theme.textMuted
                                    font.pixelSize: Theme.fontSizeXs
                                }
                            }

                            ModbusTrendCanvas {
                                id: trendCanvas
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                            }
                        }
                    }

                    // 标签 2：扫描探测器
                    GlassPanel {
                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: Theme.spacingMd
                            spacing: Theme.spacingSm

                            RowLayout {
                                Layout.fillWidth: true
                                Text {
                                    text: "🧭 寄存器区段扫描探测器 (Interrogator Scanner)"
                                    color: Theme.textPrimary
                                    font.pixelSize: Theme.fontSizeSm
                                    font.bold: true
                                    Layout.fillWidth: true
                                }
                                Button {
                                    id: startScanBtn
                                    text: "⚡ 立即探测 (0-99)"
                                    font.pixelSize: Theme.fontSizeSm
                                    onClicked: {
                                        scannerGrid.resetAll()
                                        startScanBtn.enabled = false
                                        startScanBtn.text = "扫描中..."
                                        if (typeof modbusBridge !== "undefined" && modbusBridge !== null) {
                                            modbusBridge.scanRegisters(0, 99)
                                        } else {
                                            // 无 Bridge，仿真渐进展示
                                            _simulateScan()
                                        }
                                    }
                                }
                            }

                            Flickable {
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                contentHeight: scannerGrid.implicitHeight
                                clip: true

                                ModbusScannerGrid {
                                    id: scannerGrid
                                    width: parent.width
                                    startOffset: 0
                                    onCellClicked: {
                                        startAddrField.text = offset.toString()
                                        subTabBar.currentTabIndex = 0
                                        root._subTabIndex = 0
                                        _doRead()
                                    }
                                }
                            }
                        }
                    }

                } // StackLayout 结束

                // ── 写入参数面板 ─────────────────────────
                GlassPanel {
                    Layout.fillWidth: true
                    implicitHeight: writeCardRow.implicitHeight + Theme.spacingMd * 2

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: Theme.spacingMd
                        spacing: Theme.spacingSm

                        Text {
                            text: "✍️ 物理参数下发写入"
                            color: Theme.textPrimary
                            font.pixelSize: Theme.fontSizeSm
                            font.bold: true
                        }
                        Rectangle { Layout.fillWidth: true; height: 1; color: Theme.border }

                        RowLayout {
                            id: writeCardRow
                            Layout.fillWidth: true
                            spacing: Theme.spacingMd

                            ColumnLayout { Layout.fillWidth: true; spacing: 4
                                Text { text: "写入功能码"; color: Theme.textMuted; font.pixelSize: Theme.fontSizeXs }
                                ComboBox {
                                    id: writeFcCombo
                                    Layout.fillWidth: true; font.pixelSize: Theme.fontSizeSm
                                    model: ListModel {
                                        ListElement { text: "06 写单个保持寄存器"; value: "06" }
                                        ListElement { text: "05 写单个线圈状态"; value: "05" }
                                        ListElement { text: "16 写多个保持寄存器"; value: "16" }
                                        ListElement { text: "15 写多个线圈状态"; value: "15" }
                                    }
                                    textRole: "text"
                                    property string currentValue: model.get(currentIndex).value
                                }
                            }
                            ColumnLayout { Layout.fillWidth: true; spacing: 4
                                Text { text: "目标偏移地址"; color: Theme.textMuted; font.pixelSize: Theme.fontSizeXs }
                                TextField {
                                    id: writeAddrField; Layout.fillWidth: true; text: "0"
                                    validator: IntValidator { bottom: 0; top: 65535 }
                                    font.pixelSize: Theme.fontSizeSm; color: Theme.textPrimary
                                    background: Rectangle { color: Qt.rgba(0,0,0,0.2); radius: Theme.radiusSm; border.color: writeAddrField.activeFocus ? Theme.primary : Theme.border; border.width: 1 }
                                }
                            }
                            ColumnLayout { Layout.fillWidth: true; spacing: 4
                                Text { text: "写入设定值 (Dec)"; color: Theme.textMuted; font.pixelSize: Theme.fontSizeXs }
                                TextField {
                                    id: writeValField; Layout.fillWidth: true; text: "0"
                                    font.pixelSize: Theme.fontSizeSm; color: Theme.textPrimary
                                    background: Rectangle { color: Qt.rgba(0,0,0,0.2); radius: Theme.radiusSm; border.color: writeValField.activeFocus ? Theme.primary : Theme.border; border.width: 1 }
                                }
                            }
                            Button {
                                id: writeBtn
                                text: "下发写入指令"
                                font.pixelSize: Theme.fontSizeSm
                                font.bold: true
                                enabled: root._isConnected
                                onClicked: {
                                    if (typeof modbusBridge !== "undefined" && modbusBridge !== null) {
                                        modbusBridge.writeRegister(
                                            writeFcCombo.currentValue,
                                            parseInt(writeAddrField.text) || 0,
                                            writeValField.text
                                        )
                                    }
                                }
                            }
                        }
                    }
                }

                // ── 报文控制台 ───────────────────────────
                GlassPanel {
                    Layout.fillWidth: true
                    implicitHeight: 160

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: Theme.spacingMd
                        spacing: Theme.spacingSm

                        RowLayout {
                            Layout.fillWidth: true
                            Text {
                                text: "📟 Modbus TCP 网口物理报文链路 (Live Traffic Trace)"
                                color: Theme.textPrimary
                                font.pixelSize: Theme.fontSizeSm
                                font.bold: true
                                Layout.fillWidth: true
                            }
                            Text {
                                text: "[清除日志]"
                                color: Theme.textMuted
                                font.pixelSize: Theme.fontSizeXs
                                MouseArea {
                                    anchors.fill: parent
                                    cursorShape: Qt.PointingHandCursor
                                    onClicked: consoleText.text = "[SYS] 监听网口 TCP/IP 502 端口物理链路已就绪...\n"
                                }
                            }
                        }

                        Flickable {
                            id: consoleFlickable
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            contentHeight: consoleText.height
                            clip: true

                            Rectangle {
                                anchors.fill: parent
                                color: "#040711"
                                radius: Theme.radiusSm

                                Text {
                                    id: consoleText
                                    anchors.left: parent.left
                                    anchors.right: parent.right
                                    anchors.margins: Theme.spacingSm
                                    text: "[SYS] 监听网口 TCP/IP 502 端口物理链路已就绪...\n"
                                    color: "#34d399"
                                    font.pixelSize: Theme.fontSizeXs
                                    font.family: "Consolas, Courier New, monospace"
                                    wrapMode: Text.WrapAnywhere
                                    textFormat: Text.RichText
                                }
                            }
                        }
                    }
                }

            } // 右栏结束

        } // RowLayout 结束

    } // ColumnLayout 主布局结束

    // ── 文件对话框（导入/导出） ─────────────────────────
    FileDialog {
        id: importDialog
        title: "导入 Modbus 配置文件"
        nameFilters: ["JSON 配置文件 (*.json)"]
        onAccepted: {
            if (typeof modbusBridge !== "undefined" && modbusBridge !== null) {
                var config = modbusBridge.importConfig(selectedFile.toString().replace("file:///", ""))
                if (config && config.ip) {
                    ipField.text = config.ip
                    portField.text = (config.port || 502).toString()
                    slaveField.text = (config.slave_id || 1).toString()
                    simChk.checked = config.sim_mode !== false
                }
            }
        }
    }

    FileDialog {
        id: exportDialog
        title: "导出 Modbus 配置文件"
        fileMode: FileDialog.SaveFile
        nameFilters: ["JSON 配置文件 (*.json)"]
        defaultSuffix: "json"
        onAccepted: {
            if (typeof modbusBridge !== "undefined" && modbusBridge !== null) {
                modbusBridge.exportConfig(selectedFile.toString().replace("file:///", ""))
            }
        }
    }

    // ── 无 Bridge 时的仿真扫描函数 ───────────────────────
    function _doReadSim() {
        // 本地仿真数据（无 Bridge 时使用）
        registerModel.clear()
        var tags = ["Fan_Speed_SP", "Fan_Status", "Fan_Current", "Fan_Temp_H", "Fan_Temp_L", "Fan_Warn"]
        for (var i = 0; i < 8; i++) {
            registerModel.append({
                address: i,
                physical: (40001 + i).toString(),
                tag: i < tags.length ? tags[i] : "DB10.DBW" + (i * 2),
                dec: Math.floor(Math.random() * 4000),
                hex: "0x" + Math.floor(Math.random() * 65535).toString(16).toUpperCase().padStart(4, "0"),
                float_decoded: (Math.random() * 200).toFixed(3),
                is_coil: false
            })
        }
    }

    property var _scanTimer: null

    function _simulateScan() {
        var step = 0
        var activeSet = [0,1,2,3,4,5,6,7,10,11,12,13,14,15,42,43]
        var timer = Qt.createQmlObject("import QtQuick; Timer { interval: 60; repeat: true }", root)
        timer.triggered.connect(function() {
            for (var j = 0; j < 5; j++) {
                var cellId = step * 5 + j
                if (cellId >= 100) break
                scannerGrid.updateCell(cellId, activeSet.indexOf(cellId) >= 0)
            }
            step++
            if (step >= 20) {
                timer.stop()
                timer.destroy()
                startScanBtn.enabled = true
                startScanBtn.text = "⚡ 重新探测"
            }
        })
        timer.start()
    }
}
