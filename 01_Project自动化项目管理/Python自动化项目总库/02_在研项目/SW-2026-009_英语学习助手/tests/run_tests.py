"""
英语学习助手 - 全模块测试脚本
测试所有模块的导入、初始化、核心功能
"""
import sys
import os
import traceback

# 确保路径正确与 Windows 控制台 UTF-8 输出防护
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
if sys.platform == 'win32':
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        except Exception:
            pass
    if hasattr(sys.stderr, 'reconfigure'):
        try:
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
        except Exception:
            pass

class TestRunner:
    def __init__(self):
        self.results = []
        self.total = 0
        self.passed = 0
        self.failed = 0
    
    def test(self, name, func):
        """运行单个测试"""
        self.total += 1
        print(f"\n{'='*60}")
        print(f"测试 {self.total}: {name}")
        print(f"{'='*60}")
        try:
            func()
            self.passed += 1
            self.results.append(("PASS", name, ""))
            print(f"✅ 通过")
        except Exception as e:
            self.failed += 1
            error_msg = f"{type(e).__name__}: {str(e)}"
            self.results.append(("FAIL", name, error_msg))
            print(f"❌ 失败: {error_msg}")
            traceback.print_exc()
    
    def summary(self):
        """输出测试摘要"""
        print(f"\n\n{'='*60}")
        print(f"测试报告")
        print(f"{'='*60}")
        print(f"总计: {self.total} | 通过: {self.passed} | 失败: {self.failed}")
        print(f"通过率: {self.passed/max(self.total,1)*100:.1f}%")
        
        if self.failed > 0:
            print(f"\n失败列表:")
            for status, name, msg in self.results:
                if status == "FAIL":
                    print(f"  ❌ {name}: {msg}")
        
        return self.failed == 0


def test_imports(runner):
    """测试所有模块导入"""
    def _test():
        from dictionary import Dictionary
        from database import Database
        from dialogs_data import get_all_dialogs, get_dialog
        from fsrs_engine import FSRSEngine, FSRSState
        from us_travel_dialogs import get_all_us_dialogs, get_us_dialog
        from asr_engine import ASREngine
        from answer_matcher import AnswerMatcher, AnswerSpec, MatchResult
        from tts_engine import TTSEngine
        print("  核心模块导入成功")
        # GUI 模块在云端可能缺少 libEGL
        try:
            from dictation_page import DictationPage
            from roleplay_page import RolePlayPage
            print("  GUI 模块导入成功")
        except ImportError as e:
            print(f"  GUI 模块导入跳过（云端环境）: {e}")
    runner.test("模块导入", _test)


def test_dictionary(runner):
    """测试词典模块"""
    def _test():
        from dictionary import Dictionary
        d = Dictionary()
        
        # 精确查询
        result = d.lookup("hello")
        assert result is not None, "查询 hello 返回 None"
        assert isinstance(result, dict), "返回类型应为 dict"
        assert result.get('word', '').lower() == 'hello', f"单词不匹配: {result.get('word')}"
        print(f"  精确查询 hello: {result.get('translation', '')}")
        
        # 模糊搜索
        results = d.search("he")
        assert isinstance(results, list), "搜索返回类型应为 list"
        assert len(results) > 0, "搜索 he 应有结果"
        print(f"  模糊搜索 'he': 找到 {len(results)} 个结果")
        
        # 随机单词
        words = d.get_random_words(5)
        assert len(words) == 5, "应返回5个随机单词"
        print(f"  随机单词: {[w['word'] for w in words]}")
        
        # 查询不存在的词
        result = d.lookup("zzzzzzzzz")
        assert result is None or isinstance(result, list), "不存在词应返回 None 或列表"
        print(f"  不存在词查询: {result}")
        
        d.close()
    runner.test("词典模块 (dictionary.py)", _test)


def test_database(runner):
    """测试数据库模块"""
    def _test():
        from database import Database
        import tempfile
        import shutil
        
        # 使用临时数据库
        orig_path = None
        db_path = os.path.join(os.path.dirname(__file__), 'src', '..', 'data', 'app.db')
        if os.path.exists(db_path):
            orig_path = db_path + '.bak'
            shutil.copy2(db_path, orig_path)
        
        try:
            db = Database()
            
            # 清理测试数据
            db.cursor.execute("DELETE FROM user_words WHERE word = 'test_word_123'")
            db.cursor.execute("DELETE FROM study_records WHERE word = 'test_word_123'")
            db.conn.commit()
            
            # 测试 get_or_create_user_word
            word = db.get_or_create_user_word("test_word_123")
            assert word['word'] == 'test_word_123', f"单词不匹配: {word['word']}"
            assert word['status'] == 'new', "新词状态应为 new"
            print(f"  创建单词: {word}")
            
            # 重复创建应返回已有记录
            word2 = db.get_or_create_user_word("test_word_123")
            assert word2['word'] == 'test_word_123'
            print(f"  重复查询: {word2}")
            
            # 更新状态
            db.update_user_word("test_word_123", status='review')
            word3 = db.get_or_create_user_word("test_word_123")
            assert word3['status'] == 'review', f"状态未更新: {word3['status']}"
            print(f"  更新状态: {word3['status']}")
            
            # 添加学习记录
            db.add_study_record("test_word_123", "review", "good")
            print(f"  学习记录已添加")
            
            # 每日统计
            stats = db.get_daily_stats()
            print(f"  每日统计: {stats}")
            
            db.close()
        finally:
            if orig_path:
                shutil.copy2(orig_path, db_path)
                os.unlink(orig_path)
    runner.test("数据库模块 (database.py)", _test)


def test_fsrs(runner):
    """测试 FSRS 间隔重复算法"""
    def _test():
        from fsrs_engine import FSRSEngine, FSRSState
        
        engine = FSRSEngine()
        
        # 新词复习
        state = FSRSState()
        assert state.state == 0, "初始状态应为 0 (新词)"
        print(f"  初始状态: state={state.state}")
        
        # 评分 'good'
        new_state, due = engine.review(state, 'good')
        assert new_state.scheduled_days > 0, "复习间隔应大于0"
        print(f"  评分 good: 间隔={new_state.scheduled_days}天, 到期={due}")
        
        # 评分 'again'
        state2 = FSRSState()
        new_state2, due2 = engine.review(state2, 'again')
        assert new_state2.scheduled_days <= 1, "重来间隔应<=1天"
        print(f"  评分 again: 间隔={new_state2.scheduled_days}天")
        
        # 评分 'easy'
        state3 = FSRSState()
        new_state3, due3 = engine.review(state3, 'easy')
        assert new_state3.scheduled_days > new_state.scheduled_days, "简单间隔应大于一般"
        print(f"  评分 easy: 间隔={new_state3.scheduled_days}天")
        
        # JSON 序列化
        json_str = new_state.to_json()
        restored = FSRSState.from_json(json_str)
        assert restored.scheduled_days == new_state.scheduled_days, "序列化后状态不一致"
        print(f"  JSON 序列化: OK")
        
        # 获取各评分间隔
        intervals = engine.get_rating_intervals(state)
        assert 'again' in intervals, "应包含 again 间隔"
        assert 'easy' in intervals, "应包含 easy 间隔"
        print(f"  各评分间隔: {intervals}")
    runner.test("FSRS 算法 (fsrs_engine.py)", _test)


def test_answer_matcher(runner):
    """测试答案匹配引擎"""
    def _test():
        from answer_matcher import AnswerMatcher, AnswerSpec
        
        m = AnswerMatcher()
        
        # 测试1: 精确匹配
        spec = AnswerSpec(
            primary_answer="No, I don't. Do you have a table for two?",
            alternative_answers=["No I don't have one", "Nope, no reservation"],
            keywords=["no", "table", "two"]
        )
        
        r = m.match("No, I don't. Do you have a table for two?", spec)
        assert r.is_correct, "精确匹配应通过"
        assert r.score == 1.0, f"精确匹配分数应为1.0: {r.score}"
        print(f"  精确匹配: score={r.score}, feedback={r.feedback}")
        
        # 测试2: 替代答案
        r2 = m.match("No I don't have one", spec)
        assert r2.is_correct, "替代答案应通过"
        print(f"  替代答案: score={r2.score}, feedback={r2.feedback}")
        
        # 测试3: 关键词匹配（不完整但包含关键词）
        r3 = m.match("no table for two please", spec)
        assert r3.is_correct, "包含所有关键词应通过"
        print(f"  关键词匹配: score={r3.score}, feedback={r3.feedback}")
        
        # 测试4: 完全错误
        r4 = m.match("yes I have a reservation", spec)
        assert not r4.is_correct, "完全无关应失败"
        assert len(r4.missing_words) > 0, "应报告缺失关键词"
        print(f"  完全错误: score={r4.score}, missing={r4.missing_words}")
        
        # 测试5: 空输入
        r5 = m.match("", spec)
        assert not r5.is_correct, "空输入应失败"
        print(f"  空输入: score={r5.score}")
        
        # 测试6: 大小写不敏感
        r6 = m.match("NO TABLE FOR TWO", spec)
        assert r6.is_correct, "大小写不敏感应通过"
        print(f"  大小写不敏感: score={r6.score}")
        
        # 测试7: 标点不影响
        r7 = m.match("No, I don't! Table for two?", spec)
        assert r7.is_correct, "标点不应影响匹配"
        print(f"  标点不影响: score={r7.score}")
    runner.test("答案匹配引擎 (answer_matcher.py)", _test)


def test_dialogs_data(runner):
    """测试对话数据"""
    def _test():
        from dialogs_data import get_all_dialogs, get_dialog
        
        dialogs = get_all_dialogs()
        assert len(dialogs) > 0, "应有基础对话"
        print(f"  基础对话数: {len(dialogs)}")
        
        for d in dialogs:
            assert 'id' in d, f"缺少 id: {d}"
            assert 'title' in d, f"缺少 title: {d}"
            assert 'line_count' in d, f"缺少 line_count: {d}"
        
        # 获取单个对话
        dialog = get_dialog(dialogs[0]['id'])
        assert dialog is not None, "应能获取对话详情"
        assert 'lines' in dialog, "对话应有 lines"
        assert len(dialog['lines']) > 0, "对话应至少有一行"
        
        line = dialog['lines'][0]
        assert 'speaker' in line, f"缺少 speaker: {line}"
        assert 'text' in line, f"缺少 text: {line}"
        assert 'translation' in line, f"缺少 translation: {line}"
        print(f"  对话 '{dialogs[0]['title']}': {len(dialog['lines'])} 行")
    runner.test("基础对话数据 (dialogs_data.py)", _test)


def test_us_travel_dialogs(runner):
    """测试美国出差对话数据"""
    def _test():
        from us_travel_dialogs import get_all_us_dialogs, get_us_dialog
        
        dialogs = get_all_us_dialogs()
        assert len(dialogs) == 22, f"应有22个美国出差对话，实际: {len(dialogs)}"
        print(f"  美国出差对话数: {len(dialogs)}")
        
        # 检查分类
        categories = {}
        for d in dialogs:
            cat = d['category']
            categories[cat] = categories.get(cat, 0) + 1
        
        expected_cats = {'超市购物', '交通出行', '问路', '日常交流', '美国特有'}
        for cat in expected_cats:
            assert cat in categories, f"缺少分类: {cat}"
        print(f"  分类统计: {categories}")
        
        # 检查每个对话结构
        for d in dialogs:
            dialog = get_us_dialog(d['id'])
            assert dialog is not None, f"无法获取对话: {d['id']}"
            for line in dialog['lines']:
                assert 'speaker' in line
                assert 'text' in line
                assert 'translation' in line
                assert 'highlight_words' in line
        print(f"  所有对话结构验证通过")
        
        # 检查海关对话
        customs = get_us_dialog('customs_entry')
        assert customs is not None, "应包含海关对话"
        print(f"  海关对话: {len(customs['lines'])} 行")
    runner.test("美国出差对话 (us_travel_dialogs.py)", _test)


def test_tts_engine(runner):
    """测试 TTS 引擎"""
    def _test():
        from tts_engine import TTSEngine
        
        tts = TTSEngine()
        status = tts.get_status()
        print(f"  TTS 状态: {status}")
        # 不实际播放，只检查初始化
        print(f"  TTS 可用: {tts.available}")
    runner.test("TTS 引擎 (tts_engine.py)", _test)


def test_asr_engine(runner):
    """测试 ASR 引擎"""
    def _test():
        from asr_engine import ASREngine
        
        asr = ASREngine()
        status = asr.get_status()
        print(f"  ASR 状态: {status}")
        print(f"  ASR 可用: {asr.available}")
        
        # 文本模式测试
        result = asr.recognize_from_text("hello world")
        assert result == "hello world", f"文本模式返回不正确: {result}"
        print(f"  文本模式: OK")
    runner.test("ASR 引擎 (asr_engine.py)", _test)


def test_cefr_tagger(runner):
    """测试 CEFR 标注模块"""
    def _test():
        from cefr_tagger import CEFRTagger, CEFR_LEVELS, CEFRPY_AVAILABLE
        
        print(f"  cefrpy 可用: {CEFRPY_AVAILABLE}")
        assert len(CEFR_LEVELS) == 6, "应有6个CEFR等级"
        assert 'A1' in CEFR_LEVELS
        assert 'C2' in CEFR_LEVELS
        print(f"  CEFR 等级: {list(CEFR_LEVELS.keys())}")
        
        # 测试标注器
        tagger = CEFRTagger()
        if tagger.available:
            # 测试查询
            level = str(tagger.get_level('breakfast'))
            assert level == 'A1', f"breakfast 应为 A1, 得到: {level}"
            print(f"  breakfast: {level}")
            
            level2 = str(tagger.get_level('reservation'))
            assert level2 == 'B1', f"reservation 应为 B1, 得到: {level2}"
            print(f"  reservation: {level2}")
            
            # 测试不在数据库中的词
            level3 = tagger.get_level('xyzasdfqwer')
            assert level3 is None, "不存在的词应返回 None"
            print(f"  不存在词: {level3}")
            
            # 测试 is_known
            assert tagger.is_known('hello') is False, "hello 不在 cefrpy 数据库"
            assert tagger.is_known('breakfast') is True
            print(f"  is_known: OK")
        else:
            print(f"  cefrpy 未安装，跳过标注测试")
    runner.test("CEFR 标注 (cefr_tagger.py)", _test)


def test_grammar_engine(runner):
    """测试语法课程引擎"""
    def _test():
        from grammar_engine import GrammarEngine, GRAMMAR_POINTS
        
        # 验证数据
        assert len(GRAMMAR_POINTS['A1']) == 34, f"A1 应有34个语法点，实际: {len(GRAMMAR_POINTS['A1'])}"
        assert len(GRAMMAR_POINTS['A2']) == 37, f"A2 应有37个语法点"
        assert len(GRAMMAR_POINTS['B1']) == 42, f"B1 应有42个语法点"
        print(f"  语法点总数: A1={len(GRAMMAR_POINTS['A1'])}, A2={len(GRAMMAR_POINTS['A2'])}, B1={len(GRAMMAR_POINTS['B1'])}")
        
        # 测试引擎
        engine = GrammarEngine()
        levels = engine.get_all_levels()
        assert len(levels) >= 3, f"应有至少3个等级，实际: {len(levels)}"
        print(f"  等级: {[l['level'] for l in levels]}")
        
        # 获取 A1 语法点
        a1_points = engine.get_points_by_level('A1')
        assert len(a1_points) == 34, f"A1 应有34个语法点，实际: {len(a1_points)}"
        assert 'name' in a1_points[0]
        assert 'examples' in a1_points[0]
        assert isinstance(a1_points[0]['examples'], list)
        print(f"  A1 第一个语法点: {a1_points[0]['name']}")
        print(f"  A1 例句: {a1_points[0]['examples'][:2]}")
        
        # 获取分类
        categories = engine.get_categories_by_level('A1')
        assert len(categories) > 0, "A1 应有语法分类"
        print(f"  A1 分类数: {len(categories)}")
        print(f"  第一个分类: {categories[0]['name']} ({categories[0]['count']}个)")
        
        # 按 ID 获取
        point = engine.get_point_by_id(1)
        assert point is not None, "应能获取语法点"
        assert point['name'] == a1_points[0]['name']
        print(f"  按ID获取: {point['name']}")
    runner.test("语法课程引擎 (grammar_engine.py)", _test)


def test_course_manager(runner):
    """测试课程管理模块"""
    def _test():
        from course_manager import CourseManager, init_course_system
        
        mgr = CourseManager()
        
        # 测试等级信息
        levels = mgr.get_levels()
        assert len(levels) == 6, f"应有6个CEFR等级，实际: {len(levels)}"
        print(f"  CEFR 等级: {[l['level'] for l in levels]}")
        
        # 测试用户进度
        progress = mgr.get_user_progress()
        assert 'current_level' in progress
        assert progress['current_level'] == 'A1'
        assert progress['target_level'] == 'B1'
        print(f"  当前等级: {progress['current_level']} → {progress['target_level']}")
        print(f"  词汇进度: {progress['vocab_mastered']}/{progress['vocab_target']} ({progress['vocab_percent']}%)")
        
        # 测试每日计划
        plan = mgr.get_daily_plan()
        assert 'tasks' in plan
        assert len(plan['tasks']) == 5, f"应有5个每日任务，实际: {len(plan['tasks'])}"
        print(f"  每日计划: {len(plan['tasks'])} 个任务, 预计 {plan['estimated_minutes']} 分钟")
        for task in plan['tasks']:
            print(f"    - {task['icon']} {task['title']}: {task['target']}")
        
        # 测试学习路线图
        roadmap = mgr.get_6month_roadmap()
        assert 'phase1' in roadmap
        assert 'phase2' in roadmap
        assert len(roadmap['phase1']['months_detail']) == 3
        assert len(roadmap['phase2']['months_detail']) == 3
        print(f"  学习路线图: 2个阶段, 6个月")
        
        # 测试词汇统计
        vocab_stats = mgr.get_vocab_stats_by_level()
        print(f"  词汇统计: {vocab_stats}")
        
        # 测试更新进度
        mgr.update_study_progress(vocab_count=5, grammar_count=1)
        progress2 = mgr.get_user_progress()
        assert progress2['vocab_mastered'] >= 5, f"词汇进度应更新"
        print(f"  更新后进度: vocab={progress2['vocab_mastered']}, grammar={progress2['grammar_completed']}")
    runner.test("课程管理 (course_manager.py)", _test)


def test_main_import(runner):
    """测试主程序与 QML Bridge 模块导入"""
    def _test():
        try:
            import PySide6.QtWidgets
            import PySide6.QtCore
            import PySide6.QtGui
            from ui.qml_bridge import QmlBridge
            import main
            print(f"  PySide6 版本: {PySide6.__version__}")
            print(f"  QML Bridge 模块: OK")
            print(f"  主程序 main.py 模块: OK")
        except ImportError as e:
            print(f"  导入失败: {e}")
            raise e
    runner.test("主程序与 QML Bridge 导入", _test)


def test_services_layer(runner):
    """测试重构后的服务层 (Service Layer)"""
    def _test():
        from services import (
            DatabaseManager, get_db,
            StudyService, DictionaryService, GrammarService, CourseService
        )
        db = get_db()
        study_svc = StudyService(db)
        dict_svc = DictionaryService()
        grammar_svc = GrammarService()
        course_svc = CourseService(db)

        # 验证 DictionaryService
        res = dict_svc.lookup("apple")
        assert res is not None and res.get('cefr_level') == 'A1', "DictionaryService 查询异常"
        print("  DictionaryService 校验 OK")

        # 验证 StudyService
        word = study_svc.get_or_create_word("svc_test_word")
        assert word['word'] == 'svc_test_word', "StudyService 创建单词异常"
        rev = study_svc.record_review("svc_test_word", "good", study_minutes=3)
        assert rev['status'] == 'review', "StudyService 记录复习异常"
        print("  StudyService 校验 OK")

        # 验证 GrammarService
        pts = grammar_svc.get_points_by_level("A1")
        assert len(pts) > 0, "GrammarService 语法点获取失败"
        exs = grammar_svc.generate_practice(pts[0])
        assert isinstance(exs, list), "GrammarService 练习生成失败"
        print("  GrammarService 校验 OK")

        # 验证 CourseService
        prog = course_svc.get_user_progress()
        assert 'current_level' in prog, "CourseService 获取进度失败"
        print("  CourseService 校验 OK")

        dict_svc.close()
    runner.test("服务层架构 (services/)", _test)


def test_gui_switching_module(runner):
    """测试 QML 界面动态切换与场景流转"""
    def _test():
        from test_gui_switching import test_qml_bridge_and_switching
        test_qml_bridge_and_switching()
    runner.test("QML 界面动态切换与场景流转", _test)


if __name__ == '__main__':
    runner = TestRunner()

    print("=" * 60)
    print("英语学习助手 - 全模块测试")
    print("=" * 60)

    test_imports(runner)
    test_services_layer(runner)
    test_dictionary(runner)
    test_database(runner)
    test_fsrs(runner)
    test_answer_matcher(runner)
    test_dialogs_data(runner)
    test_us_travel_dialogs(runner)
    test_tts_engine(runner)
    test_asr_engine(runner)
    test_cefr_tagger(runner)
    test_grammar_engine(runner)
    test_course_manager(runner)
    test_main_import(runner)
    test_gui_switching_module(runner)

    success = runner.summary()
    report_path = os.path.join(os.path.dirname(__file__), 'data', 'test_report.txt')
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(f"英语学习助手 - 测试报告\n")
        f.write(f"时间: {__import__('datetime').datetime.now().isoformat()}\n")
        f.write(f"总计: {runner.total} | 通过: {runner.passed} | 失败: {runner.failed}\n")
        f.write(f"通过率: {runner.passed/max(runner.total,1)*100:.1f}%\n\n")
        for status, name, msg in runner.results:
            icon = "✅" if status == "PASS" else "❌"
            f.write(f"{icon} {name}")
            if msg:
                f.write(f" - {msg}")
            f.write("\n")
    
    print(f"\n测试报告已保存: {report_path}")
    
    sys.exit(0 if success else 1)

