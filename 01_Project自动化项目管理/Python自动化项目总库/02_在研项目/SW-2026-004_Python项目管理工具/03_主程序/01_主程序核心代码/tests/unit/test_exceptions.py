# -*- coding: utf-8 -*-
"""
自定义异常类单元测试
"""

import pytest

from src.core.exceptions import (
    AppException,
    AuthenticationError,
    AuthorizationError,
    TokenExpiredError,
    InvalidTokenError,
    ValidationError,
    BusinessValidationError,
    NotFoundError,
    ProjectNotFoundError,
    TemplateNotFoundError,
    DuplicateResourceError,
    DatabaseError,
    ConnectionError,
    TransactionError,
    FileOperationError,
    FileNotFoundError,
    PermissionDeniedError,
    ConfigError,
    MissingConfigError,
    ExternalServiceError,
    TimeoutError
)


class TestAppException:
    """基础异常测试"""
    
    def test_basic_exception(self):
        """测试基础异常"""
        exc = AppException("测试错误", code="TEST_ERROR", status_code=400)
        
        assert str(exc) == "测试错误"
        assert exc.message == "测试错误"
        assert exc.code == "TEST_ERROR"
        assert exc.status_code == 400
    
    def test_exception_to_dict(self):
        """测试异常转换为字典"""
        exc = AppException("测试错误", code="TEST_ERROR", status_code=400)
        result = exc.to_dict()
        
        assert result["message"] == "测试错误"
        assert result["code"] == "TEST_ERROR"
        assert result["status_code"] == 400


class TestAuthenticationExceptions:
    """认证相关异常测试"""
    
    def test_authentication_error(self):
        """测试认证错误"""
        exc = AuthenticationError("认证失败")
        
        assert exc.message == "认证失败"
        assert exc.code == "AUTHENTICATION_ERROR"
        assert exc.status_code == 401
    
    def test_authentication_error_default_message(self):
        """测试认证错误默认消息"""
        exc = AuthenticationError()
        
        assert exc.message == "认证失败"
    
    def test_authorization_error(self):
        """测试授权错误"""
        exc = AuthorizationError("权限不足")
        
        assert exc.message == "权限不足"
        assert exc.code == "AUTHORIZATION_ERROR"
        assert exc.status_code == 403
    
    def test_token_expired_error(self):
        """测试Token过期错误"""
        exc = TokenExpiredError()
        
        assert "过期" in exc.message
        assert exc.code == "TOKEN_EXPIRED"
        assert exc.status_code == 401
    
    def test_invalid_token_error(self):
        """测试无效Token错误"""
        exc = InvalidTokenError()
        
        assert "无效" in exc.message
        assert exc.code == "INVALID_TOKEN"
        assert exc.status_code == 401


class TestValidationExceptions:
    """验证相关异常测试"""
    
    def test_validation_error(self):
        """测试验证错误"""
        exc = ValidationError("参数错误", field="username")
        
        assert exc.message == "参数错误"
        assert exc.code == "VALIDATION_ERROR"
        assert exc.status_code == 400
        assert exc.field == "username"
    
    def test_validation_error_to_dict(self):
        """测试验证错误字典转换"""
        exc = ValidationError("参数错误", field="username")
        result = exc.to_dict()
        
        assert result["field"] == "username"
    
    def test_business_validation_error(self):
        """测试业务验证错误"""
        exc = BusinessValidationError("业务规则验证失败")
        
        assert exc.message == "业务规则验证失败"
        assert exc.code == "BUSINESS_VALIDATION_ERROR"


class TestResourceExceptions:
    """资源相关异常测试"""
    
    def test_not_found_error(self):
        """测试资源不存在错误"""
        exc = NotFoundError("项目不存在", resource_type="project")
        
        assert exc.message == "项目不存在"
        assert exc.code == "NOT_FOUND"
        assert exc.status_code == 404
        assert exc.resource_type == "project"
    
    def test_project_not_found_error(self):
        """测试项目不存在错误"""
        exc = ProjectNotFoundError("PRJ-001")
        
        assert "PRJ-001" in exc.message
        assert exc.code == "NOT_FOUND"
        assert exc.resource_type == "project"
    
    def test_project_not_found_error_no_id(self):
        """测试项目不存在错误（无ID）"""
        exc = ProjectNotFoundError()
        
        assert exc.message == "项目不存在"
    
    def test_template_not_found_error(self):
        """测试模板不存在错误"""
        exc = TemplateNotFoundError("TPL-001")
        
        assert "TPL-001" in exc.message
        assert exc.resource_type == "template"
    
    def test_duplicate_resource_error(self):
        """测试资源重复错误"""
        exc = DuplicateResourceError("项目已存在")
        
        assert exc.message == "项目已存在"
        assert exc.code == "DUPLICATE_RESOURCE"
        assert exc.status_code == 409


class TestDatabaseExceptions:
    """数据库相关异常测试"""
    
    def test_database_error(self):
        """测试数据库错误"""
        exc = DatabaseError("数据库连接失败")
        
        assert exc.message == "数据库连接失败"
        assert exc.code == "DATABASE_ERROR"
        assert exc.status_code == 500
    
    def test_connection_error(self):
        """测试连接错误"""
        exc = ConnectionError("无法连接到数据库")
        
        assert exc.message == "无法连接到数据库"
        assert exc.code == "CONNECTION_ERROR"
    
    def test_transaction_error(self):
        """测试事务错误"""
        exc = TransactionError("事务回滚")
        
        assert exc.message == "事务回滚"
        assert exc.code == "TRANSACTION_ERROR"


class TestFileExceptions:
    """文件操作异常测试"""
    
    def test_file_operation_error(self):
        """测试文件操作错误"""
        exc = FileOperationError("文件读取失败")
        
        assert exc.message == "文件读取失败"
        assert exc.code == "FILE_OPERATION_ERROR"
    
    def test_file_not_found_error(self):
        """测试文件不存在错误"""
        exc = FileNotFoundError("/path/to/file.txt")
        
        assert "/path/to/file.txt" in exc.message
        assert exc.code == "FILE_NOT_FOUND"
        assert exc.status_code == 404
    
    def test_file_not_found_error_no_path(self):
        """测试文件不存在错误（无路径）"""
        exc = FileNotFoundError()
        
        assert exc.message == "文件不存在"
    
    def test_permission_denied_error(self):
        """测试权限不足错误"""
        exc = PermissionDeniedError("没有写入权限")
        
        assert exc.message == "没有写入权限"
        assert exc.code == "PERMISSION_DENIED"
        assert exc.status_code == 403


class TestConfigExceptions:
    """配置相关异常测试"""
    
    def test_config_error(self):
        """测试配置错误"""
        exc = ConfigError("配置格式错误")
        
        assert exc.message == "配置格式错误"
        assert exc.code == "CONFIG_ERROR"
    
    def test_missing_config_error(self):
        """测试缺少配置错误"""
        exc = MissingConfigError("database.url")
        
        assert "database.url" in exc.message
        assert exc.code == "MISSING_CONFIG"


class TestExternalServiceExceptions:
    """外部服务异常测试"""
    
    def test_external_service_error(self):
        """测试外部服务错误"""
        exc = ExternalServiceError("服务调用失败", service_name="email_service")
        
        assert exc.message == "服务调用失败"
        assert exc.code == "EXTERNAL_SERVICE_ERROR"
        assert exc.status_code == 502
        assert exc.service_name == "email_service"
    
    def test_timeout_error(self):
        """测试超时错误"""
        exc = TimeoutError("请求超时")
        
        assert exc.message == "请求超时"
        assert exc.code == "TIMEOUT_ERROR"
        assert exc.status_code == 504


class TestExceptionInheritance:
    """异常继承关系测试"""
    
    def test_all_inherit_from_app_exception(self):
        """测试所有异常都继承自AppException"""
        exceptions = [
            AuthenticationError(),
            AuthorizationError(),
            TokenExpiredError(),
            InvalidTokenError(),
            ValidationError("test"),
            NotFoundError("test"),
            DatabaseError("test"),
            FileOperationError("test"),
            ConfigError("test"),
            ExternalServiceError("test")
        ]
        
        for exc in exceptions:
            assert isinstance(exc, AppException)
    
    def test_token_exceptions_inherit_authentication(self):
        """测试Token异常继承自AuthenticationError"""
        assert isinstance(TokenExpiredError(), AuthenticationError)
        assert isinstance(InvalidTokenError(), AuthenticationError)
    
    def test_connection_error_inherit_database(self):
        """测试连接错误继承自DatabaseError"""
        assert isinstance(ConnectionError(), DatabaseError)
    
    def test_transaction_error_inherit_database(self):
        """测试事务错误继承自DatabaseError"""
        assert isinstance(TransactionError(), DatabaseError)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
