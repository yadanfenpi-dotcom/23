from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from inquiry_daily_report import generate_daily_report  # noqa: E402
from inquiry_daily_report.config import DEFAULT_INPUT_DIR, DEFAULT_OUTPUT_DIR, DEFAULT_TEMPLATE_PATH  # noqa: E402
from inquiry_daily_report.excel_reader import InquiryDataError  # noqa: E402


def main() -> int:
    """命令行入口：生成日报，并根据环境变量决定是否发送邮件。"""

    parser = argparse.ArgumentParser(description="生成阿里国际站询盘日报")
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT_DIR, help="询盘 Excel 所在目录")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="日报输出目录")
    parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE_PATH, help="HTML 模板路径")
    parser.add_argument("--no-email", action="store_true", help="只生成日报，不发送邮件")
    args = parser.parse_args()

    try:
        result = generate_daily_report(
            input_dir=args.input_dir,
            output_dir=args.output_dir,
            template_path=args.template,
            send_email=not args.no_email,
        )
    except InquiryDataError as exc:
        print(f"生成失败：{exc}", file=sys.stderr)
        return 1

    date_text = result.report_data.report_date.strftime("%Y-%m-%d")
    print(f"日报日期：{date_text}")
    print(f"来源文件：{result.source_file}")
    print(f"新增询盘：{result.report_data.inquiry_count} 条")
    print(f"日报文件：{result.report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
