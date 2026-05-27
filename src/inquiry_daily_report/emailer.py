from __future__ import annotations

import os
import smtplib
from dataclasses import dataclass
from email.message import EmailMessage
from pathlib import Path


@dataclass(frozen=True)
class EmailConfig:
    host: str
    port: int
    user: str
    password: str
    mail_from: str
    mail_to: str
    use_tls: bool = True


def load_email_config_from_env() -> EmailConfig | None:
    """从环境变量读取 SMTP 配置；不完整时返回 None。"""

    required_keys = ["SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASSWORD", "MAIL_FROM", "MAIL_TO"]
    values = {key: os.getenv(key, "").strip() for key in required_keys}
    if any(not value for value in values.values()):
        return None

    try:
        port = int(values["SMTP_PORT"])
    except ValueError as exc:
        raise ValueError("SMTP_PORT 必须是数字，例如 465 或 587。") from exc

    return EmailConfig(
        host=values["SMTP_HOST"],
        port=port,
        user=values["SMTP_USER"],
        password=values["SMTP_PASSWORD"],
        mail_from=values["MAIL_FROM"],
        mail_to=values["MAIL_TO"],
        use_tls=os.getenv("SMTP_USE_TLS", "true").strip().lower() not in {"0", "false", "no"},
    )


def send_report_email(config: EmailConfig, report_path: Path, subject: str) -> None:
    """发送 HTML 日报邮件，并把日报文件作为附件一并发送。"""

    html = report_path.read_text(encoding="utf-8")
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = config.mail_from
    message["To"] = config.mail_to
    message.set_content("您的询盘日报已生成，请使用支持 HTML 的邮件客户端查看。")
    message.add_alternative(html, subtype="html")
    message.add_attachment(
        html.encode("utf-8"),
        maintype="text",
        subtype="html",
        filename=report_path.name,
    )

    if config.use_tls:
        with smtplib.SMTP(config.host, config.port, timeout=30) as server:
            server.starttls()
            server.login(config.user, config.password)
            server.send_message(message)
    else:
        with smtplib.SMTP_SSL(config.host, config.port, timeout=30) as server:
            server.login(config.user, config.password)
            server.send_message(message)
