"""
答案匹配引擎
支持多标准答案 + 关键词匹配 + 模糊匹配
接口简洁：match(user_input, expected) → MatchResult
"""
import re
from dataclasses import dataclass, field


@dataclass
class MatchResult:
    """匹配结果"""
    is_correct: bool          # 是否通过
    score: float              # 匹配分数 0.0~1.0
    best_answer: str          # 最匹配的标准答案
    diff_html: str            # 差异对比 HTML（绿色正确/红色缺失/橙色多余）
    missing_words: list[str]  # 缺少的关键词
    extra_words: list[str]    # 多余的词
    feedback: str             # 反馈文本


class AnswerMatcher:
    """答案匹配引擎"""

    def __init__(self):
        pass

    def match(self, user_input: str, expected: "AnswerSpec") -> MatchResult:
        """
        匹配用户输入与期望答案
        
        user_input: 用户输入的文本
        expected: AnswerSpec 对象，包含标准答案和关键词
        
        返回: MatchResult
        """
        if not user_input or not user_input.strip():
            return MatchResult(
                is_correct=False,
                score=0.0,
                best_answer=expected.primary_answer,
                diff_html="",
                missing_words=expected.keywords[:],
                extra_words=[],
                feedback="请输入你的回答"
            )

        user_clean = self._normalize(user_input)

        # 策略1：精确匹配任一标准答案
        for ans in expected.all_answers:
            ans_clean = self._normalize(ans)
            if user_clean == ans_clean:
                return MatchResult(
                    is_correct=True,
                    score=1.0,
                    best_answer=ans,
                    diff_html=self._green_text(ans),
                    missing_words=[],
                    extra_words=[],
                    feedback="✅ 完美！"
                )

        # 策略2：关键词检查
        user_words = set(re.findall(r'\b\w+\b', user_clean))
        required_words = set(w.lower() for w in expected.keywords)

        matched_keywords = user_words & required_words
        missing_keywords = required_words - user_words
        extra_words = user_words - required_words - self._get_common_words()

        keyword_score = len(matched_keywords) / max(len(required_words), 1)

        # 策略3：与最佳答案的词重叠度
        best_overlap = 0.0
        best_answer = expected.primary_answer
        for ans in expected.all_answers:
            ans_words = set(re.findall(r'\b\w+\b', self._normalize(ans)))
            if not ans_words:
                continue
            overlap = len(user_words & ans_words) / max(len(ans_words), 1)
            if overlap > best_overlap:
                best_overlap = overlap
                best_answer = ans

        # 综合评分
        score = max(keyword_score, best_overlap)

        # 生成差异对比
        diff_html = self._generate_diff(user_input, best_answer)

        # 判定
        is_correct = score >= 0.7  # 70%以上算通过

        # 反馈
        if is_correct:
            if missing_keywords:
                feedback = f"✅ 不错！可以更完整，试试加入: {', '.join(missing_keywords)}"
            else:
                feedback = "✅ 很好！"
        else:
            if missing_keywords:
                feedback = f"❌ 缺少关键信息: {', '.join(missing_keywords)}"
            else:
                feedback = f"❌ 再试试看，参考答案: {best_answer}"

        return MatchResult(
            is_correct=is_correct,
            score=score,
            best_answer=best_answer,
            diff_html=diff_html,
            missing_words=list(missing_keywords),
            extra_words=list(extra_words),
            feedback=feedback
        )

    def _normalize(self, text: str) -> str:
        """标准化文本：小写 + 去标点 + 去多余空格"""
        text = text.lower().strip()
        text = re.sub(r"[^\w\s']", "", text)
        text = re.sub(r'\s+', ' ', text)
        return text

    def _get_common_words(self) -> set:
        """获取常见停用词"""
        return {
            'i', 'me', 'my', 'you', 'your', 'he', 'she', 'it', 'we', 'they',
            'a', 'an', 'the', 'is', 'am', 'are', 'was', 'were', 'be', 'been',
            'do', 'does', 'did', 'have', 'has', 'had', 'can', 'could', 'will',
            'would', 'should', 'may', 'might', 'shall', 'to', 'of', 'in',
            'for', 'on', 'at', 'with', 'from', 'by', 'about', 'and', 'or',
            'but', 'not', 'no', 'so', 'if', 'that', 'this', 'please',
            'yes', 'here', 'there', 'what', 'how', 'when', 'where', 'who',
            'like', 'want', 'need', 'get', 'got',
        }

    def _green_text(self, text: str) -> str:
        """生成全绿文本"""
        return f'<span style="color:#27ae60;">{text}</span>'

    def _generate_diff(self, user_input: str, correct_answer: str) -> str:
        """生成差异对比 HTML"""
        user_words = re.findall(r'\b\w+\b', user_input.lower())
        correct_words = re.findall(r'\b\w+\b', correct_answer.lower())

        result = []
        correct_set = set(correct_words)
        used = set()

        for word in correct_words:
            if word in user_words and word not in used:
                result.append(f'<span style="color:#27ae60;">{word}</span>')
                used.add(word)
            else:
                result.append(f'<span style="color:#dc2626;font-weight:bold;">{word}</span>')

        return " ".join(result)


@dataclass
class AnswerSpec:
    """答案规格"""
    primary_answer: str                    # 主标准答案
    alternative_answers: list[str] = field(default_factory=list)  # 可接受的替代答案
    keywords: list[str] = field(default_factory=list)            # 必须包含的关键词

    @property
    def all_answers(self) -> list[str]:
        """所有可接受答案"""
        return [self.primary_answer] + self.alternative_answers
