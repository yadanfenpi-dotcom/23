from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .analyzer import ReportData, analyze_inquiries
from .charts import create_country_pie_chart
from .config import DEFAULT_INPUT_DIR, DEFAULT_OUTPUT_DIR, DEFAULT_TEMPLATE_PATH
from .emailer import load_email_config_from_env, send_report_email
from .excel_reader import find_latest_inquiry_file, read_inquiries
from .renderer import render_report


@dataclass(frozen=True)
class ReportResult:
    report_path: Path
    source_file: Path
    report_data: ReportData
    email_sent: bool


def generate_daily_report(
    input_dir: Path = DEFAULT_INPUT_DIR,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    template_path: Path = DEFAULT_TEMPLATE_PATH,
    send_email: bool = True,
) -> ReportResult:
    """生成询盘日报，并在 SMTP 配置完整时自动发送邮件。"""

    source_file = find_latest_inquiry_file(input_dir)
    inquiries = read_inquiries(source_file)
    report_data = analyze_inquiries(inquiries)

    date_text = report_data.report_date.strftime("%Y-%m-%d")
    assets_dir = output_dir / "assets"
    chart_path = create_country_pie_chart(
        report_data.country_counts,
        assets_dir / f"国家地区分布_{date_text}.png",
    )
    chart_relative_path = chart_path.relative_to(output_dir).as_posix() if chart_path else None

    report_path = output_dir / f"日报_{date_text}.html"
    render_report(
        report_data=report_data,
        template_path=template_path,
        output_path=report_path,
        source_file=source_file,
        chart_relative_path=chart_relative_path,
    )

    email_sent = False
    if send_email:
        config = load_email_config_from_env()
        if config is None:
            print("未检测到完整 SMTP 环境变量，已跳过邮件发送，仅保存本地日报。")
        else:
            send_report_email(config, report_path, subject=f"阿里国际站询盘日报 - {date_text}")
            email_sent = True
            print(f"邮件已发送至：{config.mail_to}")

    return ReportResult(
        report_path=report_path,
        source_file=source_file,
        report_data=report_data,
        email_sent=email_sent,
    )
