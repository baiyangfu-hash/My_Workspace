"""tests/qml — V0.6.0 QML PoC 测试套件

测试范围：
- ProjectListModel（QAbstractListModel）数据正确性
- QmlBridge（QObject）slot/property 行为
- QML 文件加载与基础渲染（Week 2+ 补充）

约束：
- qapp fixture 单一定位 tests/conftest.py（session 级 QApplication）
- 不在本目录重新定义 qapp，直接通过 `def test_xxx(qapp):` 引用
- GUI 测试默认可见模式，不禁用 offscreen
"""
