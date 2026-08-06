"""
ASR 引擎模块 - 语音识别
基于 Vosk 离线语音识别，支持录音和实时识别
接口简洁：init() → listen() → result
"""
import json
import os
import queue
import threading


class ASREngine:
    """离线语音识别引擎"""

    def __init__(self, model_path=None):
        """
        初始化 ASR 引擎
        model_path: Vosk 模型目录路径，为 None 时自动检测
        """
        self.available = False
        self.model = None
        self.recognizer = None
        self._audio_queue = queue.Queue()
        self._is_listening = False
        self._result_callback = None

        if model_path:
            self._load_model(model_path)
        else:
            self._auto_detect_model()

    def _auto_detect_model(self):
        """自动检测 Vosk 模型"""
        # 查找模型目录
        possible_paths = [
            os.path.join(os.path.dirname(__file__), '..', 'models', 'vosk-model-en-us'),
            os.path.join(os.path.dirname(__file__), '..', 'models', 'vosk-model-small-en-us'),
            'vosk-model-en-us',
            'vosk-model-small-en-us',
        ]

        for path in possible_paths:
            if os.path.exists(path):
                self._load_model(path)
                return

        # 尝试导入 vosk
        try:
            import vosk
            self._vosk_available = True
        except ImportError:
            self._vosk_available = False

    def _load_model(self, model_path):
        """加载 Vosk 模型"""
        try:
            import vosk
            self.model = vosk.Model(model_path)
            self.recognizer = None  # 延迟创建
            self.available = True
        except ImportError:
            self.available = False
        except Exception as e:
            print(f"加载 Vosk 模型失败: {e}")
            self.available = False

    def _create_recognizer(self, sample_rate=16000):
        """创建识别器"""
        if self.model and self.available:
            import vosk
            self.recognizer = vosk.KaldiRecognizer(self.model, sample_rate)
            self.recognizer.SetWords(True)

    def listen(self, callback=None, duration=10):
        """
        开始录音并识别
        callback: 识别完成后的回调，参数为 (text, confidence)
        duration: 最大录音时长（秒）
        返回: None（异步，结果通过 callback 返回）
        """
        if not self.available:
            if callback:
                callback("", 0.0, "ASR 不可用")
            return

        self._result_callback = callback
        self._is_listening = True

        thread = threading.Thread(target=self._record_and_recognize, args=(duration,))
        thread.daemon = True
        thread.start()

    def _record_and_recognize(self, duration):
        """录音并识别（在子线程中运行）"""
        try:
            import pyaudio

            self._create_recognizer(sample_rate=16000)

            stream = pyaudio.PyAudio().open(
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                frames_per_buffer=4000
            )

            stream.start_stream()

            all_data = b''
            for _ in range(int(16000 * duration / 4000)):
                if not self._is_listening:
                    break
                data = stream.read(4000, exception_on_overflow=False)
                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    text = result.get('text', '')
                    if text and self._result_callback:
                        self._result_callback(text, 0.0)

            stream.stop_stream()
            stream.close()

            # 获取最终结果
            final = json.loads(self.recognizer.FinalResult())
            text = final.get('text', '')

            self._is_listening = False
            if self._result_callback:
                self._result_callback(text, 0.0)

        except ImportError:
            self._is_listening = False
            if self._result_callback:
                self._result_callback("", 0.0, "pyaudio 未安装")
        except Exception as e:
            self._is_listening = False
            if self._result_callback:
                self._result_callback("", 0.0, str(e))

    def stop(self):
        """停止录音"""
        self._is_listening = False

    def recognize_from_text(self, text):
        """
        文本模式（无语音时使用）
        直接返回输入文本，供统一接口调用
        """
        return text.strip()

    def get_status(self):
        """获取 ASR 状态"""
        if self.available:
            return "Vosk 就绪"
        try:
            import vosk
            return "Vosk 已安装，模型未加载"
        except ImportError:
            return "未安装 (pip install vosk)"

    @property
    def is_listening(self):
        return self._is_listening
