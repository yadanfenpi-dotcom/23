from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .analyzer import ReportData


def render_report(
    report_data: ReportData,
    template_path: Path,
    output_path: Path,
    source_file: Path,
    chart_relative_path: str | None,
) -> Path:
    """把分析结果渲染成适合手机阅读的 HTML 日报。"""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    env = Environment(
        loader=FileSystemLoader(template_path.parent),
        autoescape=select_autoescape(("html", "xml")),
    )
    template = env.get_template(template_path.name)
    html = template.render(
        report=report_data,
        source_file=source_file.name,
        chart_path=chart_relative_path,
    )
    output_path.write_text(html, encoding="utf-8")
    return output_path
