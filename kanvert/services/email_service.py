"""
Email service for sending various types of emails.
"""

import asyncio
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import aiosmtplib
from jinja2 import Environment, FileSystemLoader
import logging
from ..config.settings import get_settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails."""
    
    def __init__(self):
        self.settings = get_settings()
        self.jinja_env = Environment(
            loader=FileSystemLoader("kanvert/templates/email")
        )
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """Send an email."""
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.settings.EMAIL_FROM
            message["To"] = to_email
            
            # Add text version if provided
            if text_content:
                text_part = MIMEText(text_content, "plain")
                message.attach(text_part)
            
            # Add HTML version
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)
            
            # Send email
            if self.settings.EMAIL_BACKEND == "smtp":
                await self._send_via_smtp(message)
            else:
                # For development/testing
                logger.info(f"Would send email to {to_email}: {subject}")
                logger.info(f"Content: {html_content}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False
    
    async def _send_via_smtp(self, message: MIMEMultipart):
        """Send email via SMTP."""
        await aiosmtplib.send(
            message,
            hostname=self.settings.SMTP_HOST,
            port=self.settings.SMTP_PORT,
            start_tls=self.settings.SMTP_TLS,
            username=self.settings.SMTP_USER,
            password=self.settings.SMTP_PASSWORD,
        )
    
    async def send_welcome_email(self, email: str, first_name: str) -> bool:
        """Send welcome email to new user."""
        try:
            template = self.jinja_env.get_template("welcome.html")
            html_content = template.render(
                first_name=first_name,
                login_url=f"{self.settings.FRONTEND_URL}/login",
                dashboard_url=f"{self.settings.FRONTEND_URL}/dashboard",
                docs_url=f"{self.settings.FRONTEND_URL}/docs"
            )
            
            subject = "Welcome to Kanvert - Start Converting Documents!"
            
            return await self.send_email(email, subject, html_content)
            
        except Exception as e:
            logger.error(f"Failed to send welcome email to {email}: {e}")
            return False
    
    async def send_password_reset_email(self, email: str, reset_token: str) -> bool:
        """Send password reset email."""
        try:
            template = self.jinja_env.get_template("password_reset.html")
            reset_url = f"{self.settings.FRONTEND_URL}/reset-password?token={reset_token}&email={email}"
            
            html_content = template.render(
                reset_url=reset_url,
                reset_token=reset_token,
                expiry_hours=1
            )
            
            subject = "Reset Your Kanvert Password"
            
            return await self.send_email(email, subject, html_content)
            
        except Exception as e:
            logger.error(f"Failed to send password reset email to {email}: {e}")
            return False
    
    async def send_conversion_complete_email(
        self, 
        email: str, 
        conversion_id: str, 
        filename: str,
        download_url: str
    ) -> bool:
        """Send conversion completion notification email."""
        try:
            template = self.jinja_env.get_template("conversion_complete.html")
            html_content = template.render(
                filename=filename,
                download_url=download_url,
                conversion_id=conversion_id,
                dashboard_url=f"{self.settings.FRONTEND_URL}/dashboard"
            )
            
            subject = f"Your conversion is ready: {filename}"
            
            return await self.send_email(email, subject, html_content)
            
        except Exception as e:
            logger.error(f"Failed to send conversion complete email to {email}: {e}")
            return False
    
    async def send_conversion_failed_email(
        self, 
        email: str, 
        conversion_id: str, 
        filename: str,
        error_message: str
    ) -> bool:
        """Send conversion failure notification email."""
        try:
            template = self.jinja_env.get_template("conversion_failed.html")
            html_content = template.render(
                filename=filename,
                error_message=error_message,
                conversion_id=conversion_id,
                support_url=f"{self.settings.FRONTEND_URL}/support",
                dashboard_url=f"{self.settings.FRONTEND_URL}/dashboard"
            )
            
            subject = f"Conversion failed: {filename}"
            
            return await self.send_email(email, subject, html_content)
            
        except Exception as e:
            logger.error(f"Failed to send conversion failed email to {email}: {e}")
            return False
    
    async def send_weekly_report_email(
        self, 
        email: str, 
        user_name: str,
        stats: dict
    ) -> bool:
        """Send weekly usage report email."""
        try:
            template = self.jinja_env.get_template("weekly_report.html")
            html_content = template.render(
                user_name=user_name,
                stats=stats,
                dashboard_url=f"{self.settings.FRONTEND_URL}/dashboard",
                analytics_url=f"{self.settings.FRONTEND_URL}/analytics"
            )
            
            subject = "Your Weekly Kanvert Usage Report"
            
            return await self.send_email(email, subject, html_content)
            
        except Exception as e:
            logger.error(f"Failed to send weekly report email to {email}: {e}")
            return False
    
    async def send_api_key_created_email(
        self, 
        email: str, 
        key_name: str,
        api_key: str
    ) -> bool:
        """Send API key creation notification email."""
        try:
            template = self.jinja_env.get_template("api_key_created.html")
            html_content = template.render(
                key_name=key_name,
                api_key=api_key,
                docs_url=f"{self.settings.FRONTEND_URL}/docs",
                settings_url=f"{self.settings.FRONTEND_URL}/settings"
            )
            
            subject = f"New API Key Created: {key_name}"
            
            return await self.send_email(email, subject, html_content)
            
        except Exception as e:
            logger.error(f"Failed to send API key created email to {email}: {e}")
            return False