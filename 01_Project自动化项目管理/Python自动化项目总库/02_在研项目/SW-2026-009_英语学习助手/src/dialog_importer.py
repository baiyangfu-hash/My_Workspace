"""
自定义对话导入模块
支持 JSON 和 TXT 两种格式的情景对话导入
"""

import json
import re
import string


class ImportError(Exception):
    """对话导入异常"""
    pass


class DialogImporter:
    """对话导入器"""

    # 英文停用词表
    STOP_WORDS = {
        'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you',
        'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his',
        'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself',
        'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which',
        'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are',
        'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having',
        'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if',
        'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for',
        'with', 'about', 'against', 'between', 'through', 'during', 'before',
        'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out',
        'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once',
        'here', 'there', 'when', 'where', 'why', 'how', 'all', 'both',
        'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor',
        'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't',
        'can', 'will', 'just', 'don', 'should', 'now', 'd', 'll', 'm', 'o',
        're', 've', 'y', 'ain', 'aren', 'couldn', 'didn', 'doesn', 'hadn',
        'hasn', 'haven', 'isn', 'ma', 'mightn', 'mustn', 'needn', 'shan',
        'shouldn', 'wasn', 'weren', 'won', 'wouldn', 'also', 'would', 'could',
        'let', 'may', 'much', 'many', 'well', 'please', 'yes', 'okay',
        'ok', 'thank', 'thanks', 'sorry', 'excuse', 'hello', 'hi', 'hey',
        'good', 'great', 'fine', 'nice', 'right', 'sure', 'think', 'know',
        'want', 'like', 'come', 'go', 'get', 'got', 'make', 'take', 'see',
        'say', 'said', 'tell', 'told', 'give', 'gave', 'look', 'need',
        'use', 'find', 'way', 'day', 'time', 'thing', 'things', 'really',
    }

    def __init__(self):
        pass

    def import_file(self, filepath: str) -> dict:
        """
        导入对话文件
        返回: dict（符合 dialogs_data.py 的对话格式）
        或抛出 ImportError 异常
        """
        if not filepath or not isinstance(filepath, str):
            raise ImportError("文件路径无效")

        if filepath.lower().endswith('.json'):
            dialog = self.import_json(filepath)
        elif filepath.lower().endswith('.txt'):
            dialog = self.import_txt(filepath)
        else:
            raise ImportError("不支持的文件格式，请使用 .json 或 .txt 文件")

        # 验证数据
        errors = self.validate(dialog)
        if errors:
            raise ImportError("数据验证失败: " + "; ".join(errors))

        return dialog

    def import_json(self, filepath: str) -> dict:
        """导入 JSON 格式"""
        try:
            with open(filepath, encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise ImportError(f"JSON 解析失败: {e}")
        except FileNotFoundError:
            raise ImportError("文件不存在")
        except Exception as e:
            raise ImportError(f"读取文件失败: {e}")

        # 确保必要字段存在
        if 'lines' not in data:
            raise ImportError("JSON 缺少 'lines' 字段")

        dialog = {
            'title': data.get('title', '未命名对话'),
            'title_en': data.get('title_en', 'Untitled'),
            'category': data.get('category', '自定义'),
            'difficulty': data.get('difficulty', '中级'),
            'lines': [],
        }

        for line in data['lines']:
            if 'text' not in line:
                raise ImportError("对话行缺少 'text' 字段")
            dialog['lines'].append({
                'speaker': line.get('speaker', 'Unknown'),
                'text': line['text'],
                'translation': line.get('translation', ''),
                'highlight_words': line.get('highlight_words', []),
            })

        return dialog

    def import_txt(self, filepath: str) -> dict:
        """导入 TXT 格式"""
        try:
            with open(filepath, encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            raise ImportError("文件不存在")
        except Exception as e:
            raise ImportError(f"读取文件失败: {e}")

        lines = content.strip().split('\n')

        # 解析元数据
        metadata = {
            'title': '未命名对话',
            'title_en': 'Untitled',
            'category': '自定义',
            'difficulty': '中级',
        }
        content_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('#'):
                # 解析元数据: # key: value
                meta_match = re.match(r'^#\s*(\w+)\s*:\s*(.+)$', stripped)
                if meta_match:
                    key = meta_match.group(1).strip()
                    value = meta_match.group(2).strip()
                    if key in metadata:
                        metadata[key] = value
            elif stripped:
                content_lines.append(stripped)

        # 解析对话行
        dialog_lines = []
        i = 0
        while i < len(content_lines):
            line = content_lines[i]

            # 匹配 Speaker: English text
            speaker_match = re.match(r'^(.+?)\s*:\s*(.+)$', line)
            if speaker_match:
                speaker = speaker_match.group(1).strip()
                text = speaker_match.group(2).strip()

                # 下一行应该是中文翻译
                translation = ''
                if i + 1 < len(content_lines):
                    next_line = content_lines[i + 1]
                    # 如果下一行不是新的对话行（不含冒号分隔的speaker模式），则视为翻译
                    next_speaker_match = re.match(r'^(.+?)\s*:\s*(.+)$', next_line)
                    if not next_speaker_match:
                        translation = next_line
                        i += 1

                dialog_lines.append({
                    'speaker': speaker,
                    'text': text,
                    'translation': translation,
                    'highlight_words': self._extract_keywords(text),
                })

            i += 1

        if not dialog_lines:
            raise ImportError("未找到有效的对话内容")

        return {
            'title': metadata['title'],
            'title_en': metadata['title_en'],
            'category': metadata['category'],
            'difficulty': metadata['difficulty'],
            'lines': dialog_lines,
        }

    def validate(self, dialog: dict) -> list:
        """
        验证对话数据完整性
        返回: 错误列表（空列表表示验证通过）
        """
        errors = []

        if not isinstance(dialog, dict):
            errors.append("对话数据必须是字典类型")
            return errors

        # 检查必要字段
        required_fields = ['title', 'title_en', 'category', 'difficulty', 'lines']
        for field in required_fields:
            if field not in dialog:
                errors.append(f"缺少必要字段: {field}")

        # 检查对话行
        if 'lines' in dialog:
            if not isinstance(dialog['lines'], list):
                errors.append("'lines' 必须是列表类型")
            elif len(dialog['lines']) == 0:
                errors.append("对话内容不能为空")
            else:
                for idx, line in enumerate(dialog['lines']):
                    if not isinstance(line, dict):
                        errors.append(f"第 {idx + 1} 行: 对话行必须是字典类型")
                        continue
                    if 'text' not in line or not line['text'].strip():
                        errors.append(f"第 {idx + 1} 行: 缺少英文文本")
                    if 'speaker' not in line or not line['speaker'].strip():
                        errors.append(f"第 {idx + 1} 行: 缺少说话人")

        return errors

    def _extract_keywords(self, text: str) -> list:
        """从英文文本中提取关键词（过滤停用词和标点）"""
        # 移除标点，转小写
        cleaned = text.lower().translate(
            str.maketrans('', '', string.punctuation)
        )
        words = cleaned.split()

        # 过滤停用词和过短的词
        keywords = []
        for word in words:
            if (len(word) > 2
                    and word not in self.STOP_WORDS
                    and word not in keywords):
                keywords.append(word)

        return keywords
