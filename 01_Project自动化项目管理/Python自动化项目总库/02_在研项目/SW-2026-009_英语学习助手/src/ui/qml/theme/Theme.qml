// Theme.qml - SW-2026-009 QML 深色玻璃拟物设计系统单例
pragma Singleton

import QtQuick

QtObject {
    // ── 深色玻璃拟物基底色 ─────────────────────────────
    readonly property color background: "#020617"          // --bg-base 深蓝黑
    readonly property color surface: "#0f172a"             // --bg-surface 极深蓝（卡片表面）
    readonly property color sidebarBg: "#0f172a"           // 侧边栏玻璃背景
    readonly property color backgroundTertiary: "#1e293b"  // 三级背景色
    readonly property color bgCard: "#0f172a"              // 卡片背景色

    // ── 功能色 ─────────────────────────────────────────
    readonly property color primary: "#6366f1"             // 靛蓝主色
    readonly property color primaryHover: "#4f46e5"        // 靛蓝悬停
    readonly property color primaryGlow: Qt.rgba(0.388, 0.400, 0.945, 0.35)
    readonly property color secondary: "#38bdf8"           // 天蓝次色
    readonly property color success: "#10b981"             // 绿色
    readonly property color warning: "#f59e0b"             // 橙色
    readonly property color danger: "#ef4444"              // 红色

    // ── 玻璃拟物 Token ─────────────────────────────────
    readonly property color glassBg: Qt.rgba(1.0, 1.0, 1.0, 0.03)
    readonly property color glassBorder: Qt.rgba(1.0, 1.0, 1.0, 0.08)
    readonly property color glassHighlight: Qt.rgba(1.0, 1.0, 1.0, 0.06)

    // ── 高对比度文本色 ─────────────────────────────────
    readonly property color textPrimary: "#f1f5f9"         // 主文本 (对比度 >7:1)
    readonly property color textSecondary: "#cbd5e1"       // 次文本 (对比度 >4.5:1)
    readonly property color textMuted: "#94a3b8"           // 辅助文本 (对比度 >3:1)
    readonly property color textOnPrimary: "#ffffff"       // 主按钮文本纯白

    // ── 边框与分隔 ─────────────────────────────────────
    readonly property color border: Qt.rgba(1.0, 1.0, 1.0, 0.08)
    readonly property color borderSubtle: Qt.rgba(1.0, 1.0, 1.0, 0.04)

    // ── 尺寸与间距 Token ───────────────────────────────
    readonly property int sidebarWidth: 260
    readonly property int topbarHeight: 70

    readonly property int spacingXs: 4
    readonly property int spacingSm: 8
    readonly property int spacingMd: 16
    readonly property int spacingLg: 24
    readonly property int spacingXl: 32

    readonly property int radiusSm: 8
    readonly property int radiusMd: 12
    readonly property int radiusLg: 18

    readonly property int fontSizeXs: 11
    readonly property int fontSizeSm: 12
    readonly property int fontSizeMd: 14
    readonly property int fontSizeLg: 16
    readonly property int fontSizeXl: 20
    readonly property int fontSizeXxl: 28
}
