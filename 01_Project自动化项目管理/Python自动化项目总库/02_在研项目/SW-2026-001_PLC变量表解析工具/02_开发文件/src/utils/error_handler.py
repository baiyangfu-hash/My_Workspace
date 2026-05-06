#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
异常处理工具类

提供用户友好的错误提示和错误恢复机制
"""

import traceback
from typing import Optional, Callable, Any
from enum import Enum


class ErrorLevel(Enum):
    """
    错误级别枚举
    """
    INFO = "信息"
    WARNING = "警告"
    ERROR = "错误"
    CRITICAL = "严重错误"


class ErrorCode(Enum):
    """
    错误代码枚举
    """
    FILE_NOT_FOUND = "E001"
    FILE_READ_ERROR = "E002"
    FILE_WRITE_ERROR = "E003"
    ENCODING_ERROR = "E004"
    PARSE_ERROR = "E005"
    EXPORT_ERROR = "E006"
    INVALID_FORMAT = "E007"
    INVALID_ENCODING = "E008"
    UNKNOWN_ERROR = "E999"


class ErrorHandler:
    """
    异常处理工具类
    
    提供用户友好的错误提示和错误恢复机制
    """
    
    def __init__(self):
        """
        初始化异常处理器
        """
        self.error_messages = {
            ErrorCode.FILE_NOT_FOUND: {
                'level': ErrorLevel.ERROR,
                'message': '文件不存在',
                'suggestion': '请检查文件路径是否正确，或选择其他文件',
                'recoverable': False
            },
            ErrorCode.FILE_READ_ERROR: {
                'level': ErrorLevel.ERROR,
                'message': '文件读取失败',
                'suggestion': '请检查文件是否被其他程序占用，或文件权限是否正确',
                'recoverable': True
            },
            ErrorCode.FILE_WRITE_ERROR: {
                'level': ErrorLevel.ERROR,
                'message': '文件写入失败',
                'suggestion': '请检查磁盘空间是否充足，或文件是否被其他程序占用',
                'recoverable': True
            },
            ErrorCode.ENCODING_ERROR: {
                'level': ErrorLevel.ERROR,
                'message': '编码检测失败',
                'suggestion': '请尝试手动选择文件编码，或使用其他编码格式',
                'recoverable': True
            },
            ErrorCode.PARSE_ERROR: {
                'level': ErrorLevel.ERROR,
                'message': '文件解析失败',
                'suggestion': '请检查文件格式是否正确，或选择正确的PLC格式',
                'recoverable': True
            },
            ErrorCode.EXPORT_ERROR: {
                'level': ErrorLevel.ERROR,
                'message': '文件导出失败',
                'suggestion': '请检查输出路径是否有效，或磁盘空间是否充足',
                'recoverable': True
            },
            ErrorCode.INVALID_FORMAT: {
                'level': ErrorLevel.WARNING,
                'message': '文件格式无效',
                'suggestion': '请选择正确的PLC软件格式',
                'recoverable': True
            },
            ErrorCode.INVALID_ENCODING: {
                'level': ErrorLevel.ERROR,
                'message': '不支持的编码',
                'suggestion': '请从支持的编码列表中选择',
                'recoverable': True
            },
            ErrorCode.UNKNOWN_ERROR: {
                'level': ErrorLevel.ERROR,
                'message': '未知错误',
                'suggestion': '请重试操作，如问题持续存在请联系技术支持',
                'recoverable': False
            }
        }
    
    def handle_exception(self, exception: Exception, context: str = "") -> dict:
        """
        处理异常，返回用户友好的错误信息
        
        Args:
            exception (Exception): 异常对象
            context (str): 错误发生的上下文信息
            
        Returns:
            dict: 包含错误信息的字典
        """
        error_code = self._identify_error_code(exception)
        error_info = self.error_messages.get(error_code, self.error_messages[ErrorCode.UNKNOWN_ERROR])
        
        return {
            'code': error_code.value,
            'level': error_info['level'].value,
            'message': error_info['message'],
            'suggestion': error_info['suggestion'],
            'recoverable': error_info['recoverable'],
            'context': context,
            'detail': str(exception),
            'traceback': traceback.format_exc()
        }
    
    def _identify_error_code(self, exception: Exception) -> ErrorCode:
        """
        识别异常对应的错误代码
        
        Args:
            exception (Exception): 异常对象
            
        Returns:
            ErrorCode: 错误代码
        """
        error_type = type(exception).__name__
        
        if isinstance(exception, FileNotFoundError):
            return ErrorCode.FILE_NOT_FOUND
        elif isinstance(exception, PermissionError):
            return ErrorCode.FILE_READ_ERROR
        elif isinstance(exception, UnicodeDecodeError):
            return ErrorCode.ENCODING_ERROR
        elif isinstance(exception, UnicodeEncodeError):
            return ErrorCode.ENCODING_ERROR
        elif 'parse' in str(exception).lower():
            return ErrorCode.PARSE_ERROR
        elif 'export' in str(exception).lower():
            return ErrorCode.EXPORT_ERROR
        elif 'format' in str(exception).lower():
            return ErrorCode.INVALID_FORMAT
        elif 'encoding' in str(exception).lower():
            return ErrorCode.INVALID_ENCODING
        else:
            return ErrorCode.UNKNOWN_ERROR
    
    def format_error_message(self, error_info: dict) -> str:
        """
        格式化错误信息为用户友好的消息
        
        Args:
            error_info (dict): 错误信息字典
            
        Returns:
            str: 格式化后的错误消息
        """
        lines = [
            f"【{error_info['level']}】{error_info['code']}: {error_info['message']}",
            f"详细描述: {error_info['detail']}",
            f"建议操作: {error_info['suggestion']}"
        ]
        
        if error_info['context']:
            lines.insert(1, f"操作上下文: {error_info['context']}")
        
        if error_info['recoverable']:
            lines.append("此错误可以恢复，请根据建议操作后重试")
        else:
            lines.append("此错误无法恢复，请联系技术支持")
        
        return '\n'.join(lines)
    
    def handle_with_recovery(self, func: Callable, recovery_func: Optional[Callable] = None, context: str = "") -> Any:
        """
        执行函数并处理异常，提供错误恢复机制
        
        Args:
            func (Callable): 要执行的函数
            recovery_func (Optional[Callable]): 恢复函数，当错误可恢复时调用
            context (str): 错误发生的上下文信息
            
        Returns:
            Any: 函数执行结果，或None（如果发生错误且无法恢复）
        """
        try:
            return func()
        except Exception as e:
            error_info = self.handle_exception(e, context)
            
            if error_info['recoverable'] and recovery_func:
                try:
                    return recovery_func(error_info)
                except Exception as recovery_error:
                    error_info['recovery_error'] = str(recovery_error)
                    print(self.format_error_message(error_info))
                    return None
            else:
                print(self.format_error_message(error_info))
                return None
    
    def log_error(self, error_info: dict, log_file: str = "error.log"):
        """
        记录错误到日志文件
        
        Args:
            error_info (dict): 错误信息字典
            log_file (str): 日志文件路径
        """
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"\n{'='*60}\n")
                f.write(f"时间: {self._get_current_time()}\n")
                f.write(f"错误代码: {error_info['code']}\n")
                f.write(f"错误级别: {error_info['level']}\n")
                f.write(f"错误消息: {error_info['message']}\n")
                f.write(f"上下文: {error_info['context']}\n")
                f.write(f"详细信息: {error_info['detail']}\n")
                f.write(f"堆栈跟踪:\n{error_info['traceback']}\n")
                f.write(f"{'='*60}\n")
        except Exception as e:
            print(f"无法写入错误日志: {str(e)}")
    
    @staticmethod
    def _get_current_time() -> str:
        """
        获取当前时间字符串
        
        Returns:
            str: 当前时间字符串
        """
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
