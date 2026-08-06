"""
TTS 引擎模块 - 文本转语音
使用系统内置 TTS 或简单的音频播放
"""
import os
import subprocess
import sys
import tempfile
import threading


class TTSEngine:
    """TTS 引擎"""

    def __init__(self):
        self.available = False
        self.engine = None
        self._check_availability()

    def _check_availability(self):
        """检查 TTS 可用性"""
        # Windows 系统使用 SAPI5
        if sys.platform == 'win32':
            try:
                import win32com.client
                self.engine = win32com.client.Dispatch("SAPI.SpVoice")
                self.available = True
                return
            except ImportError:
                pass

        # 尝试使用 pyttsx3
        try:
            import pyttsx3
            self.engine = pyttsx3.init()
            self.available = True
            return
        except ImportError:
            pass

        # 尝试使用 gTTS (需要网络)
        try:
            from gtts import gTTS
            self.engine = 'gtts'
            self.available = True
            return
        except ImportError:
            pass

        # 尝试使用 edge-tts (需要网络)
        try:
            import edge_tts
            self.engine = 'edge'
            self.available = True
            return
        except ImportError:
            pass

    def speak(self, text, callback=None):
        """
        朗读文本
        callback: 朗读完成后的回调函数
        """
        if not self.available or not text:
            if callback:
                callback()
            return

        def _do_speak():
            try:
                if sys.platform == 'win32' and hasattr(self.engine, 'Speak'):
                    # Windows SAPI
                    self.engine.Speak(text)
                elif hasattr(self.engine, 'say'):
                    # pyttsx3
                    self.engine.say(text)
                    self.engine.runAndWait()
                elif self.engine == 'gtts':
                    # gTTS
                    from gtts import gTTS
                    tts = gTTS(text=text, lang='en')
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                        tts.save(fp.name)
                        self._play_audio(fp.name)
                        os.unlink(fp.name)
                elif self.engine == 'edge':
                    # edge-tts
                    import asyncio

                    import edge_tts

                    async def _edge_speak():
                        communicate = edge_tts.Communicate(text, "en-US-AriaNeural")
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                            await communicate.save(fp.name)
                            self._play_audio(fp.name)
                            os.unlink(fp.name)

                    asyncio.run(_edge_speak())
            except Exception as e:
                print(f"TTS 朗读失败: {e}")
            finally:
                if callback:
                    callback()

        thread = threading.Thread(target=_do_speak)
        thread.daemon = True
        thread.start()

    def _play_audio(self, filepath):
        """播放音频文件"""
        if sys.platform == 'win32':
            os.startfile(filepath)
        elif sys.platform == 'darwin':
            subprocess.run(['afplay', filepath])
        else:
            subprocess.run(['mpg123', filepath], capture_output=True)

    def get_status(self):
        """获取 TTS 状态"""
        if not self.available:
            return "未安装"
        if sys.platform == 'win32' and hasattr(self.engine, 'Speak'):
            return "Windows SAPI"
        elif hasattr(self.engine, 'say'):
            return "pyttsx3"
        elif self.engine == 'gtts':
            return "gTTS (需网络)"
        elif self.engine == 'edge':
            return "Edge TTS (需网络)"
        return "未知"
