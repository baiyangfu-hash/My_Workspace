"""
词典服务模块 - 封装离线 ECDICT 查询、模糊搜索与 CEFR 等级标注
"""
from cefr_tagger import CEFRTagger
from dictionary import Dictionary


class DictionaryService:
    def __init__(self):
        self.dict_engine = Dictionary()
        self.cefr_tagger = CEFRTagger()

    @staticmethod
    def sanitize_word(query):
        """入参清洗防御：去除首尾空白字符，若为空或非字符串则安全返回空字符串"""
        if not query or not isinstance(query, str):
            return ""
        return query.strip()

    def lookup(self, word):
        """精准查询单词信息，附带入参清洗防御与 CEFR 等级标注"""
        cleaned = self.sanitize_word(word)
        if not cleaned:
            return None
        result = self.dict_engine.lookup(cleaned)
        if result:
            if isinstance(result, dict):
                lvl = self.cefr_tagger.get_level(cleaned)
                result['cefr_level'] = lvl.upper() if lvl else None
            elif isinstance(result, list):
                for item in result:
                    if isinstance(item, dict) and 'word' in item:
                        lvl = self.cefr_tagger.get_level(item['word'])
                        item['cefr_level'] = lvl.upper() if lvl else None
        return result

    def query_word(self, query):
        """查询单词信息，附带入参清洗防御与 CEFR 标注"""
        cleaned = self.sanitize_word(query)
        if not cleaned:
            return None
        return self.lookup(cleaned)

    def search(self, prefix, limit=20):
        """前缀模糊搜索，附带入参清洗防御"""
        cleaned = self.sanitize_word(prefix)
        if not cleaned:
            return []
        results = self.dict_engine.search(cleaned)
        if limit is not None and isinstance(results, list):
            results = results[:limit]
        for item in results:
            if isinstance(item, dict) and 'word' in item:
                item['cefr_level'] = self.cefr_tagger.get_level(item['word'])
        return results

    def get_random_words(self, count=5, level=None):
        """获取随机单词列表"""
        words = self.dict_engine.get_random_words(count)
        for w in words:
            if isinstance(w, dict) and 'word' in w:
                w['cefr_level'] = self.cefr_tagger.get_level(w['word'])
        return words

    def close(self):
        self.dict_engine.close()
