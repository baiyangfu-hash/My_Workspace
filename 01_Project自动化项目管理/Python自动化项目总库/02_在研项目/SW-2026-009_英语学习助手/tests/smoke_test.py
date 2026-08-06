"""
SW-2026-009 英语学习助手 - 自动化冒烟测试 (Smoke Test)
包含核心导入、QML UI 加载、场景切换、FSRS 背词卡片、离线词典、CEFR 语法、答案匹配及 TTS 发音全链路
"""
import sys
import os
import json

# 确保 src 目录在 sys.path
SRC_DIR = os.path.join(os.path.dirname(__file__), '..', 'src')
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

if sys.platform == 'win32':
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        except Exception:
            pass


def run_smoke_tests():
    print("=" * 70)
    print("🔥 SW-2026-009 英语学习助手 - 全系统冒烟测试 (Smoke Test) 🔥")
    print("=" * 70)

    passed_count = 0
    total_count = 0

    def smoke_check(name, fn):
        nonlocal passed_count, total_count
        total_count += 1
        print(f"\n[冒烟测试 {total_count}] {name} ... ", end="")
        try:
            fn()
            print("🟢 PASSED")
            passed_count += 1
        except Exception as e:
            print(f"🔴 FAILED: {e}")

    # 1. 核心模块与桥接层导入
    def _test_import():
        from ui.qml_bridge import QmlBridge
        from services import DatabaseManager, StudyService, DictionaryService, GrammarService, CourseService
        from us_travel_dialogs import DIALOGS
        from tts_engine import TTSEngine
        assert len(DIALOGS) >= 20, "美国出差对话词典缺失"
    smoke_check("核心模块与 QML Bridge 导入", _test_import)

    # 2. QML 主窗口与 6 大视图初始化
    def _test_qml_engine():
        from PySide6.QtGui import QGuiApplication
        from PySide6.QtQml import QQmlApplicationEngine
        from PySide6.QtCore import QUrl
        from ui.qml_bridge import QmlBridge

        app = QGuiApplication.instance() or QGuiApplication(sys.argv)
        bridge = QmlBridge()
        engine = QQmlApplicationEngine()
        qml_dir = os.path.join(SRC_DIR, 'ui', 'qml')
        engine.addImportPath(qml_dir)
        engine.rootContext().setContextProperty("qmlBridge", bridge)

        main_qml = os.path.join(qml_dir, 'main.qml')
        engine.load(QUrl.fromLocalFile(main_qml))
        root_objs = engine.rootObjects()
        assert len(root_objs) > 0, "QML 根窗口创建失败"
    smoke_check("QML 主窗口及 6 大视图 UI 加载", _test_qml_engine)

    # 3. 出差情景对话 27+ 动态切换与数据检索
    def _test_scenarios():
        from ui.qml_bridge import QmlBridge
        bridge = QmlBridge()
        scenarios_json = bridge.getScenariosJson()
        scenarios = json.loads(scenarios_json)
        assert len(scenarios) >= 25, f"场景数不足，实际: {len(scenarios)}"

        detail_json = bridge.getScenarioDetailJson(scenarios[0]["id"])
        detail = json.loads(detail_json)
        assert "lines" in detail or "dialogue" in detail, "场景详情缺失对话内容"
    smoke_check("27+ 实战场景动态列表与详情检索", _test_scenarios)

    # 4. FSRS 抽词、背词卡片翻转数据与评分持久化
    def _test_vocab_fsrs():
        from ui.qml_bridge import QmlBridge
        bridge = QmlBridge()
        card_json = bridge.getRandomVocabCardJson()
        card_data = json.loads(card_json)
        assert "word" in card_data and "translation" in card_data, "背词卡片数据不完整"

        word = card_data["word"]
        res_json = bridge.recordReviewJson(word, "good", 2)
        res = json.loads(res_json)
        assert res.get("word") == word, "FSRS 复习记录更新失败"
    smoke_check("FSRS 算法抽词与背词卡片记录持久化", _test_vocab_fsrs)

    # 5. ECDICT 离线词典精准查询与 CEFR 标注
    def _test_dictionary():
        from ui.qml_bridge import QmlBridge
        bridge = QmlBridge()
        word_json = bridge.lookupWordJson("airport")
        data = json.loads(word_json)
        assert data.get("word") == "airport", "词典查询词条不匹配"
    smoke_check("ECDICT 离线词典检索与 CEFR 标注", _test_dictionary)

    # 6. CEFR 语法课程知识点获取
    def _test_grammar():
        from ui.qml_bridge import QmlBridge
        bridge = QmlBridge()
        pts_json = bridge.getGrammarPointsJson("A1")
        pts = json.loads(pts_json)
        assert len(pts) > 0, "A1 语法知识点获取为空"
    smoke_check("CEFR 语法课程知识点获取", _test_grammar)

    # 7. 答案匹配器与智能判定
    def _test_matcher():
        from answer_matcher import AnswerMatcher, AnswerSpec
        matcher = AnswerMatcher()
        spec = AnswerSpec(primary_answer="Where is the subway station?", keywords=["subway", "station"])
        res = matcher.match("Where is the subway station?", spec)
        assert res.score >= 0.9, "答案匹配评级异常"
    smoke_check("听写答案匹配与模糊判定引擎", _test_matcher)

    # 8. TTS 语音引擎初始化
    def _test_tts():
        from tts_engine import TTSEngine
        tts = TTSEngine()
        assert tts.available, "TTS 引擎不可用"
    smoke_check("Windows SAPI5 TTS 离线语音引擎", _test_tts)

    print("\n" + "=" * 70)
    print(f"冒烟测试结果: 总计 {total_count} 项 | 通过 {passed_count} 项 | 失败 {total_count - passed_count} 项")
    print(f"冒烟测试通过率: {passed_count / max(total_count, 1) * 100:.1f}%")
    print("=" * 70)
    return passed_count == total_count


if __name__ == '__main__':
    success = run_smoke_tests()
    sys.exit(0 if success else 1)
