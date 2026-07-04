// Theme.qml - V0.6.0 设计系统映射（CSS 变量 → QML Theme 属性）
//
// 映射自 02_设计/GUI原型设计.md §15.6 设计系统映射表
// Week 1 PoC 版本：包含 5 个明确 token + 推导基础 token
// Week 2-3 补充完整 20+ token（含阴影/动画等）
//
// QML 端使用方式：import "../theme"  // 自动加载为单例
//                 color: Theme.primary

pragma Singleton

import QtQuick

QtObject {
    // ── 颜色 token（映射自 HTML 原型 CSS 变量）──────────
    readonly property color sidebarBg: "#1e1e2e"          // --sidebar-bg
    readonly property color primary: "#4a6cf7"            // --primary
    readonly property color success: "#22c55e"            // --success
    readonly property color badgePlc: "#2563eb"           // --badge-plc
    readonly property color phaseDeveloping: "#3b82f6"    // --phase-developing

    // ── 推导颜色（基础设计系统）─────────────────────────
    readonly property color background: "#ffffff"         // 主背景
    readonly property color surface: "#f8fafc"            // 卡片表面
    readonly property color textPrimary: "#1e293b"        // 主文本
    readonly property color textSecondary: "#64748b"      // 次文本
    readonly property color textMuted: "#94a3b8"          // 静音文本
    readonly property color border: "#e2e8f0"             // 边框
    readonly property color badgePython: "#16a34a"        // Python 徽标
    readonly property color badgeUnknown: "#6b7280"       // 未分类徽标
    readonly property color phaseCommissioning: "#f59e0b" // 调试中
    readonly property color phaseProduction: "#10b981"    // 生产中
    readonly property color phaseArchived: "#6b7280"      // 已归档
    readonly property color warning: "#f59e0b"
    readonly property color error: "#ef4444"

    // ── 间距 token（8px 网格系统）───────────────────────
    readonly property int spacingXs: 4
    readonly property int spacingSm: 8
    readonly property int spacingMd: 16
    readonly property int spacingLg: 24
    readonly property int spacingXl: 32

    // ── 排版 token ──────────────────────────────────────
    readonly property int fontSizeXs: 10
    readonly property int fontSizeSm: 12
    readonly property int fontSizeMd: 14
    readonly property int fontSizeLg: 16
    readonly property int fontSizeXl: 20
    readonly property int fontSizeXxl: 24

    // ── 圆角 token ──────────────────────────────────────
    readonly property int radiusSm: 4
    readonly property int radiusMd: 8
    readonly property int radiusLg: 12

    // ── 侧边栏宽度 ──────────────────────────────────────
    readonly property int sidebarWidth: 220
}
