"""
词典服务模块 - 封装离线 ECDICT 查询、模糊搜索与 CEFR 等级标注
"""
from cefr_tagger import CEFRTagger
from dictionary import Dictionary


class DictionaryService:
    def __init__(self):
        self.dict_engine = Dictionary()
        self.cefr_tagger = CEFRTagger()

    def lookup(self, word):
        """精准查询单词信息，附带 CEFR 等级标注"""
        result = self.dict_engine.lookup(word)
        if result:
            lvl = self.cefr_tagger.get_level(word)
            result['cefr_level'] = lvl.upper() if lvl else None
        return result

    def search(self, prefix, limit=20):
        """前缀模糊搜索"""
        results = self.dict_engine.search(prefix, limit)
        for item in results:
            if 'word' in item:
                item['cefr_level'] = self.cefr_tagger.get_level(item['word'])
        return results

    def get_random_words(self, count=5, level=None):
        """获取随机单词列表"""
        words = self.dict_engine.get_random_words(count)
        for w in words:
            w['cefr_level'] = self.cefr_tagger.get_level(w['word'])
        return words

    def close(self):
        self.dict_engine.close()
