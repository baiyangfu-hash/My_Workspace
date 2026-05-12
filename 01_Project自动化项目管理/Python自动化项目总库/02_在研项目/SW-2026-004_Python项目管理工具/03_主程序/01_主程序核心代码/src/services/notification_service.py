# -*- coding: utf-8 -*-
"""
通知服务
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional

from src.dao.change_dao import ChangeDAO
from src.core.constants import ChangeStatus
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class NotificationService:
    """通知服务"""
    
    @staticmethod
    def notify_change_status(change_id: str, status: str):
        """通知变更状态变更"""
        try:
            # 1. 获取变更信息
            change = ChangeDAO.get_by_id(change_id)
            if not change:
                logger.error(f"变更单不存在: {change_id}")
                return
            
            # 2. 确定通知接收人
            recipients = NotificationService._get_recipients(change, status)
            if not recipients:
                logger.info(f"无通知接收人: {change_id}")
                return
            
            # 3. 生成通知内容
            subject, content = NotificationService._generate_notification_content(change, status)
            
            # 4. 发送通知
            for recipient in recipients:
                # 这里可以实现不同的通知方式
                # 暂时只实现邮件通知
                NotificationService.send_email_notification(recipient, subject, content)
            
            logger.info(f"变更状态通知已发送: {change_id}, status: {status}")
            
        except Exception as e:
            logger.exception(f"发送变更状态通知失败: {e}")
    
    @staticmethod
    def send_email_notification(recipient: str, subject: str, content: str):
        """发送邮件通知"""
        try:
            # 这里需要配置邮件服务器信息
            # 暂时只记录日志，不实际发送邮件
            logger.info(f"发送邮件通知: 收件人={recipient}, 主题={subject}")
            logger.info(f"邮件内容: {content}")
            
            # 实际发送邮件的代码（需要配置）
            # smtp_server = "smtp.example.com"
            # smtp_port = 587
            # smtp_user = "your_email@example.com"
            # smtp_password = "your_password"
            # 
            # msg = MIMEMultipart()
            # msg['From'] = smtp_user
            # msg['To'] = recipient
            # msg['Subject'] = subject
            # msg.attach(MIMEText(content, 'plain', 'utf-8'))
            # 
            # with smtplib.SMTP(smtp_server, smtp_port) as server:
            #     server.starttls()
            #     server.login(smtp_user, smtp_password)
            #     server.send_message(msg)
            
        except Exception as e:
            logger.exception(f"发送邮件失败: {e}")
    
    @staticmethod
    def _get_recipients(change, status: str) -> List[str]:
        """获取通知接收人"""
        recipients = []
        
        # 根据状态确定接收人
        if status == ChangeStatus.PENDING.value:
            # 待审批状态，通知审批人
            if change.approver:
                recipients.append(change.approver)
        elif status == ChangeStatus.APPROVED.value:
            # 已批准状态，通知实施人
            if change.implementer:
                recipients.append(change.implementer)
            # 同时通知提出人
            if change.proposer:
                recipients.append(change.proposer)
        elif status == ChangeStatus.REJECTED.value:
            # 已拒绝状态，通知提出人
            if change.proposer:
                recipients.append(change.proposer)
        elif status == ChangeStatus.COMPLETED.value:
            # 已完成状态，通知提出人和审批人
            if change.proposer:
                recipients.append(change.proposer)
            if change.approver:
                recipients.append(change.approver)
        
        return recipients
    
    @staticmethod
    def _generate_notification_content(change, status: str) -> tuple[str, str]:
        """生成通知内容"""
        status_map = {
            ChangeStatus.DRAFT.value: "草稿",
            ChangeStatus.PENDING.value: "待审批",
            ChangeStatus.APPROVED.value: "已批准",
            ChangeStatus.REJECTED.value: "已拒绝",
            ChangeStatus.IMPLEMENTING.value: "实施中",
            ChangeStatus.COMPLETED.value: "已完成",
            ChangeStatus.CANCELLED.value: "已取消"
        }
        
        subject = f"变更单状态更新: {change.title}"
        content = f"尊敬的用户：\n\n"
        content += f"变更单 {change.change_id} 的状态已更新为：{status_map.get(status, status)}\n\n"
        content += f"变更标题：{change.title}\n"
        content += f"变更类型：{change.type}\n"
        content += f"变更描述：{change.description}\n\n"
        content += "请及时查看并处理。\n\n"
        content += "此致\n项目管理系统"
        
        return subject, content
