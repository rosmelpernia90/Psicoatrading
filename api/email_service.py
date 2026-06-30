import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
import os
import logging
import re

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self):
        self.host = os.getenv("SMTP_HOST", "smtp.hostinger.com")
        self.port = int(os.getenv("SMTP_PORT", "465"))
        self.user = os.getenv("SMTP_USER")
        self.password = os.getenv("SMTP_PASSWORD")
        self.from_name = os.getenv("SMTP_FROM_NAME", "PsicoaTrading")
        self.from_email = os.getenv("SMTP_FROM_EMAIL", self.user)

    def send_email(self, to_email: str, subject: str, html_body: str, reply_to: str = None) -> bool:
        """Enviar un email HTML vía SMTP SSL."""
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = formataddr((self.from_name, self.from_email))
            msg["To"] = to_email
            if reply_to:
                msg["Reply-To"] = reply_to

            # Versión texto plano (fallback)
            text_body = re.sub(r'<[^>]+>', '', html_body)
            msg.attach(MIMEText(text_body, "plain", "utf-8"))
            msg.attach(MIMEText(html_body, "html", "utf-8"))

            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(self.host, self.port, context=context) as server:
                server.login(self.user, self.password)
                server.sendmail(self.from_email, to_email, msg.as_string())

            logger.info(f"Email enviado exitosamente a {to_email}: {subject}")
            return True

        except Exception as e:
            logger.error(f"Error enviando email a {to_email}: {str(e)}")
            return False


# Instancia global
email_service = EmailService()
