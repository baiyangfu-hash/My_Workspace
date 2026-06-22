"""file_utils 工具函数测试"""

from __future__ import annotations

from auto_pm.utils.file_utils import get_mtime, read_file, write_file


class TestReadFile:
    """read_file 测试"""

    def test_read_existing_file(self, tmp_path: object) -> None:
        """读取存在的文件"""
        tmp = tmp_path  # type: Path
        f = tmp / "test.txt"
        f.write_text("hello", encoding="utf-8")
        assert read_file(str(f)) == "hello"

    def test_read_nonexistent_file(self, tmp_path: object) -> None:
        """读取不存在的文件返回空字符串"""
        tmp = tmp_path  # type: Path
        assert read_file(str(tmp / "nonexistent.txt")) == ""

    def test_read_file_with_encoding_error(self, tmp_path: object) -> None:
        """读取编码错误的文件返回空字符串"""
        tmp = tmp_path  # type: Path
        f = tmp / "binary.bin"
        f.write_bytes(b"\xff\xfe\x80\x81")
        result = read_file(str(f))
        # UnicodeDecodeError 被捕获，返回空字符串
        assert result == ""


class TestWriteFile:
    """write_file 测试"""

    def test_write_creates_parent_dirs(self, tmp_path: object) -> None:
        """写入文件时自动创建父目录"""
        tmp = tmp_path  # type: Path
        f = tmp / "sub" / "dir" / "test.txt"
        write_file(str(f), "hello")
        assert f.read_text(encoding="utf-8") == "hello"

    def test_write_overwrites_existing(self, tmp_path: object) -> None:
        """写入覆盖已有文件"""
        tmp = tmp_path  # type: Path
        f = tmp / "test.txt"
        f.write_text("old", encoding="utf-8")
        write_file(str(f), "new")
        assert f.read_text(encoding="utf-8") == "new"


class TestGetMtime:
    """get_mtime 测试"""

    def test_get_mtime_existing_file(self, tmp_path: object) -> None:
        """获取存在文件的修改时间"""
        tmp = tmp_path  # type: Path
        f = tmp / "test.txt"
        f.write_text("hello", encoding="utf-8")
        assert get_mtime(str(f)) > 0

    def test_get_mtime_nonexistent_file(self, tmp_path: object) -> None:
        """获取不存在文件的修改时间返回 0"""
        tmp = tmp_path  # type: Path
        assert get_mtime(str(tmp / "nonexistent.txt")) == 0.0
