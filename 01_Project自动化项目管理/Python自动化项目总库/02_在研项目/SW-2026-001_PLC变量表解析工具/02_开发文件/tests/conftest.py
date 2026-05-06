import pytest
import tkinter as tk
from unittest import mock

@pytest.fixture
def root():
    """创建Tkinter根窗口"""
    root = tk.Tk()
    root.withdraw()  # 隐藏窗口，避免测试时显示
    yield root
    root.destroy()

@pytest.fixture
def mock_filedialog():
    """模拟文件对话框"""
    with mock.patch('tkinter.filedialog.askopenfilename') as mock_open:
        with mock.patch('tkinter.filedialog.asksaveasfilename') as mock_save:
            yield {
                'askopenfilename': mock_open,
                'asksaveasfilename': mock_save
            }

@pytest.fixture
def mock_messagebox():
    """模拟消息框"""
    with mock.patch('tkinter.messagebox.showinfo') as mock_showinfo:
        with mock.patch('tkinter.messagebox.showwarning') as mock_showwarning:
            with mock.patch('tkinter.messagebox.showerror') as mock_showerror:
                with mock.patch('tkinter.messagebox.askyesno') as mock_askyesno:
                    yield {
                        'showinfo': mock_showinfo,
                        'showwarning': mock_showwarning,
                        'showerror': mock_showerror,
                        'askyesno': mock_askyesno
                    }

@pytest.fixture
def test_variables():
    """测试用的变量数据"""
    return [
        {
            'name': 'VAR1',
            'type': 'BOOL',
            'scope': 'GLOBAL',
            'description': '测试变量1'
        },
        {
            'name': 'VAR2',
            'type': 'INT',
            'scope': 'LOCAL',
            'description': '测试变量2'
        }
    ]

@pytest.fixture
def test_csv_content():
    """测试用的CSV文件内容"""
    return "类别,名称,数据类型,注释\nGLOBAL,VAR1,BOOL,测试变量1\nLOCAL,VAR2,INT,测试变量2"
